# Created by guxu at 3/4/25
RAW_DATA_DIR = "../data/kaggle/News Articles"
REFERENCE_DIR = "../data/kaggle/References"
SUMMARY_DIR = "../data/summaries"
SENTENCE_DIR = "../data/sentences"
OLLAMA_KEYFACT_DIR = "../data/ollama_output/keyfacts"
OLLAMA_ALIGNMENT_DIR = "../data/ollama_output/alignments"
OLLAMA_FACTERROR_DIR = "../data/ollama_output/facterrors"

GPT_KEYFACT_DIR = "../data/gpt_output/keyfacts"
GPT_ALIGNMENT_DIR = "../data/gpt_output/alignments"
GPT_FACTERROR_DIR = "../data/gpt_output/facterrors"

RESULT_DIR = "../result"

OLLAMA_MODELS = {
    'llama3.2': ['1b', '3b'], 'gemma2': ['2b'], 'qwen2.5': ['0.5b', '1.5b', '3b'],
    'opencoder': ['1.5b'], 'smollm': ['1.7b'], 'deepseek-r1': ['1.5b'],
    'tinyllama': ['1.1b'], 'tinydolphin': ['1.1b'], 'phi': ['2.7b'],
    'orca-mini': ['3b'], 'hermes3': ['3b'], 'stablelm-zephyr': ['3b'],
    'stablelm2': ['1.6b'], 'granite3.1-dense': ['2b']
}
BASELINE_MODEL = 'chatgpt-4o-latest'

OLLAMA_MODEL_LIST = [f"{model}:{size}" for model, sizes in OLLAMA_MODELS.items() for size in sizes]
OLLAMA_REQUEST_TIME_OUT=90

TEXT_CATEGORIES = [
    "business",
    "entertainment",
    "politics",
    "sport",
    "tech",
]

CONFIG_FILE_PATH = '../config/model_config_dev.yml'