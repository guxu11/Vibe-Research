# Created by guxu at 3/10/25
import json

from constants import RESULT_DIR, SENTENCE_DIR, TEXT_CATEGORIES, BASELINE_MODEL, OLLAMA_MODEL_LIST
import os
import pandas as pd

from src.constants import OLLAMA_ALIGNMENT_DIR

MODELS = OLLAMA_MODEL_LIST + [BASELINE_MODEL]

def calculate_faithfulness_single_file(category, file_id):
    file_path = os.path.join(SENTENCE_DIR, category, file_id)
    with open(file_path, 'r') as f:
        summary_json = f.read()
    summary_json = json.loads(summary_json)
    text_id = f"{category}/{file_id}"
    print(text_id)
    category_data = [text_id]
    for model in MODELS:
        if not model in summary_json or not 'pred_labels' in summary_json[model] or not summary_json[model]['pred_labels']:
            category_data.append(0)
            continue
        pred_labels = summary_json[model]['pred_labels']
        faithfulness = round(pred_labels.count(0) / len(pred_labels), 4)
        category_data.append(faithfulness)
    return category_data

def calculate_faithfulness_all_files():
    faithfulness_data = []
    for category in TEXT_CATEGORIES:
        type_folder = os.path.join(SENTENCE_DIR, category)
        files = os.listdir(type_folder)
        files.sort()
        for file in files:
            category_data = calculate_faithfulness_single_file(category, file)
            faithfulness_data.append(category_data)
    faithfulness_path = os.path.join(RESULT_DIR, 'faithfulness')
    os.makedirs(faithfulness_path, exist_ok=True)
    faithfulness_file_path = os.path.join(faithfulness_path, 'faithfulness.csv')
    title = ['text_id'] + MODELS
    df = pd.DataFrame(faithfulness_data, columns=title)
    df.to_csv(faithfulness_file_path, index=False)

def calc_single_case(num_keyfacts, num_sentences, alignments):
    sentences_set = set()
    valid_keyfacts_count = 0
    for alignment in alignments:
        if 'line_numbers' not in alignment or 'response' not in alignment or 'line_numbers' not in alignment:
            continue
        if alignment['response'] and alignment['line_numbers']:
            for line in alignment['line_numbers']:
                sentences_set.add(line)
            valid_keyfacts_count += 1
    completeness = round(valid_keyfacts_count / num_keyfacts, 4) if num_keyfacts > 0 else 0
    conciseness = round(len(sentences_set) / num_sentences, 4) if num_sentences > 0 else 0
    return completeness, conciseness

def calc_single_file(category, file_id):
    file_path = os.path.join(OLLAMA_ALIGNMENT_DIR, category, file_id)
    text_id = f"{category}/{file_id}"
    with open(file_path, 'r') as f:
        alignments_json = f.read()
    alignments_json = json.loads(alignments_json)
    category_completeness_data = [text_id]
    category_conciseness_data = [text_id]
    num_keyfacts = len(alignments_json['key_facts'])
    for model in MODELS:
        if not model in alignments_json or not 'alignments' in alignments_json[model] or not alignments_json[model]['alignments']:
            category_completeness_data.append(0)
            category_conciseness_data.append(0)
            continue
        num_sentences = len(alignments_json[model]['sentences'])
        completeness, conciseness = calc_single_case(num_keyfacts, num_sentences, alignments_json[model]['alignments'])
        category_completeness_data.append(completeness)
        category_conciseness_data.append(conciseness)
    return category_completeness_data, category_conciseness_data

def calc_and_write_all_files():
    completeness_data, conciseness_data = [], []
    for category in TEXT_CATEGORIES:
        files = os.listdir(os.path.join(OLLAMA_ALIGNMENT_DIR, category))
        files.sort()
        for file_id in files:
            if not file_id.endswith('.json'):
                continue
            completeness, conciseness = calc_single_file(category, file_id)
            completeness_data.append(completeness)
            conciseness_data.append(conciseness)
    completeness_folder_path = os.path.join(RESULT_DIR, 'completeness')
    os.makedirs(completeness_folder_path, exist_ok=True)
    conciseness_folder_path = os.path.join(RESULT_DIR, 'conciseness')
    os.makedirs(conciseness_folder_path, exist_ok=True)

    completeness_file_path = os.path.join(completeness_folder_path, 'completeness.csv')
    conciseness_file_path = os.path.join(conciseness_folder_path, 'conciseness.csv')

    title = ['text_id'] + MODELS
    df = pd.DataFrame(completeness_data, columns=title)
    df.to_csv(completeness_file_path, index=False)
    df = pd.DataFrame(conciseness_data, columns=title)
    df.to_csv(conciseness_file_path, index=False)


if __name__ == '__main__':
    calc_and_write_all_files()