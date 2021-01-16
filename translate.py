from collections import defaultdict
from pathlib import Path
import re
from googletrans import Translator
from google_trans_new import google_translator
import string
import importlib

def load_maps(module_names):
    res = {}
    for module_name in module_names:
        module = importlib.import_module(module_name)
        for k, v in module.m.items():
            if k not in res:
                res[k] = v
    return res

def translate_files(files, m):
    for file in files:
        print("TRANSLATING: ", file)
        txt = file.read_text(encoding='utf-8')
        for f, t in m.items():
            f = re.escape(f)
            txt = re.sub(f'([^а-яїіщёА-ЯЇІЩЁ]){f}([^а-яїіщёА-ЯЇІЩЁ])', f'\\1{t}\\2', txt)
        file.write_text(txt, encoding="utf-8")

def translate_word(word):
    translator = google_translator()
    res = translator.translate(word, lang_src='ru', lang_tgt='uk')
    res = res.strip()
    if word.istitle():
        res = res.title()
    elif word.islower():
        res = res.lower()
    elif word.isupper():
        res = res.upper()
    return res

def save_map_to_file(m, path, counts=None, skip_without_count=False):
    with open(path, "w", encoding="utf-8") as f:
        f.write('m = {\n')
        for k, v in m.items():
            row = f'"{k}": "{v}",'
            if counts is not None:
                if k in counts:
                    row += f' # cnt={counts[k]}'
                elif skip_without_count:
                    continue
            f.write(f'{row}\n')
        f.write('}\n')

def count_words(files):
    words_cnt = defaultdict(int)
    for file in files:
        print('COUNTING WORDS: ', file)
        txt = file.read_text(encoding='utf-8')
        lines = txt.splitlines()

        words = [word for line in lines for word in line.split(' ') if word != '']
        for word in words:
            word = word.strip(r' ()$,.:[]{}<>/0123456789"-\'' + string.ascii_letters)
            forbidden = set(r'[]{}()\\')
            if any((c in forbidden) for c in word):
                continue
            if re.search('[а-яїіщё]+', word, flags=re.IGNORECASE) is None:
                continue
            words_cnt[word] += 1
    return words_cnt

def build_maps_from_files(files, words_cnt, existing_mapping=None):
    res = {}
    skipped = {}

    common_words = filter(lambda p: p[1] > 1, words_cnt.items())
    common_words = sorted(common_words, key=lambda p:p[1], reverse=True)[:5000]
    
    for word, cnt in common_words:
        if existing_mapping is not None and word in existing_mapping:
            continue
        to = translate_word(word)
        print(f'ORIG: "{word}", TRANSLATED: "{to}", CNT: {cnt}, ADDED: {word != to}')
        if word != to:
            res[word] = to
        else:
            skipped[word] = to
        
    save_map_to_file(res, "map_ru_ua_gen.py", words_cnt)
    save_map_to_file(skipped, "map_ru_ua_skipped.py", words_cnt)

    return words_cnt, common_words

# files = [file for file in Path('').glob('templates/pages/*.html')]
# files.append(Path('templates/index.html'))
# words_cnt = count_words(files)
# build_maps_from_files(files, words_cnt, load_maps(['map_ru_ua_custom', 'map_ru_ua_top']))

# translate_files(files, load_maps(['map_ru_ua_custom', 'map_ru_ua_top', 'map_ru_ua_rest']))
translate_files([Path('../algorithms/templates/pages/eratosthenes_sieve.html')], load_maps(['map_ru_ua_custom', 'map_ru_ua_top', 'map_ru_ua_rest']))