# Created by guxu at 2/27/25
import json
import os
from utils import summarize_with_ollama
import sys

# type_index = int(sys.argv[1])
# type_index = 1

models = {'llama3.2': ['1b', '3b'], 'gemma2': ['2b'], 'qwen2.5': ['0.5b', '1.5b', '3b'], 'opencoder': ['1.5b'], 'smollm': ['1.7b'], 'deepseek-r1': ['1.5b'], 'tinyllama': ['1.1b'], 'tinydolphin': ['1.1b'], 'phi': ['2.7b'], 'orca-mini': ['3b'], 'hermes3': ['3b'], 'stablelm-zephyr': ['3b'], 'stablelm2': ['1.6b'], 'granite3.1-dense': ['2b']}
model_names = []
for model, model_sizes in models.items():
    for model_size in model_sizes:
        model_names.append(f"{model}:{model_size}")

RAW_DATA_DIR = "../News Articles"
SUMMARY_DIR = "../summaries"
types = [
    "business",
    "entertainment",
    "politics",
    "sport",
    "tech",
]

def make_summaries():
    for type_index in range(len(types)):
        raw_text_files = os.listdir(os.path.join(RAW_DATA_DIR, types[type_index]))
        raw_text_files.sort()
        for raw_text_file in raw_text_files:
            content = []
            try:
                raw_text_file_path = os.path.join(RAW_DATA_DIR, types[type_index], raw_text_file)
                print(raw_text_file)
                with open(raw_text_file_path, 'r') as f:
                    line = f.readline()
                    while line:
                        content.append(line)
                        line = f.readline()
                text = ' '.join(content)
                summary_file_parent_path = os.path.join(SUMMARY_DIR, types[type_index])
                if not os.path.exists(summary_file_parent_path):
                    os.makedirs(summary_file_parent_path, exist_ok=True)
                summary_file_path = os.path.join(summary_file_parent_path, raw_text_file.replace('.txt', '.json'))
                summaries_dict = {
                    "raw_text": text
                }
                if os.path.exists(summary_file_path):
                    with open(summary_file_path, 'r') as file:
                        summaries_dict = json.load(file)

                keys_to_delete = [k for k in summaries_dict if k != "raw_text" and k not in model_names]

                for k in keys_to_delete:
                    del summaries_dict[k]

                summary_needed_models = []
                for _model in model_names:
                    if _model not in summaries_dict or len(summaries_dict[_model]) == 0:
                        summary_needed_models.append(_model)

                for model_name in summary_needed_models:
                    print(model_name)
                    summary = summarize_with_ollama(model_name, text)
                    summaries_dict[model_name] = summary

                with open(summary_file_path, 'w') as f:
                    f.write(json.dumps(summaries_dict))

            except Exception as e:
                print(e)
                continue



if __name__ == '__main__':
    make_summaries()
    # print(models)
