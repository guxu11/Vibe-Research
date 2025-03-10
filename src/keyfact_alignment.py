# Created by guxu at 2/27/25
import os

from utils import KeyFact, get_response_from_ollama, get_extract_keyfact_prompt, parsing_llm_extract_keyfact_output, \
    get_keyfact_alighment_prompt, parsing_llm_keyfact_alignment_output, KeyFactAlignments
from constants import SUMMARY_DIR, TEXT_CATEGORIES, KEYFACT_DIR, ALIGNMENT_DIR, SENTENCE_DIR
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

def compute_keyfact_alignment_single_file(sentence_path, keyfact_path, alignment_path, llm):
    with open(sentence_path, 'r') as f:
        sentence_file = f.read()
    sentence_object = json.loads(sentence_file)
    raw_text = sentence_object['raw_text']
    with open(keyfact_path, 'r') as f:
        keyfact_file = f.read()
    keyfact_object = json.loads(keyfact_file)
    keyfacts = keyfact_object['key_facts']
    alignment_dict = {
        "raw_text": raw_text,
        "key_facts": keyfacts
    }
    if os.path.exists(alignment_path):
        with open(alignment_path, 'r') as f:
            alignment_file = f.read()
        alignment_dict = json.loads(alignment_file)

    for model in sentence_object:
        if model == 'raw_text' or model == 'fact_checking_status':
            continue
        if can_pass(alignment_dict, model):
            continue
        print(model)
        sentences = sentence_object[model]['sentences']
        prompt = get_keyfact_alighment_prompt(keyfacts=keyfacts, sentences=sentences)
        try:
            response = get_response_from_ollama(llm, prompt, format=KeyFactAlignments.model_json_schema())
            alignment_json = parsing_llm_keyfact_alignment_output(response)
            alignment_dict[model] = {}
            alignment_dict[model].update({'sentences': sentences})
            alignment_dict[model].update(alignment_json)
        except Exception as e:
            print(f"Error processing {model}: {e}")
            continue
    return alignment_dict

def can_pass(alignment_dict, model):
    if not alignment_dict:
        return False
    if not model in alignment_dict:
        return False
    alignment = alignment_dict[model]
    if not ('alignments' in alignment and alignment['alignments']):
        return False
    return True

def compute_keyfact_alignment_all_files(model='llama3.3:latest'):
    for i, t in enumerate(TEXT_CATEGORIES):
        print(t)
        type_folder = os.path.join(SENTENCE_DIR, t)
        files = os.listdir(type_folder)
        files.sort()
        files = files[task_id::4]
        print(files)
        for file in files:
            print(f'******** {t}-{file} ********')
            sentence_file_path = os.path.join(type_folder, file)
            keyfact_folder_path = os.path.join(KEYFACT_DIR, t, file)
            alignment_folder_path = os.path.join(ALIGNMENT_DIR, t)
            if not os.path.exists(alignment_folder_path):
                os.makedirs(alignment_folder_path, exist_ok=True)
            try:
                alignment_file_path = os.path.join(alignment_folder_path, file)
                alignment_dict = compute_keyfact_alignment_single_file(sentence_file_path, keyfact_folder_path, alignment_file_path, model)
                with open(alignment_file_path, 'w') as f:
                    f.write(json.dumps(alignment_dict))
            except Exception as e:
                print(e)
                continue
        print(f'{t} completed. {i + 1}/{len(TEXT_CATEGORIES)}')



if __name__ == '__main__':
    # extract_keyfact_all_files()
    compute_keyfact_alignment_all_files()