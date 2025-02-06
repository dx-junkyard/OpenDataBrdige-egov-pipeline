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
            'xml_input_dir': 'path/to/your/xml_directory',
            'json_output_dir': 'path/to/your/json_directory'
        }
        """
        self.xml_input_dir = step_config.get('xml_input_dir', '')
        self.json_output_dir = step_config.get('json_output_dir', '')

    def execute(self):
        """
        self.xml_input_dir に含まれるすべてのXMLファイルを、
        そのまま辞書にパース→JSON化し、self.json_output_dir に書き出す。
        """
        logging.info(f"XML入力ディレクトリ: {self.xml_input_dir}")
        logging.info(f"JSON出力ディレクトリ: {self.json_output_dir}")

        # 出力ディレクトリが存在しない場合は作成
        if not os.path.exists(self.json_output_dir):
            os.makedirs(self.json_output_dir)

        # ディレクトリ内のファイル一覧を取得
        for filename in os.listdir(self.xml_input_dir):
            # 拡張子が .xml のファイルに限定する（大文字小文字問わず）
            if filename.lower().endswith('.xml'):
                xml_path = os.path.join(self.xml_input_dir, filename)
                logging.info(f"処理対象XML: {xml_path}")

                # XMLファイルを辞書として読み込み
                with open(xml_path, 'r', encoding='utf-8') as f:
                    data_dict = xmltodict.parse(f.read())

                # JSON文字列に変換
                json_data = json.dumps(data_dict, ensure_ascii=False, indent=2)

                # 出力先のJSONファイル名を決定（拡張子を .json に）
                base_name, _ = os.path.splitext(filename)
                json_filename = base_name + ".json"
                json_path = os.path.join(self.json_output_dir, json_filename)

                # ファイルへ出力
                with open(json_path, 'w', encoding='utf-8') as f:
                    f.write(json_data)

                logging.info(f"→ JSON出力完了: {json_path}")

        logging.info("XML→JSON変換が完了しました。")

