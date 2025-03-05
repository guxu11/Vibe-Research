# Created by guxu at 3/3/25

import json
import os
from constants import OLLAMA_MODEL_LIST, RAW_DATA_DIR, SUMMARY_DIR

def count_file():
    ret = 0
    for types in os.listdir(RAW_DATA_DIR):
        type_folder = os.path.join(RAW_DATA_DIR, types)
        ret += len(os.listdir(type_folder))
    return ret

def check_progress():
    text_count = count_file()
    summary_count = 0
    for types in os.listdir(SUMMARY_DIR):
        type_folder = os.path.join(SUMMARY_DIR, types)
        for summary_file in os.listdir(type_folder):
            summary_file = os.path.join(type_folder, summary_file)
            with open(summary_file, 'r') as f:
                json_data = json.load(f)
                summary_done = True
                for model in OLLAMA_MODEL_LIST:
                    if model not in json_data or not json_data[model] or json_data[model].startswith("ERROR"):
                        summary_done = False
                        break
                if summary_done:
                    summary_count += 1
    print(f"Text count: {text_count}, Summary count: {summary_count}")
    print(f"Progress: {summary_count / text_count * 100:.2f}%")

if __name__ == '__main__':
    check_progress()