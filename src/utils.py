# Created by guxu at 2/27/25
import concurrent.futures
import json
from typing import List

import openai
import ollama
import ast
import pprint
import multiprocessing
from pydantic import BaseModel


def get_api_key():
    base_path = '../.env'
    with open(base_path) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('OPENAI_API_KEY'):
                return line.split('=')[1].strip()
    return 'Not Found'

def get_client():
    return openai.OpenAI(api_key=get_api_key())

'''
This is for providing fundamental functions for FineSurE.
'''

ERROR_TYPES = ['out-of-context error', 'entity error', 'predicate error', 'circumstantial error', 'grammatical error',
               'coreference error', 'linking error', 'other error']


def get_response(client, prompt, model, temperature=0.0):
    ''' A function to get the response from GPT-series
    Args:
        client: openai client
        prompt: input prompt
        model: openai model name
    Return:
        text_response: the output from LLMs
    '''

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature)
    text_response = response.choices[0].message.content

    return text_response


'''
Two functions for fact checking
'''


def get_fact_checking_prompt(input, sentences):
    ''' A function to define the input prompt
    Args:
        input: input document
        sentences: list of summary sentences
    Return:
        prompt: the final input prompt
    '''

    num_sentences = str(len(sentences))
    sentences = '\n'.join(sentences)

    prompt = \
        """
        You will receive a transcript followed by a corresponding summary. Your task is to assess the factuality of each summary sentence across nine categories:
        * no error: the statement aligns explicitly with the content of the transcript and is factually consistent with it.
        * out-of-context error: the statement contains information not present in the transcript.
        * entity error: the primary arguments (or their attributes) of the predicate are wrong.
        * predicate error: the predicate in the summary statement is inconsistent with the transcript.
        * circumstantial error: the additional information (like location or time) specifying the circumstance around a predicate is wrong.
        * grammatical error: the grammar of the sentence is so wrong that it becomes meaningless.
        * coreference error: a pronoun or reference with wrong or non-existing antecedent.
        * linking error: error in how multiple statements are linked together in the discourse (for example temporal ordering or causal link).
        * other error: the statement contains any factuality error which is not defined here.
        
        Instruction:
        First, compare each summary sentence with the transcript.
        Second, provide a single sentence explaining which factuality error the sentence has.
        Third, answer the classified error category for each sentence in the summary.
        
        Provide your answer in JSON format. The answer should be a list of dictionaries whose keys are "sentence", "reason", and "category":
        [{"sentence": "first sentence", "reason": "your reason", "category": "no error"}, {"sentence": "second sentence", "reason": "your reason", "category": "out-of-context error"}, {"sentence": "third sentence", "reason": "your reason", "category": "entity error"},]
        
        Transcript:
        %s
        
        Summary with %s sentences:
        %s
        """ % (input, num_sentences, sentences)

    return prompt


def parsing_llm_fact_checking_output(output):
    ''' A function to parse the output from LLMs based on heuristic rules
    Args:
        output: the output from LLMs
    Return:
        pred_labels: the binary label for each sentence (0: no factuality error, 1: factuality error)
        pred_types: the error type of each sentence
    '''

    try:
        start_idx = output.find('[')

        if start_idx != -1:
            end_idx = output.find(']')
            output = output[start_idx:end_idx + 1]
            output = output.replace('\n', '')
            output = ast.literal_eval(output)

            pred_labels, pred_types = [], []
            for out in output:
                category = out["category"]
                category = category.replace('\n', '').replace('[', '').replace(']', '')
                if category.lower() == "no error":
                    pred_labels.append(0)
                else:
                    pred_labels.append(1)
                pred_types.append(category)
            return pred_labels, pred_types

        else:
            start_idx = output.find('{')
            end_idx = output.find('}')
            output = output[start_idx:end_idx + 1]
            output = output.replace('\n', '')
            output = ast.literal_eval(output)

            pred_labels, pred_types = [], []
            category = output["category"]
            category = category.replace('\n', '').replace('[', '').replace(']', '')
            if category.lower() == "no error":
                pred_labels.append(0)
            else:
                pred_labels.append(1)
            pred_types.append(category)
            return pred_labels, pred_types

    except Exception as e:

        try:
            subseqs = output.split("category")

            def error_detection(subseq):
                detected = False
                for error_type in ERROR_TYPES:
                    if error_type in subseq:
                        detected = True
                        detected_type = error_type
                if detected:
                    return 1, error_type
                else:
                    return 0, "no error"

            pred_labels, pred_types = [], []
            for subseq in subseqs:
                error_label, error_type = error_detection(subseq)
                pred_labels.append(error_label)
                pred_types.append(error_type)

            return pred_labels, pred_types

        except Exception as e:
            print('parsing error:', e)
            return [], []


