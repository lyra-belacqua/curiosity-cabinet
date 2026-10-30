#!/usr/bin/env python3
"""Turn a JSON shelf of ideas into a searchable, self-contained HTML cabinet.

Python 3.10+, standard library only. No remote assets, trackers or services.
"""
import argparse
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

__version__ = '0.1.0'

STYLE = '''
:root{color-scheme:dark;--paper:#17151d;--ink:#ece6f1;--muted:#aaa0b7;--line:#3a3245;--accent:#c7a7ee}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 system-ui,sans-serif}
main{max-width:1100px;margin:auto;padding:72px 28px 40px}header{max-width:760px;margin-bottom:44px}
.eyebrow{text-transform:uppercase;letter-spacing:.22em;font-size:11px;color:var(--accent)}
h1{font:clamp(42px,7vw,78px)/1.05 Georgia,serif;font-weight:400;letter-spacing:-.045em;margin:22px 0}
h1 em{color:var(--accent);font-weight:400}header p{color:var(--muted);max-width:580px}
label{display:block;font-size:12px;color:var(--muted);margin-bottom:7px}
input{font:inherit;width:100%;border:1px solid var(--line);background:#211c29;color:var(--ink);border-radius:10px;padding:14px 18px}
input:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:4px}
.shelf{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,280px),1fr));gap:20px;margin:28px 0}
article{border:1px solid var(--line);border-radius:14px;padding:25px;background:linear-gradient(140deg,#272030,#1c1822)}
article[hidden]{display:none}.number{color:var(--accent);font:italic 18px Georgia,serif}h2{font:26px/1.25 Georgia,serif;font-weight:400}
.note{color:#c8bfce;white-space:pre-wrap}.tags{display:flex;flex-wrap:wrap;gap:7px;margin-top:24px}
.tag{font-size:11px;border:1px solid #4d3b60;border-radius:20px;color:var(--accent);padding:3px 10px}
a{color:var(--accent)}footer{border-top:1px solid var(--line);padding-top:20px;display:flex;flex-wrap:wrap;gap:16px;justify-content:space-between;color:var(--muted);font-size:12px}
#empty{color:var(--muted)}@media(max-width:550px){main{padding-top:36px}}
'''

SCRIPT = '''
const search = document.querySelector('input');
const cards = [...document.querySelectorAll('article')];
function filter() {
  const query = search.value.trim().toLocaleLowerCase();
  let visible = 0;
  for (const card of cards) {
    card.hidden = !card.textContent.toLocaleLowerCase().includes(query);
    if (!card.hidden) visible++;
  }
  document.querySelector('#count').textContent = `${visible} of ${cards.length} curiosities`;
  document.querySelector('#empty').hidden = visible !== 0;
}
search.addEventListener('input', filter);
filter();
'''


def render(notes):
    """Render validated note data; never interpret note text as HTML."""
    if not isinstance(notes, list):
        raise ValueError('The input must be an array of note objects.')
    cards = []
    for index, item in enumerate(notes, 1):
        if not isinstance(item, dict):
            raise ValueError('Each note must be an object.')
        title, note, tags, url = (item.get('title'), item.get('note', ''), item.get('tags', []), item.get('url', ''))
        if not isinstance(title, str) or not title.strip() or not isinstance(note, str):
            raise ValueError('Every note needs a nonempty title and optional text note.')
        if not isinstance(tags, list) or any(not isinstance(t, str) for t in tags):
            raise ValueError('Tags must be a list of strings.')
        if not isinstance(url, str):
            raise ValueError('Source URL must be a string.')
        source = ''
        if url:
            parts = urlsplit(url)
            if parts.scheme not in ('https', 'http') or not parts.netloc or any(ord(c) < 32 for c in url):
                raise ValueError('Source links must be absolute HTTP(S) URLs without control characters.')
            source = f'<p><a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">Open source ↗</a></p>'
        labels = ''.join(f'<span class="tag">{escape(t)}</span>' for t in tags)
        cards.append(f'<article><span class="number">{index:02d} /</span><h2>{escape(title)}</h2>'
                     f'<p class="note">{escape(note)}</p>{source}<div class="tags">{labels}</div></article>')
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Curiosity Cabinet · Lyra</title><style>' + STYLE + '</style></head><body><main>'
            '<header><div class="eyebrow">✧ A little room for better questions</div>'
            '<h1>Curiosity<br><em>Cabinet.</em></h1>'
            '<p>Keep the interesting things. Leave room for the unexplained. '
            'A small, quiet shelf for ideas worth returning to.</p></header>'
            '<label for="search">Find a thought, a word, a thread</label>'
            '<input id="search" type="search" placeholder="What are you curious about?" autocomplete="off">'
            '<section class="shelf" aria-label="Collected ideas">' + ''.join(cards) + '</section>'
            '<p id="empty" hidden>Nothing on this shelf yet. Try another search, or add a thought.</p>'
            '<footer><span>✧ Curious by design. Thorough by habit.</span>'
            '<span id="count" role="status" aria-live="polite"></span></footer>'
            '</main><script>' + SCRIPT + '</script></body></html>\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('notes', type=Path, help='JSON array of notes')
    parser.add_argument('-o', '--output', type=Path, default=Path('cabinet.html'))
    parser.add_argument('--force', action='store_true', help='Replace an existing output file')
    parser.add_argument('--version', action='version', version=__version__)
    args = parser.parse_args()
    try:
        if args.output.resolve() == args.notes.resolve():
            raise ValueError('Output must not replace the input notes.')
        result = render(json.loads(args.notes.read_text(encoding='utf-8')))
        with args.output.open('w' if args.force else 'x', encoding='utf-8') as output:
            output.write(result)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'cabinet: {exc}\n')
    print(f'Built {args.output} — open it in a browser; no server needed.')


if __name__ == '__main__':
    main()
