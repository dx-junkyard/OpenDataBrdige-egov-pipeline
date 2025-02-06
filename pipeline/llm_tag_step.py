import os
import json
import yaml
from openai import OpenAI
import logging

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



class LlmTagStep:
    def __init__(self, step_config):
        self.progress_data = None
        self.url_to_filepath = None
        # URLに対応するHTML（スクレイピングで取得したもの）
        self.progress_file_path = step_config['progress_file']
        # 入力：「概要」再作成対象のサービスカタログjson
        self.input_json_path = step_config['input_json_file']
        # 出力：「概要」再作成したサービスカタログの出力先
        self.output_json_path = step_config['output_json_file']

        # LLMの設定
        self.llm_url = step_config['llm_url']
        self.llm_api_key = step_config['llm_api_key']
        self.llm_model = step_config['llm_model']
        llm_prompt_file = step_config['llm_prompt_file']
        llm_prompt = self.load_llm_prompt(llm_prompt_file)
        self.ollama_client = OllamaClient(self.llm_url, self.llm_api_key, self.llm_model, llm_prompt)

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
        """Load the JSON data file."""
        if not os.path.exists(self.input_json_path):
            raise FileNotFoundError(f"{self.input_json_path} does not exist.")
        with open(self.input_json_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_law_content(self):
        """Create the 'tags' field with a summary from OllamaStep.create_tags()."""
        data = self.load_data()
        total_entries = len(data)

        for index, entry in enumerate(data):
            law = entry.get("Law", {})
            if law:
                law_content = json.dumps(law, ensure_ascii=False)
                if law_content:
                    # Create the 'tags' field
                    entry["tags"] = self.ollama_client.create_tags(law_content)
            # 進捗の割合を計算して画面に表示する
            progress = (index + 1) / total_entries * 100
            logging.info(f"Progress: {progress:.2f}% ({index + 1}/{total_entries})")
        return data
    def execute(self):
        #data = self.get_url_content()
        data = self.get_law_content()
        
        # 変更点：概要フィールドの形式を修正し、itemsとしてリストで保持
        for entry in data:
            if "概要" in entry:
                entry["概要"] = {"items": entry["概要"]}

        with open(self.output_json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


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

