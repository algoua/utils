import requests
import re
import json
from pathlib import Path
from typing import List
from tqdm import tqdm


def gpt_correct(text: str):
    url = 'http://moon-vm-ubuntu.home:3000/api/chat'
    data = {
        "model": {
            "id": "gpt-3.5-turbo",
            "name": "GPT-3.5",
            "maxLength": 12000,
            "tokenLimit": 4000,
        },
        "messages": [{
            "role": "user",
            "content": text,
        }],
        "key": "",
        "prompt": "Будь-ласка, як лінгвіст з української мови, виправляй граматичні помилки у моїх наступних повідомленнях. Текст може містити русизми чи російські слова, які повинні бути замінені на українські. Також текст може містити LaTeX вставки між $ символом, які повинні бути не змінені. Виправлений текст напиши без пояснень і без цитування. Нічого не дописуй.",
        "temperature": 0.5,
    }
    resp = requests.post(url, data=json.dumps(data).encode('utf-8'))
    resp.raise_for_status()
    return resp.content.decode('utf-8')


def gpt_correct_file(text: str):
    lines = text.splitlines()
    result = []
    for line in lines:
        words = [word for word in line.split(' ') if word != '']
        cyrillic_words = [word for word in words if re.match(
            '[а-яїіщё]+', word, flags=re.IGNORECASE)]
        if len(cyrillic_words) < 2:
            result.append(line)
            continue
        print(f'FROM: {line}')
        input_line = line
        # Skip Markdown symbols.
        prefix = ''
        h = re.match(r'^(#+\s)', line)
        if h:
            prefix = h.group(1)
            input_line = input_line[len(prefix):]
        if input_line.startswith('* ') and not prefix:
            prefix = '* '
            input_line = input_line[len(prefix):]
        # Correct line.
        corrected_line = gpt_correct(input_line)
        if abs(len(corrected_line) / len(input_line) - 1) > 0.6:
            print(f'INPUT: {input_line}')
            print(f'OUTPUT: {corrected_line}')
            print(f'GPT failed to correct the input! Reverting to original.')
            corrected_line = input_line
        # Restore Markdown symbols.
        corrected_line = prefix + corrected_line
        # Dot at the end of the line is sometimes added by GPT when not needed.
        if corrected_line.endswith('.') and not line.endswith('.'):
            corrected_line = corrected_line[:-1]
        # Preserve capitalization of the first letter.
        if line[0].isupper() and not corrected_line[0].isupper():
            corrected_line = corrected_line[0].upper() + corrected_line[1:]
        if line[0].islower() and not corrected_line[0].islower():
            corrected_line = corrected_line[0].lower() + corrected_line[1:]
        print(f'TO: {corrected_line}')
        result.append(corrected_line)
    return '\n'.join(result)


def gpt_correct_files(files: List[str], save_dir: Path):
    save_dir.mkdir(exist_ok=True)
    failed_files = []
    for file in tqdm(sorted(files)):
        save_file = save_dir / file.name
        if save_file.exists():
            continue
        print(f"FILE: {file}")
        text = file.read_text(encoding='utf-8')
        try:
            text = gpt_correct_file(text)
        except Exception as e:
            print(e)
            failed_files.append(file)
            continue
        save_file.write_text(text, encoding='utf-8')
        print(f"SAVED: {save_file}")


root_dir = Path('../algoua')
gpt_correct_files(list((root_dir / 'translated_md').glob('*.md')),
                  root_dir / 'latest_md')
# print(gpt_correct("Довга арифметика - це набір программных средств (структури данних і алгоритми), які дозволяють працювати з числами набагато великих величин, ніж це дозволяють стандартні типи данних."))
