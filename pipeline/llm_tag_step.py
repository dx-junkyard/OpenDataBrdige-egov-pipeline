import os
import json
import logging
from collections import Counter
from openai import OpenAI

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LlmTagStep:
    def __init__(self, step_config):
        self.input_json_path = step_config['input_json_file']
        self.output_json_path = step_config['output_json_file']
        self.llm_url = step_config['llm_url']
        self.llm_api_key = step_config['llm_api_key']
        self.llm_model = step_config['llm_model']
        llm_prompt_file = step_config['llm_prompt_file']
        llm_prompt = self.load_llm_prompt(llm_prompt_file)
        self.ollama_client = OllamaClient(self.llm_url, self.llm_api_key, self.llm_model, llm_prompt)
        self.tag_count = Counter()

    def load_llm_prompt(self, llm_prompt_file):
        try:
            with open(llm_prompt_file, 'r', encoding='utf-8') as file:
                llm_prompt = file.read()
                return llm_prompt
        except FileNotFoundError:
            print(f"指定されたファイル '{self.llm_prompt_file}' が見つかりません。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
        return ""

    def load_data(self):
        if not os.path.exists(self.input_json_path):
            raise FileNotFoundError(f"{self.input_json_path} does not exist.")
        with open(self.input_json_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def save_data(self, data):
        with open(self.output_json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        logging.info("出力ファイルを上書きしました。")

    def first_tagging(self, data):
        """ 1回目のタグ付け: 各Lawにタグを付与し、タグの参照回数を記録 """
        for entry in data:
            law_content = json.dumps(entry.get("Law", {}), ensure_ascii=False)
            if law_content:
                entry["tags"] = self.ollama_client.create_tags(law_content)
                self.tag_count.update(entry["tags"])
        logging.info(f"1回目のタグ付け完了。使用されたタグ数: {len(self.tag_count)}")
        return data

    def refine_tags(self, data):
        """ タグの統一処理を繰り返し、15個以下になるか10回実行する """
        iterations = 0
        while len(self.tag_count) > 15 and iterations < 10:
            tag_mapping = {tag: max(self.tag_count, key=self.tag_count.get) for tag in self.tag_count}
            for entry in data:
                entry["tags"] = [tag_mapping.get(tag, tag) for tag in entry["tags"]]
            self.tag_count = Counter(tag for entry in data for tag in entry["tags"])
            iterations += 1
            logging.info(f"{iterations}回目のタグ統一処理完了。使用されているタグ数: {len(self.tag_count)}")
        return data

    def execute(self):
        data = self.load_data()
        data = self.first_tagging(data)
        data = self.refine_tags(data)
        self.save_data(data)


class OllamaClient:
    def __init__(self, llm_url, llm_api_key, llm_model, llm_prompt):
        self.llm_url = llm_url
        self.llm_api_key = llm_api_key
        self.llm_model = llm_model
        self.llm_prompt = llm_prompt
        logging.info(f"LLM prompt : {llm_prompt}")
        # OpenAIクライアントのセットアップ
        self.client = OpenAI(
            base_url=self.llm_url,
            api_key=self.llm_api_key,
        )

    def exp_tags(self, response):
        lines = response.splitlines()
        tags = [line for line in lines if "tags" in line][0]
        return "{" + tags + "}"
    def create_tags(self, content):
        try:
            prompt = f"{self.llm_prompt}\n{content}\nJSON:"
            chat_completion = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'temperature': 0.5
                    }
                ]
            )
            response = chat_completion.choices[0].message.content
            logging.info(f"Raw LLM response: {response}")
            response = self.exp_tags(response)
            tags = json.loads(response).get("tags", [])
            logging.info("LLMの応答を受信しました")
            return tags
        except (json.JSONDecodeError, KeyError):
            logging.error(f"Invalid response format: {response}")
            return []
        except Exception as e:
            logging.error(f"LLMの呼び出しに失敗しました: {str(e)}")
            return []

