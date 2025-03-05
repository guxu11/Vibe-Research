# Created by guxu at 2/27/25
from constants import SUMMARY_DIR, TEXT_CATEGORIES
import nltk.data

def split_text_into_sentences(text):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)
