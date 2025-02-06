import os
import json
import xmltodict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class XmlLawToJsonStep:
    def __init__(self, step_config):
        """
        step_config から必要なパラメータを取得し、インスタンス変数に格納する。
        例）
        step_config = {
            'xml_input_file': '108DF0000000054_20030501_414CO0000000277.xml',
            'json_output_file': 'output.json'
        }
        """
        self.xml_input_file = step_config.get('xml_input_file', '')
        self.json_output_file = step_config.get('json_output_file', '')

    def execute(self):
        """
        XMLをそのまま辞書にパースし、JSON化して self.json_output_file に書き出す。
        """
        logging.info(f"XML入力ファイル: {self.xml_input_file}")
        logging.info(f"JSON出力ファイル: {self.json_output_file}")

        # XMLを辞書として読み込み
        with open(self.xml_input_file, 'r', encoding='utf-8') as f:
            data_dict = xmltodict.parse(f.read())

        # JSONに変換
        json_data = json.dumps(data_dict, ensure_ascii=False, indent=2)

        # ファイルへ出力
        with open(self.json_output_file, 'w', encoding='utf-8') as f:
            f.write(json_data)

        logging.info("XML→JSON変換が完了しました。")

