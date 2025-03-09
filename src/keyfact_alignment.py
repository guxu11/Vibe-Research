# Created by guxu at 2/27/25
import os

from utils import KeyFact, get_response_from_ollama, get_extract_keyfact_prompt, parsing_llm_extract_keyfact_output
from constants import SUMMARY_DIR, TEXT_CATEGORIES, KEYFACT_DIR
import json
import sys

task_id = int(sys.argv[1])
OLLAMA_HOST = sys.argv[2]
os.environ["OLLAMA_HOST"] = OLLAMA_HOST
print("OLLAMA_HOST: ", OLLAMA_HOST)

def extract_keyfact_single_file(file_path, model):
    with open(file_path, 'r') as f:
        summary_json = f.read()
    json_object = json.loads(summary_json)
    if 'key_facts' in json_object and json_object['key_facts']:
        return json_object
    reference = json_object['reference']
    json_object = {
        "raw_text": json_object['raw_text'],
        "reference": reference
    }
    prompt = get_extract_keyfact_prompt(reference)
    try:
        response = get_response_from_ollama(model, prompt, format=KeyFact.model_json_schema())
        keyfacts = parsing_llm_extract_keyfact_output(response)
        json_object.update(keyfacts)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return json_object

def extract_keyfact_all_files(model='llama3.3:latest'):
    for i, t in enumerate(TEXT_CATEGORIES):
        print(t)
        type_folder = os.path.join(SUMMARY_DIR, t)
        files = os.listdir(type_folder)
        files.sort()
        files = files[task_id::4]
        for file in files:
            print(f'******** {t}-{file} ********')
            summary_file_path = os.path.join(type_folder, file)
            keyfact_folder_path = os.path.join(KEYFACT_DIR, t)
            if not os.path.exists(keyfact_folder_path):
                os.makedirs(keyfact_folder_path)
            keyfact_file_path = os.path.join(keyfact_folder_path, file)
            json_object = extract_keyfact_single_file(summary_file_path, model)
            with open(keyfact_file_path, 'w') as f:
                f.write(json.dumps(json_object))
        print(f'{t} completed. {i + 1}/{len(TEXT_CATEGORIES)}')

if __name__ == '__main__':
    extract_keyfact_all_files()