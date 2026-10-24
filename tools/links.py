"""Check every internal link and asset reference in the built pages.

python -I tools/links.py   -> lists broken targets and missing #anchors, exits 1 if any
"""
import glob
import os
import re
import sys
from urllib.parse import unquote, urldefrag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://taktek-dev.github.io/palestine-online-prototype/'
pages = [p for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)
         if os.sep + 'research' + os.sep not in p and os.sep + 'tools' + os.sep not in p]
ids = {}
for p in pages:
    ids[os.path.normpath(p)] = set(re.findall(r'\sid="([^"]+)"', open(p, encoding='utf-8').read()))

bad = []
for p in pages:
    html = open(p, encoding='utf-8').read()
    for ref in re.findall(r'(?:href|src)="([^"]+)"', html):
        if ref.startswith(BASE):
            ref = os.path.relpath(os.path.join(ROOT, ref[len(BASE):]), os.path.dirname(p)).replace(os.sep, '/')
        if re.match(r'^(https?:|mailto:|tel:|data:|javascript:)', ref) or ref == '#':
            continue
        path, frag = urldefrag(ref)
        path = path.split('?')[0]
        target = os.path.normpath(os.path.join(os.path.dirname(p), unquote(path))) if path else os.path.normpath(p)
        if not os.path.exists(target):
            bad.append((os.path.relpath(p, ROOT), ref, 'missing file'))
        elif frag and target.endswith('.html') and frag not in ids.get(target, set()):
            bad.append((os.path.relpath(p, ROOT), ref, 'missing #' + frag))

for b in sorted(set(bad)):
    print(*b, sep='  |  ')
print(len(pages), 'pages,', len(set(bad)), 'broken')
sys.exit(1 if bad else 0)