'''
Two functions for keyfact alignment
'''

class KeyFactAlignments(BaseModel):
    class KeyFactAlignment(BaseModel):
        key_fact_number: int
        response: bool
        line_numbers: List[int]
    alignments: List[KeyFactAlignment]

def get_keyfact_alighment_prompt(keyfacts, sentences):
    ''' A function to define the input prompt
    Args:
        keyfacts: the list of keyfacts
        sentences: list of summary sentences
    Return:
        prompt: the final input prompt
    '''

    num_sentences = str(len(sentences))
    summary = ['[' + str(line_num + 1) + '] ' + sentence for line_num, sentence in enumerate(sentences)]
    summary = '\n'.join(summary)
    num_key_facts = str(len(keyfacts))
    key_facts = ['[' + str(line_num + 1) + '] ' + keyfact for line_num, keyfact in enumerate(keyfacts)]
    key_facts = '\n'.join(key_facts)

    prompt = \
        '''
        You will receive a summary and a set of key facts for the same transcript. Your task is to assess if each key fact is inferred from the summary.
        
        Instruction:
        First, compare each key fact with the summary.
        Second, check if the key fact is inferred from the summary and then response "True" or "False" for each key fact. If "True", specify the line_numbers of the summary sentence(s) relevant to each key fact. 
        
        Provide your answer in JSON format. The answer should be a list of dictionaries whose keys are "key_fact_number", "response", and "line_numbers":
        {"alignments": [{"key_fact_number": 1, "response": "True", "line_numbers": [1]}, {"key_fact_number": 2, "response": "False", "line_numbers": []}, {"key_fact_number": 3, "response": "True", "line_numbers": [1, 2, 3]}]}
        
        
        There are %s lines in the summary.
        Summary:
        %s
        
        There are %s key facts.
        key facts:
        %s
        ''' % (num_sentences, summary, num_key_facts, key_facts)

    return prompt


def parsing_llm_keyfact_alighment_output(output):
    ''' A function to parse the output from LLMs based on heuristic rules
    Args:
        output: the output from LLMs
    Return:
        pred_labels: the binary label for each keyfact (0: no match, 1: match)
        matched_lines: the list of sentence line numbers that align with at least one keyfact
    '''

    try:
        output = output.replace('```', '')
        start_idx = output.find('[')
        output = output[start_idx:]
        output = ast.literal_eval(output)

        matched_lines = set()
        pred_labels = []

        for out in output:
            category = out["response"]

            if category.lower() == "yes":
                pred_labels.append(1)
            else:
                pred_labels.append(0)

            if 'line number' in out:
                line_nums = out["line number"]

                for line_num in line_nums:
                    if type(line_num) is str:
                        line_num = line_num.replace('[', '').replace(']', '')
                    matched_lines.add(int(line_num))

        return pred_labels, list(matched_lines)

    except Exception as e:
        print(e)
        return [], []
def parsing_llm_keyfact_alignment_output(output):
    return json.loads(output)

'''
 Score funtions
'''


def compute_faithfulness_percentage_score(pred_faithfulness_labels):
    faithfulness = 1.0 - sum(pred_faithfulness_labels) / len(pred_faithfulness_labels)
    return faithfulness


def compute_completeness_percentage_score(pred_alignment_labels):
    completeness = sum(pred_alignment_labels) / len(pred_alignment_labels)
    return completeness


def compute_conciseness_percentage_score(pred_sentence_line_numbers, num_sentences):
    conciseness = len(pred_sentence_line_numbers) / num_sentences
    return conciseness

def get_summarization_prompt(transcript):
    return f"""
            Summarize the following text concisely, preserving key ideas and details.  
            Output only the summary as plain text—no explanations, no formatting, no reasoning process.

            {transcript}
            """
class KeyFact(BaseModel):
    key_facts: List[str]


