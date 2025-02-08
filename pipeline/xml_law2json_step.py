import os
import json
import xmltodict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class XmlLawToJsonStep:
    def __init__(self, step_config):
        self.xml_input_dir = step_config.get('xml_input_dir', '')
        self.json_output_file = step_config.get('json_output_file', '')
        self.keys_to_remove = step_config.get('keys_to_remove', '')
        self.array_item = step_config.get('array_item', '')

    def remove_keys(self, data, keys_to_remove):
        """
        指定されたキーを辞書から削除する。
        ネストされた辞書にも対応。
        """
        if isinstance(data, dict):
            return {
                k: self.remove_keys(v, keys_to_remove)
                for k, v in data.items() if k not in keys_to_remove
            }
        elif isinstance(data, list):
            return [self.remove_keys(item, keys_to_remove) for item in data]
        else:
            return data
    
    def ensure_list_format(self, data, array_item):
        """
        指定されたキーについて、単一の要素であってもリストとして保持する。
        """
        if isinstance(data, dict):
            return {
                k: [v] if k in array_item and not isinstance(v, list) else self.ensure_list_format(v, array_item)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self.ensure_list_format(item, array_item) for item in data]
        else:
            return data

    def execute(self):
        logging.info(f"XML入力ディレクトリ: {self.xml_input_dir}")
        logging.info(f"JSON出力ファイル: {self.json_output_file}")
        
        all_data = []

        if not os.path.isdir(self.xml_input_dir):
            logging.error(f"指定された入力ディレクトリが存在しません: {self.xml_input_dir}")
            return

        for filename in os.listdir(self.xml_input_dir):
            if filename.lower().endswith('.xml'):
                xml_path = os.path.join(self.xml_input_dir, filename)
                logging.info(f"処理対象XML: {xml_path}")

                try:
                    with open(xml_path, 'r', encoding='utf-8') as f:
                        data_dict = xmltodict.parse(f.read())
                    
                    if self.keys_to_remove:
                        data_dict = self.remove_keys(data_dict, self.keys_to_remove)
                    
                    if self.array_item:
                        data_dict = self.ensure_list_format(data_dict, self.array_item)
                    
                    all_data.append(data_dict)
                except Exception as e:
                    logging.error(f"XMLファイルの読み込み・変換中にエラーが発生しました: {xml_path}")
                    logging.error(e)

        output_dir = os.path.dirname(self.json_output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        try:
            with open(self.json_output_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            logging.info(f"JSON出力完了: {self.json_output_file}")
        except Exception as e:
            logging.error(f"JSONファイルの書き込み中にエラーが発生しました: {self.json_output_file}")
            logging.error(e)

        logging.info("XML→JSON変換（全ファイルまとめて）が完了しました。")

