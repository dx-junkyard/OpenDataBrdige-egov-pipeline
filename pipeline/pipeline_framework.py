import sys
from step_factory import StepFactory
import yaml


# ステップクラスのインポート
from web_scraper_step import WebScraperStep
from html2htaglayer_step import Html2HtagLayerStep
from ollama_step import OllamaStep
from llm_tag_step import LlmTagStep
from tfidf_tag_step import TfidfTagStep
from embedding_step import EmbeddingStep
from xml_law2json_step import XmlLawToJsonStep

# ステップをファクトリーに登録
StepFactory.register_step('web_scraper_step', WebScraperStep)
StepFactory.register_step('html2htaglayer_step', Html2HtagLayerStep)
StepFactory.register_step('ollama_step', OllamaStep)
StepFactory.register_step('llm_tag_step', LlmTagStep)
StepFactory.register_step('tfidf_tag_step', TfidfTagStep)
StepFactory.register_step('embedding_step', EmbeddingStep)
StepFactory.register_step('xml_law2json_step', XmlLawToJsonStep)

def execute_pipeline(pipeline_config_path):
    with open(pipeline_config_path, 'r') as file:
        pipeline_config = yaml.safe_load(file)

    for step_config in pipeline_config.get('steps', []):
        # skip_flgがtrueとして評価されるかどうかをチェック
        if step_config.get('skip_flg', False) == True:
            print(f"Skipping step: {step_config['name']}")
            continue

        step = StepFactory.create_step(step_config['type'], step_config)
        step.execute()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        execute_pipeline(sys.argv[1])

