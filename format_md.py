from collections import defaultdict
from pathlib import Path
import re

def format_file(file:Path):
    print("FORMATTING: ", file)
    txt = file.read_text(encoding='utf-8')
    
    txt = txt.replace(' ~~~~ ', ' ')
    txt = txt.replace('---', '-')
    txt = txt.replace('.)', ').')
    txt = txt.replace('\t', '    ')
    txt = txt.replace('$O (', '$O(')
    txt = txt.replace('&lt;', '<')

    tags = {
        'ul': ('<ul>', '</ul>'),
        'li': ('<li>', '</li>'),
        'h1': ('<h1>', '</h1>'),
        'h2': ('<h2>', '</h2>'),
        'h3': ('<h3>', '</h3>'),
        'h4': ('<h4>', '</h4>'),
        'bf': ('**', '**'),
    }
    for tex_tag, md_tag in tags.items():
        open_tex_tag = f'\\{tex_tag}{{'
        open_tex_generic = '{'
        closed_tex_tag = '}'
        open_md_tag, closed_md_tag = md_tag

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
                txt = txt[:s] + open_md_tag + txt[s+len(open_tex_tag):e].strip(' ') + closed_md_tag + txt[e+len(closed_tex_tag):] 
            else:
                break

    code_id_prefix = '<!--- TODO: specify code snippet id -->'
    txt = re.sub(r'\\code(.+?)\\endcode', f'{code_id_prefix}\n``` cpp\\1```', txt, flags=re.DOTALL)
    txt = re.sub(r'<code>[\s\n]*', f'{code_id_prefix}\n``` cpp\n', txt)
    txt = re.sub(r'[\s\n]*</code>', '\n```', txt)
 
    txt = re.sub(r'\\href=([^{]+){([^}]+)}', '[\\2](\\1)', txt)
    txt = re.sub(r'\\algohref=([a-z_0-9]+)\{(.+?)\}', '[\\2](\\1)', txt)
    txt = re.sub(r'<algohref=([a-z_0-9]+)>(.+?)</algohref>', '[\\2](\\1)', txt)

    txt = re.sub(r'^<h1>\s*', '# ', txt)
    txt = re.sub(r'\n+<h1>\s*', '\n\n# ', txt)
    txt = re.sub(r'\n+<h2>\s*', '\n\n## ', txt)
    txt = re.sub(r'\n+<h3>\s*', '\n\n### ', txt)
    txt = re.sub(r'\n+<h4>\s*', '\n\n#### ', txt)
    txt = re.sub(r'<li>\s*', '* ', txt)
    txt = '\n'.join([re.sub(r'^(\s*)\\li\s*([^\{].+)$', '* \\2', line)  for line in txt.split('\n')])
    txt = re.sub(r'<\/p>\n*([^\n])', '\n\n\\1', txt)
    txt = re.sub(r'<br>', '\n', txt)
    txt = re.sub(r'<b>|</b>', '**', txt)
    txt = re.sub(r'<formula>\s*', '$$ ', txt)
    txt = re.sub(r'\s*</formula>', ' $$', txt)

    txt = txt.replace('<ul>', '')
    txt = txt.replace('<p>', '')
    txt = txt.replace('</h1>', '')
    txt = txt.replace('</h2>', '')
    txt = txt.replace('</h3>', '')
    txt = txt.replace('</h4>', '')
    txt = txt.replace('</ul>', '')
    txt = txt.replace('</li>', '')
    txt = re.sub(r'\n\n+', '\n\n', txt)

    txt = txt.strip()
    txt = f'{txt}\n'

    out_dir = file.parent / 'formatted_md'
    out_dir.mkdir(exist_ok=True)
    (out_dir / file.with_suffix('.md').name).write_text(txt, encoding="utf-8")

def format_files(files):
    for file in files:
        format_file(file)

format_files(list(Path('raw').glob('*.tex')))
# format_files(list(Path('../algorithms/templates/pages').glob('*.tex')))
# format_file(Path('../algorithms/templates/index.tex'))
# format_file(Path('../algorithms/templates/pages/bfs.html'))