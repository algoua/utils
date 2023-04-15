import requests
import re
import json
import urllib.parse
from pathlib import Path
from typing import List
from tqdm import tqdm


def format_code(text: str):
    url = 'https://formatter.org/admin/format'
    data = {
        "language": "cpp",
        "codeSrc": urllib.parse.quote(text),
        "style": "LLVM",
        "indentWidth": "4",
        "columnLimit": "1000",
    }
    resp = requests.post(url, data=json.dumps(data).encode('utf-8'))
    resp.raise_for_status()
    resp_json = json.loads(resp.content.decode('utf-8'))
    if resp_json['errcode'] != 0:
        raise Exception(
            f"format_code failed: errorcode={resp_json['errcode']} errmsg={resp_json['errmsg']}")
    return urllib.parse.unquote(resp_json['codeDst'])


def format_code_file(text: str):
    code_blocks = re.findall(r'``` cpp\n(.*?)```', text, flags=re.DOTALL)
    for code_block in code_blocks:
        formatted_code_block = format_code(code_block)
        print(f"FROM: {code_block}")
        print(f"TO: {formatted_code_block}")
        text = text.replace(code_block, formatted_code_block)
    return text


def format_code_files(files: List[str], save_dir: Path):
    save_dir.mkdir(exist_ok=True)
    for file in tqdm(sorted(files)):
        print(f"FILE: {file}")
        text = file.read_text(encoding='utf-8')
        text = format_code_file(text)
        save_file = save_dir / file.name
        save_file.write_text(text, encoding='utf-8')
        print(f"SAVED: {save_file}")


root_dir = Path('../algoua')
format_code_files(list((root_dir / 'formatted_md').glob('*.md')),
                  root_dir / 'formatted_md')
