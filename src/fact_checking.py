# Created by guxu at 2/27/25
import json
import sys
import traceback

from constants import SUMMARY_DIR, SENTENCE_DIR, TEXT_CATEGORIES, GPT_FACTERROR_DIR, OLLAMA_FACTERROR_DIR
from utils import get_client, get_response, get_fact_checking_prompt, parsing_llm_fact_checking_output, get_response_from_ollama
import os
import re
try:
    import nltk.data
except Exception as e:
    pass

task_id = 0
if sys.platform.startswith("linux"):
    task_id = int(sys.argv[1])
    OLLAMA_HOST = sys.argv[2]
    os.environ["OLLAMA_HOST"] = OLLAMA_HOST
    print("OLLAMA_HOST: ", OLLAMA_HOST)

def split_text_into_sentences(text):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)

def remove_think_deepseek(summary):
    return re.sub(r'<think>.*?</think>\s*', '', summary, flags=re.DOTALL)

def write_sentences():
    if not os.path.exists(SENTENCE_DIR):
        os.makedirs(SENTENCE_DIR)
    types = TEXT_CATEGORIES
    for t in types:
        print(t)
        if not os.path.exists(os.path.join(SENTENCE_DIR, t)):
            os.makedirs(os.path.join(SENTENCE_DIR, t))
        summaries_folder = os.listdir(os.path.join(SUMMARY_DIR, t))
        for summary_file in summaries_folder:
            print(summary_file)
            summary_file_path = os.path.join(SUMMARY_DIR, t, summary_file)
            sentence_file_path = os.path.join(SENTENCE_DIR, t, summary_file)
            try:
                with open(summary_file_path, 'r') as f:
                    summary_dict = json.load(f)
                if not summary_dict:
                    continue
                if os.path.exists(sentence_file_path):
                    with open(sentence_file_path, 'r') as f:
                        sentence_dict = json.load(f)
                else:
                    sentence_dict = {"raw_text": summary_dict['raw_text']}
                for model, summary in summary_dict.items():
                    if model == 'raw_text':
                        continue
                    if model == 'deepseek-r1:1.5b':
                        summary = remove_think_deepseek(summary)
                    try:
                        if model not in sentence_dict or not sentence_dict[model]:
                            sentences = split_text_into_sentences(summary)
                        else:
                            sentences = sentence_dict[model]
                        sentences = sentences if isinstance(sentences, list) else sentences['sentences']
                        sentence_dict[model]= {"sentences": sentences}
                    except Exception as e:
                        print(e)
                        continue
                with open(sentence_file_path, 'w') as f:
                    f.write(json.dumps(sentence_dict))
            except Exception as e:
                print(e)
                continue

MODEL_OPENAI = "chatgpt-4o-latest"
MODEL_OLLAMA = "llama3.3:latest"
def fact_checking_by_type(model_family='openai'):
    for i, t in enumerate(TEXT_CATEGORIES):
        print(t)
        sentence_folder = os.path.join(SENTENCE_DIR, t)
        factorrator_folder = os.path.join(GPT_FACTERROR_DIR, t) if model_family == 'openai' else os.path.join(OLLAMA_FACTERROR_DIR, t)
        os.makedirs(factorrator_folder, exist_ok=True)
        files = os.listdir(sentence_folder)
        files.sort()
        files = files[task_id::4]
        print(files)
        for file in files:
            print(f'******** {t}-{file} ********')
            try:
                with open(os.path.join(sentence_folder, file), 'r') as f:
                    sentence_dict = json.load(f)
                raw_text = sentence_dict['raw_text']
                factorrator_file = os.path.join(factorrator_folder, file)
                factorrator_dict = {'raw_text': raw_text}
                if os.path.exists(factorrator_file):
                    with open(factorrator_file, 'r') as f:
                        factorrator_dict = json.load(f)
                if 'fact_checking_status' in factorrator_dict and factorrator_dict['fact_checking_status'] == 'completed':
                    continue
                for model in sentence_dict:
                    if model == 'raw_text':
                        continue
                    if model in factorrator_dict and 'pred_labels' in factorrator_dict[model] and 'pred_types' in sentence_dict[model] \
                            and not (
                            len(factorrator_dict[model]['sentences']) > 1 and factorrator_dict[model]['pred_labels'] == [0] and factorrator_dict[model]['pred_types'] == ['no error']):
                        continue
                    print(model)
                    sentences = sentence_dict[model]
                    factorrator_dict.update({model: {"sentences": sentences}})
                    prompt = get_fact_checking_prompt(raw_text, sentences)
                    response = ""
                    try:
                        response = get_response(get_client(), prompt, MODEL_OPENAI) if model_family == 'openai' else get_response_from_ollama(MODEL_OLLAMA, prompt, timeout=90)
                    except Exception as e:
                        print(e)
                        traceback.format_exc()
                        continue
                    if response:
                        pred_labels, pred_types = parsing_llm_fact_checking_output(response)
                        factorrator_dict[model].update({'pred_labels': pred_labels})
                        factorrator_dict[model].update({'pred_types': pred_types})
                factorrator_dict.update({'fact_checking_status': 'completed'})
                with open(factorrator_file, 'w') as f:
                    f.write(json.dumps(factorrator_dict))
            except Exception as e:
                print(e)
                traceback.format_exc()
                continue
        print(f'{t} completed. {i + 1}/{len(TEXT_CATEGORIES)}')


if __name__ == '__main__':
    fact_checking_by_type()
    print("🎉 All tasks completed!")