def get_extract_keyfact_prompt(summary):
    return f'''
    You will be provided with a summary. Your task is to decompose
    the summary into a set of "key facts". A "key fact" is a single
    fact written as briefly and clearly as possible, encompassing at
    most 2-3 entities.
    Here are nine examples of key facts to illustrate the desired
    level of granularity:
    * Kevin Carr set off on his journey from Haytor.
    * Kevin Carr set off on his journey from Dartmoor.
    * Kevin Carr set off on his journey in July 2013.
    * Kevin Carr is less than 24 hours away from completing his trip.
    * Kevin Carr ran around the world unsupported.
    * Kevin Carr ran with his tent.
    * Kevin Carr is set to break the previous record.
    * Kevin Carr is set to break the record by 24 hours.
    * The previous record was held by an Australian.
    Instruction:
    First, read the summary carefully.
    Second, decompose the summary into (at most 16) key facts.
    
    Provide your answer in JSON format. The answer should be a
    dictionary with the key "key facts" containing the key facts as a
    list:
    
    {{"key_facts" ["first key fact", "second key facts", "third key facts"]}}
    
    Summary:
    {summary}
    '''

def parsing_llm_extract_keyfact_output(output):
    return json.loads(output)



def request_ollama(model, prompt, queue, **kwargs):
    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt.strip()}],
            **kwargs
        )
        queue.put(response['message']['content'])
    except Exception as e:
        queue.put(f"ERROR: {e}")


def summarize_with_ollama(model, transcript, timeout=60):
    prompt = get_summarization_prompt(transcript)
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=request_ollama, args=(model, prompt, queue))

    process.start()
    process.join(timeout)
    if process.is_alive():
        print(f"⏳ Timeout: Model {model} took too long, killing process...")
        process.terminate()
        process.join()
        return ""

    return queue.get() if not queue.empty() else ""

def get_response_from_ollama(model, prompt, timeout=60, **kwargs):
    """ 使用多进程调用 Ollama，支持超时控制 """
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=request_ollama, args=(model, prompt, queue), kwargs=kwargs)
    process.start()

    if timeout > 0:
        process.join(timeout)  # 等待最多 `timeout` 秒
        if process.is_alive():
            print(f"⏳ Timeout: Model {model} took too long, killing process...")
            process.terminate()
            process.join()
            return ""

    else:
        process.join()  # `timeout <= 0` 时，等待进程执行完毕（无超时）

    return queue.get() if not queue.empty() else ""

def get_ollama_model_list():
    models = []
    try:
        response = ollama.list()
        models = response['models']
    except Exception as e:
        pprint.pprint(e)
        return []
    if not models:
        return []
    return [{"model": m.model, "parameter_size": m.details.parameter_size} for m in models]


if __name__ == '__main__':
    raw_text = '''
    Ad sales boost Time Warner profit

    Quarterly profits at US media giant TimeWarner jumped 76% to $1.13bn (£600m) for the three months to December, from $639m year-earlier.

    The firm, which is now one of the biggest investors in Google, benefited from sales of high-speed internet connections and higher advert sales. TimeWarner said fourth quarter sales rose 2% to $11.1bn from $10.9bn. Its profits were buoyed by one-off gains which offset a profit dip at Warner Bros, and less users for AOL.

    Time Warner said on Friday that it now owns 8% of search-engine Google. But its own internet business, AOL, had has mixed fortunes. It lost 464,000 subscribers in the fourth quarter profits were lower than in the preceding three quarters. However, the company said AOL's underlying profit before exceptional items rose 8% on the back of stronger internet advertising revenues. It hopes to increase subscribers by offering the online service free to TimeWarner internet customers and will try to sign up AOL's existing customers for high-speed broadband. TimeWarner also has to restate 2000 and 2003 results following a probe by the US Securities Exchange Commission (SEC), which is close to concluding.

    Time Warner's fourth quarter profits were slightly better than analysts' expectations. But its film division saw profits slump 27% to $284m, helped by box-office flops Alexander and Catwoman, a sharp contrast to year-earlier, when the third and final film in the Lord of the Rings trilogy boosted results. For the full-year, TimeWarner posted a profit of $3.36bn, up 27% from its 2003 performance, while revenues grew 6.4% to $42.09bn. "Our financial performance was strong, meeting or exceeding all of our full-year objectives and greatly enhancing our flexibility," chairman and chief executive Richard Parsons said. For 2005, TimeWarner is projecting operating earnings growth of around 5%, and also expects higher revenue and wider profit margins.

    TimeWarner is to restate its accounts as part of efforts to resolve an inquiry into AOL by US market regulators. It has already offered to pay $300m to settle charges, in a deal that is under review by the SEC. The company said it was unable to estimate the amount it needed to set aside for legal reserves, which it previously set at $500m. It intends to adjust the way it accounts for a deal with German music publisher Bertelsmann's purchase of a stake in AOL Europe, which it had reported as advertising revenue. It will now book the sale of its stake in AOL Europe as a loss on the value of that stake.

    '''
    print(get_extract_keyfact_prompt(raw_text))