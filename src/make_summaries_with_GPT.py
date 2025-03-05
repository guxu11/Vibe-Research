# Created by guxu at 3/4/25
from utils import get_client, get_response, get_summarization_prompt
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from constants import SUMMARY_DIR, TEXT_CATEGORIES

MODEL = "chatgpt-4o-latest"
MAX_THREADS = max_threads = os.cpu_count() * 2
print(f"Using {MAX_THREADS} threads.")


def make_summaries_from_gpt(t):
    folder = os.path.join(SUMMARY_DIR, t)
    files = os.listdir(folder)
    files.sort()
    for file in files:
        if not file.endswith('.json'):
            continue
        print(f"Processing file: {t}-{file}")
        file_path = os.path.join(folder, file)
        with open(file_path, 'r') as f:
            summary_json = f.read()
        json_object = json.loads(summary_json)
        if MODEL in json_object:
            continue
        raw_text = json_object['raw_text']
        prompt = get_summarization_prompt(raw_text)
        try:
            client = get_client()
            response = get_response(client, prompt, MODEL)
            json_object[MODEL] = response
            with open(file_path, 'w') as f:
                json.dump(json_object, f)
        except Exception as e:
            print(f"Error processing {file}: {e}")
            return f"Error in {t}: {e}"
    return f"Completed: {t}"


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(make_summaries_from_gpt, t): t for t in TEXT_CATEGORIES}

        for future in as_completed(futures):
            result = future.result()
            print(result)

    print("All threads completed.")
