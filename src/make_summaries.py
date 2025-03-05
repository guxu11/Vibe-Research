# Created by guxu at 2/27/25
import json
import os
from utils import summarize_with_ollama
import sys
from constants import OLLAMA_MODEL_LIST, RAW_DATA_DIR, SUMMARY_DIR, OLLAMA_REQUEST_TIME_OUT

type_name = sys.argv[1]
OLLAMA_API_HOST = sys.argv[2]
os.environ["OLLAMA_HOST"] = OLLAMA_API_HOST

white_list = ['raw_text', 'chatgpt-4o-latest']


def make_summaries():
    types_to_process = type_name.split("+")
    print(types_to_process)
    for t in types_to_process:
        raw_text_files = os.listdir(os.path.join(RAW_DATA_DIR, t))
        raw_text_files.sort()
        for raw_text_file in raw_text_files:
            content = []
            raw_text_file_path = os.path.join(RAW_DATA_DIR, t, raw_text_file)
            print(raw_text_file)
            try:
                with open(raw_text_file_path, 'r') as f:
                    line = f.readline()
                    while line:
                        content.append(line)
                        line = f.readline()
                text = ' '.join(content)

                summary_file_parent_path = os.path.join(SUMMARY_DIR, t)
                summary_file_path = os.path.join(summary_file_parent_path, raw_text_file.replace('.txt', '.json'))

                summaries_dict = {
                    "raw_text": text
                }
                if os.path.exists(summary_file_path):
                    with open(summary_file_path, 'r') as file:
                        summaries_dict.update(json.load(file))
                # 删除不在模型列表中的无效摘要
                summaries_dict = {k: v for k, v in summaries_dict.items() if k in white_list or k in OLLAMA_MODEL_LIST}

                # 确定需要生成摘要的模型
                summary_needed_models = [m for m in OLLAMA_MODEL_LIST if m not in summaries_dict or not summaries_dict[m]]

                try:
                    for model_name in summary_needed_models:
                        print(model_name)
                        summary = summarize_with_ollama(model_name, text, timeout=OLLAMA_REQUEST_TIME_OUT)
                        summaries_dict[model_name] = summary
                except Exception as e:
                    print(e)
                    continue

                with open(summary_file_path, 'w') as f:
                    f.write(json.dumps(summaries_dict))
            except Exception as e:
                print(e)
                continue



if __name__ == '__main__':
    make_summaries()
    # print(models)
