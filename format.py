from collections import defaultdict
from pathlib import Path
import re

def format_files(files):
    for file in files:
        print("FORMATTING: ", file)
        txt = file.read_text(encoding='utf-8')
        
        txt = txt.replace(' ~~~~ ', ' ')
        txt = txt.replace('---', '-')
        txt = txt.replace('.)', ').')
        txt = txt.replace('\t', '    ')
        txt = txt.replace('$O (', '$O(')
        tags = {'ul':'ul',
                'li': 'li',
                'h1': 'h1',
                'h2': 'h2',
                'h3': 'h3',
                'h4': 'h4',
                'bf': 'b',
                }
        for tex_tag, html_tag in tags.items():
            open_tex_tag = f'\\{tex_tag}{{'
            open_tex_generic = '{'
            closed_tex_tag = '}'
            open_html_tag = f'<{html_tag}>'
            closed_html_tag = f'</{html_tag}>'

            while True:
                s = txt.find(open_tex_tag)
                if s == -1:
                    break

                e = -1
                nxt = s + len(open_tex_tag)
                cnt = 1
                while (cnt != 0):
                    k1 = txt.find(open_tex_generic, nxt)
                    k2 = txt.find(closed_tex_tag, nxt)
                    if k1 != -1 and k1 < k2:
                        cnt += 1
                        nxt = k1 + len(open_tex_generic)
                    elif k2 != -1:
                        cnt -= 1
                        nxt = k2 + len(closed_tex_tag)
                        e = k2
                    else:
                        break

                if e != -1 and cnt == 0:
                    txt = txt[:s] + open_html_tag + txt[s+len(open_tex_tag):e].strip(' ') + closed_html_tag + txt[e+len(closed_tex_tag):] 
                else:
                    break

        txt = re.sub(r'\n+<h1>', '\n\n\n\n\n<h1>', txt)
        txt = re.sub(r'\n+<h2>', '\n\n\n\n<h2>', txt)
        txt = re.sub(r'\n+<h3>', '\n\n\n<h3>', txt)
        txt = re.sub(r'\n+<h4>', '\n\n<h4>', txt)
        txt = re.sub(r'\\href=([^{]+){([^}]+)}', '<a href="\\1">\\2</a>', txt)
        txt = re.sub(r'\\algohref=([a-z_0-9]+)\{([а-яїіщёА-ЯЇІЩЁ0-9 ]+)\}', '<a href="\\1">\\2</a>', txt)
        txt = '\n'.join([line if re.match('^([а-яА-Я(]|<b>).+([а-яА-Я.:)]|<\/b>)$', line) is None else f'<p>{line}</p>' for line in txt.split('\n')])
        txt = '\n'.join([re.sub(r'^(\s*)\\li\s*([^\{].+)$', '\\1<li>\\2</li>', line)  for line in txt.split('\n')])

        txt = txt.strip()

        file.write_text(txt, encoding="utf-8")

files = [file for file in Path('').glob('templates/pages/*.html')]
files.append(Path('templates/index.html'))

# skip_files = []
skip_files = ['index.html']
# skip_files = ['index.html, 'euler_function.html']
files = [file for file in files if file.name not in skip_files]

format_files(files)