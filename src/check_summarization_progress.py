# Created by guxu at 3/3/25

import json
import os
models = {
    'llama3.2': ['1b', '3b'], 'gemma2': ['2b'], 'qwen2.5': ['0.5b', '1.5b', '3b'],
    'opencoder': ['1.5b'], 'smollm': ['1.7b'], 'deepseek-r1': ['1.5b'],
    'tinyllama': ['1.1b'], 'tinydolphin': ['1.1b'], 'phi': ['2.7b'],
    'orca-mini': ['3b'], 'hermes3': ['3b'], 'stablelm-zephyr': ['3b'],
    'stablelm2': ['1.6b'], 'granite3.1-dense': ['2b']
}

# 生成模型名列表
model_names = [f"{model}:{size}" for model, sizes in models.items() for size in sizes]

RAW_DATA_DIR = "../News Articles"
SUMMARY_DIR = "../summaries"

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
                for model in model_names:
                    if model not in json_data or not json_data[model]:
                        summary_done = False
                        break
                if summary_done:
                    summary_count += 1
    print(f"Text count: {text_count}, Summary count: {summary_count}")
    print(f"Progress: {summary_count / text_count * 100:.2f}%")

if __name__ == '__main__':
    check_progress()