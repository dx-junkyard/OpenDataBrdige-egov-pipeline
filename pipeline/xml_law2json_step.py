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
            'xml_input_dir': 'path/to/xml_directory',
            'json_output_file': 'merged_output.json'
        }
        """
        self.xml_input_dir = step_config.get('xml_input_dir', '')
        self.json_output_file = step_config.get('json_output_file', '')

    def execute(self):
        """
        1) self.xml_input_dir に含まれる全XMLファイルを辞書化
        2) それらの辞書をまとめてリスト化
        3) ひとつのJSONファイル（self.json_output_file）に出力
        """
        logging.info(f"XML入力ディレクトリ: {self.xml_input_dir}")
        logging.info(f"JSON出力ファイル: {self.json_output_file}")

        # 出力用のリストを用意
        all_data = []

        # ディレクトリが存在しない場合のチェック（任意で追加）
        if not os.path.isdir(self.xml_input_dir):
            logging.error(f"指定された入力ディレクトリが存在しません: {self.xml_input_dir}")
            return

        # ディレクトリ内のXMLファイルを走査
        for filename in os.listdir(self.xml_input_dir):
            if filename.lower().endswith('.xml'):
                xml_path = os.path.join(self.xml_input_dir, filename)
                logging.info(f"処理対象XML: {xml_path}")

                try:
                    with open(xml_path, 'r', encoding='utf-8') as f:
                        data_dict = xmltodict.parse(f.read())
                    # 変換した辞書をリストに追加
                    all_data.append(data_dict)
                except Exception as e:
                    logging.error(f"XMLファイルの読み込み・変換中にエラーが発生しました: {xml_path}")
                    logging.error(e)

        # JSON出力前に、出力先ディレクトリが存在しない場合は作成する
        output_dir = os.path.dirname(self.json_output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # all_data を一つのリストとして JSON 化し、ファイルへ出力
        try:
            with open(self.json_output_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            logging.info(f"JSON出力完了: {self.json_output_file}")
        except Exception as e:
            logging.error(f"JSONファイルの書き込み中にエラーが発生しました: {self.json_output_file}")
            logging.error(e)

        logging.info("XML→JSON変換（全ファイルまとめて）が完了しました。")

