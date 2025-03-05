# Created by guxu at 2/27/25
import json

from constants import SUMMARY_DIR, SENTENCE_DIR
import nltk.data
import os

def split_text_into_sentences(text):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)

def write_sentences():
    if not os.path.exists(SENTENCE_DIR):
        os.makedirs(SENTENCE_DIR)
    types = os.listdir(SUMMARY_DIR)
    for t in types:
        print(t)
        if not os.path.exists(os.path.join(SENTENCE_DIR, t)):
            os.makedirs(os.path.join(SENTENCE_DIR, t))
        summaries_folder = os.listdir(os.path.join(SUMMARY_DIR, t))
        for summary_file in summaries_folder:
            print(summary_file)
            summary_file_path = os.path.join(SUMMARY_DIR, t, summary_file)
            try:
                with open(summary_file_path, 'r') as f:
                    summary_dict = json.load(f)
                if not summary_dict:
                    continue
                sentence_dict = {"raw_text": summary_dict['raw_text'],}
                for model, summary in summary_dict.items():
                    if model == 'raw_text':
                        continue
                    try:
                        sentences = split_text_into_sentences(summary)
                        sentence_dict[model] = sentences
                    except Exception as e:
                        print(e)
                        continue
                sentence_file_path = os.path.join(SENTENCE_DIR, t, summary_file)
                with open(sentence_file_path, 'w') as f:
                    f.write(json.dumps(sentence_dict))
            except Exception as e:
                print(e)
                continue



if __name__ == '__main__':
    write_sentences()