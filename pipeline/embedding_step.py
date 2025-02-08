import os
import json
import torch        
from transformers import BertTokenizer, BertModel 
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import logging  # ログ出力のために追加

# ロギングの設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')




class EmbeddingStep:
    def __init__(self, step_config):
        self.law_catalog_file = step_config['law_catalog_json']
        self.embeddings_file = step_config['embeddings_file']
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')

    # law catalog jsonの読み込み
    def load_json_data(self, file_path):
        """JSONファイルを読み込む"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    # law catalog
    def save_embeddings_to_file(self, embeddings, entries, output_file):
        """ベクトルデータをJSONファイルに保存する"""
        data = {
            'embeddings': embeddings.tolist(),
            'entries': entries
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    # vector化した概要と対応するサービス情報をファイルに保存
    def save_embeddings_to_file(self, embeddings, entries, output_file):
        """ベクトルデータをJSONファイルに保存する"""
        data = {
            'embeddings': embeddings.tolist(),
            'entries': entries
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)


    # 渡されたtextをベクトル化
    def get_embedding(self, text):
        """テキストをベクトル化する"""
        if isinstance(text, list):  # リストなら結合して1つの文字列にする
            text = " ".join(text)
        inputs = self.tokenizer(text, return_tensors='pt', max_length=512, truncation=True)
        outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
        return embedding.detach().numpy()

    def extract_text(self, law):
        """Lawオブジェクトから特定のフィールドのテキストを抽出"""
        texts = []
        fields = ['@Abbrev', '#text', 'EnactStatement', 'ChapterTitle', 'ArticleCaption', 'ArticleTitle', 'Sentence']

        for key, value in law.items():
            if key in fields and isinstance(value, str):
                texts.append(value)
            elif isinstance(value, dict):
                texts.extend(self.extract_text(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        texts.extend(self.extract_text(item))
        return texts

    # law catalog中の全概要をvector化
    def get_overview_embeddings(self, law_catalog):
        """全ての概要をベクトル化する"""
        overview_embeddings = []
        entries = []

        for law in law_catalog:
            #logging.info(f"Service data: {law}")

            law = law.get("Law")
            overview = self.extract_text(law)

            if overview:
                embedding = self.get_embedding(overview)
                overview_embeddings.append(embedding)

                law_num = law.get("LawNum")
                law_title = law.get("LawBody").get("LawTitle").get("@Abbrev")
                law_text = law.get("LawBody").get("LawTitle").get("#text")
    
                entry = {
                    'law_num': law_num,
                    'law_title': law_title,
                    'law_text': law_text
                }
                entries.append(entry)

        return np.vstack(overview_embeddings), entries

    def execute(self):
        self.law_catalog = self.load_json_data(self.law_catalog_file)
        self.overview_embeddings, self.entries = self.get_overview_embeddings(self.law_catalog)
        if self.embeddings_file:
            self.save_embeddings_to_file(self.overview_embeddings, self.entries, self.embeddings_file)


