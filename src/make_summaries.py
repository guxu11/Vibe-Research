# Created by guxu at 2/27/25
import json
import os
from utils import summarize_with_ollama

models = {'llama3.2': ['1b', '3b'], 'gemma2': ['2b'], 'qwen2.5': ['0.5b', '1.5b', '3b'], 'codegemma': ['2b'], 'opencoder': ['1.5b'], 'smollm': ['1.7b', '135m', '360m'], 'deepseek-r1': ['1.5b'], 'tinyllama': ['1.1b'], 'tinydolphin': ['1.1b'], 'phi': ['2.7b'], 'orca-mini': ['3b'], 'hermes3': ['3b'], 'moondream': ['1.8b'], 'stablelm-zephyr': ['3b']}
# models = {'llama3.2': ['1b']}

RAW_DATA_DIR = "../News Articles"
SUMMARY_DIR = "../summaries"

def make_summaries():
    types = os.listdir(RAW_DATA_DIR)
    print("types", types)
    for t in types:
        raw_text_files = os.listdir(os.path.join(RAW_DATA_DIR, t))
        raw_text_files.sort()
        for raw_text_file in raw_text_files:
            content = []
            try:
                raw_text_file_path = os.path.join(RAW_DATA_DIR, t, raw_text_file)
                print(raw_text_file)
                with open(raw_text_file_path, 'r') as f:
                    line = f.readline()
                    while line:
                        content.append(line)
                        line = f.readline()
                text = ' '.join(content)
                summaries_dict = {
                    "raw_text": text
                }
                for model, model_sizes in models.items():
                    for model_size in model_sizes:
                        model_name = f"{model}:{model_size}"
                        print(model_name)
                        summary = summarize_with_ollama(model_name, text)
                        print(summary)
                        summaries_dict[model_name] = summary
                summary_file_parent_path = os.path.join(SUMMARY_DIR, t)
                if not os.path.exists(summary_file_parent_path):
                    os.makedirs(summary_file_parent_path, exist_ok=True)
                summary_file_path = os.path.join(summary_file_parent_path, raw_text_file.replace('.txt', '.json'))
                with open(summary_file_path, 'w') as f:
                    f.write(json.dumps(summaries_dict))

            except Exception as e:
                print(e)
                continue



if __name__ == '__main__':
    make_summaries()
    # print(models)
