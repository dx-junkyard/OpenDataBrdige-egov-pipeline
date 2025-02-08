import json
import MeCab
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

class TfidfTagStep:
    def __init__(self, step_config):
        self.input_json_path = step_config['input_json_file']
        self.output_json_path = step_config['output_json_file']
        self.exclude_words = set(step_config.get('exclude_words', "").split(',')) if isinstance(step_config.get('exclude_words'), str) else set(step_config.get('exclude_words', []))
        self.exclude_words = {word.strip() for word in self.exclude_words}  # 空白を削除
        self.mecab = MeCab.Tagger("-Owakati")

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

    def tokenize_and_clean(self, text):
        """形態素解析を用いてテキストをトークナイズ"""
        words = self.mecab.parse(text).strip().split()
        return " ".join(words)

    def execute(self):
        """TF-IDFを使用してLawごとに最大5つの特徴的なタグを抽出し、結果をJSONに保存"""
        with open(self.input_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for law in data:
            all_texts = self.extract_text(law)
            all_texts = [text.strip() for text in all_texts if text.strip()]
            
            processed_texts = [self.tokenize_and_clean(text) for text in all_texts]
            
            if not processed_texts:
                law["tags"] = []
                continue
            
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            
            try:
                feature_names = vectorizer.get_feature_names_out()
            except AttributeError:
                feature_names = vectorizer.get_feature_names()
            
            word_scores = Counter()
            for doc in tfidf_matrix:
                indices = doc.indices
                scores = doc.data
                for idx, score in zip(indices, scores):
                    word_scores[feature_names[idx]] += score
            
            # 除外リストに含まれる単語をフィルタリング
            filtered_tags = [word for word, score in word_scores.most_common(10) if word not in self.exclude_words][:5]
            
            law["tags"] = filtered_tags
        
        with open(self.output_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"タグの抽出が完了しました: {self.output_json_path}")

