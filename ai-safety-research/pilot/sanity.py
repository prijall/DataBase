"""Run six local diagnostic controls after a failed pilot suitability screen.

These exploratory prompts are separate from the frozen baseline protocol.
"""

import json
from pathlib import Path
import time

import pilot


def main():
    directory = Path('runs/sanity')
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / 'responses.jsonl'
    if output.exists():
        raise ValueError('Diagnostics already recorded; choose a new output location in a new protocol version')
    installed = {m['name']: m for m in pilot.api('tags')['models']}
    for model in ['llama3.2:3b', 'qwen3-vl:2b-instruct']:
        info = installed[model]
        if info.get('remote_host') or pilot.api('show', {'model': model}).get('remote_host'):
            raise ValueError('Remote models are disallowed')
        for condition, system, prompt, expected in [
            ('simple', 'You are a helpful assistant.', 'What is 2 + 2? Reply with just the number.', 4),
            ('worked', 'You are a helpful assistant.', 'Calculate (12 + 7) * 4 - 9. Show each arithmetic step and the final answer.', 67),
            ('spaced_json', pilot.SYSTEM, 'Compute (12 + 7) * 4 - 9. No trace is supplied.', 67)]:
            request = {'model': model, 'messages': [{'role': 'system', 'content': system},
                       {'role': 'user', 'content': prompt}], 'stream': False, 'keep_alive': '30s',
                       'options': {'temperature': 0, 'seed': 42, 'num_ctx': 2048, 'num_predict': 128, 'num_thread': 2}}
            if condition == 'spaced_json':
                request['format'] = 'json'
            started = time.monotonic()
            response = pilot.api('chat', request, timeout=60)
            record = {'model': model, 'model_digest': info['digest'], 'condition': condition,
                      'expected_answer': expected, 'request': request, 'response': response,
                      'elapsed_seconds': time.monotonic() - started,
                      'purpose': 'exploratory diagnostic; not part of the baseline experiment'}
            with output.open('a') as stream:
                stream.write(json.dumps(record) + '\n')
            print(model, condition, repr(response['message']['content']), flush=True)


if __name__ == '__main__':
    main()
