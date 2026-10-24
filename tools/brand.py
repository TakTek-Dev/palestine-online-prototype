"""The Palestine Online marks, drawn from one net cell.

python -I tools/brand.py   -> assets/brand/*.svg, favicon.svg, tools/out/marks.json

شبكة (shabaka) is one Arabic word for a fishing net and for a phone or internet network.
The keffiyeh carries the fisherman's net; a phone in Gaza searches for the other one.
The mark is a hash sign turned 45 degrees: two threads each way cross in four knots and
leave eight cut ends, so the sign of online speech becomes a cell of the net. The knot at
the top is the one that answers, in sea blue.

The wordmark is set in Schibsted Grotesk 780 and outlined here, so the SVGs need no font.
"""
import io
import json
import math
import os
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'brand')
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(ROOT, 'tools', 'out'), exist_ok=True)

COTTON, THREAD, SEA = '#F4F2EB', '#121315', '#0D5BA1'
NIGHT, NIGHT_SEA = '#0F1012', '#6AB0F2'

# Cell geometry in a 100-unit box, before the 45 degree turn: threads at +-G, running to +-L.
G, STUB, W, K = 17.0, 11.0, 5.6, 10.4
L = G + STUB


def cell(ink, sea, lit=(0,), knots=True, x=0, y=0, size=100):
    """One net cell as SVG elements in a box of `size` at (x, y)."""
    s = size / 100
    lines = ''.join(
        f'<path d="M{p:.2f} {-L:.2f}V{L:.2f}M{-L:.2f} {p:.2f}H{L:.2f}"/>' for p in (-G, G))
    kn = ''
    if knots:
        for i, (kx, ky) in enumerate(((-G, -G), (G, -G), (-G, G), (G, G))):
            fill = sea if i in lit else ink
            kn += f'<rect x="{kx - K / 2:.2f}" y="{ky - K / 2:.2f}" width="{K}" height="{K}" fill="{fill}"/>'
    return (f'<g transform="translate({x + 50 * s:.2f} {y + 50 * s:.2f}) scale({s:.4f}) rotate(45)">'
            f'<g fill="none" stroke="{ink}" stroke-width="{W}">{lines}</g>{kn}</g>')


def extent():
    """Half-size of the turned cell's bounding box (thread ends reach furthest)."""
    # a thread end at (G, L) turned 45 degrees, plus half the stroke
    return (G + L) / math.sqrt(2) + W / 2 / math.sqrt(2)


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" width="{w:.0f}" height="{h:.0f}" '
            f'role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n')


def write(name, text):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


# ---- the wordmark, outlined from the variable font
SRC = os.path.join(ROOT, 'research', 'font-src', 'schibstedgrotesk-SchibstedGrotesk[wght].ttf')
font = instancer.instantiateVariableFont(TTFont(SRC), {'wght': 780})
buf = io.BytesIO(); font.save(buf); buf.seek(0); font = TTFont(buf)
upm = font['head'].unitsPerEm
cmap, gs, hmtx = font.getBestCmap(), font.getGlyphSet(), font['hmtx']
kern = {}
if 'GPOS' in font:
    pass  # Schibsted's pair kerning is applied by browsers; for the outline we track by hand


def outline(text, size, track=-0.032):
    """Path data for text at `size` px, baseline at y=0, plus its advance width."""
    pen = SVGPathPen(gs)
    x = 0.0
    scale = size / upm
    for ch in text:
        g = cmap[ord(ch)]
        if ch != ' ':
            tp = TransformPen(pen, (scale, 0, 0, -scale, x, 0))
            gs[g].draw(tp)
        x += hmtx[g][0] * scale + track * size
    return pen.getCommands(), x - track * size


CAP = font['OS/2'].sCapHeight / upm
WORD = 'Palestine Online'
SIZE = 100
d, adv = outline(WORD, SIZE)
cap = CAP * SIZE

# ---- files
E = extent()                      # half-size of the mark at size 100
mark_box = 2 * E


def mark_file(ink, sea, bg=None, pad=0):
    size = 100
    w = mark_box + 2 * pad
    inner = cell(ink, sea, x=pad + E - 50, y=pad + E - 50, size=size)
    rect = f'<rect width="{w:.2f}" height="{w:.2f}" fill="{bg}"/>' if bg else ''
    return svg(w, w, rect + inner, 'Palestine Online')


write('mark.svg', mark_file(THREAD, SEA))
write('mark-night.svg', mark_file(COTTON, NIGHT_SEA))
write('mark-one.svg', mark_file(THREAD, THREAD))
write('avatar.svg', mark_file(COTTON, NIGHT_SEA, bg=THREAD, pad=46))
write('avatar-cotton.svg', mark_file(THREAD, SEA, bg=COTTON, pad=46))

# the lockup: mark as tall as the cap height times 1.9, centred on the x-height band
def lockup(ink, sea, sub):
    mh = cap * 1.95                       # rendered mark height
    s = mh / mark_box * 100               # cell size that gives that height
    gap = cap * 0.62
    ox = 0
    mark = cell(ink, sea, x=ox + mh / 2 - s / 2, y=-cap / 2 - s / 2, size=s)
    tx = mh + gap
    body = mark + f'<path transform="translate({tx:.2f} 0)" fill="{ink}" d="{d}"/>'
    w = tx + adv
    top = -max(mh / 2 + cap / 2, cap) - 2
    h = mh + 4
    y0 = -cap / 2 - mh / 2 - 2
    return svg(w, h, f'<g transform="translate(0 {-y0:.2f})">{body}</g>', 'Palestine Online')


write('lockup.svg', lockup(THREAD, SEA, True))
write('lockup-night.svg', lockup(COTTON, NIGHT_SEA, True))
write('wordmark.svg', svg(adv, cap * 1.36, f'<path transform="translate(0 {cap * 1.02:.2f})" fill="{THREAD}" d="{d}"/>',
                          'Palestine Online'))

# favicon follows the reader's scheme
fav = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {mark_box:.2f} {mark_box:.2f}">'
       f'<style>.i{{stroke:{THREAD}}}.k{{fill:{THREAD}}}.s{{fill:{SEA}}}'
       f'@media (prefers-color-scheme:dark){{.i{{stroke:{COTTON}}}.k{{fill:{COTTON}}}.s{{fill:{NIGHT_SEA}}}}}</style>'
       + cell('currentColor', 'currentColor', x=E - 50, y=E - 50)
       .replace('stroke="currentColor"', 'class="i"')
       .replace('fill="currentColor"', 'class="k"', 3)
       .replace('fill="currentColor"', 'class="k"') + '</svg>\n')
# first knot is the lit one: give it the sea class
fav = fav.replace('class="k"', 'class="s"', 1)
with open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8', newline='\n') as f:
    f.write(fav)

json.dump({'G': G, 'L': L, 'W': W, 'K': K, 'E': E, 'word': d, 'advance': adv, 'cap': cap},
          open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), 'w', encoding='utf-8'))
print('mark box', round(mark_box, 2), 'word', round(adv, 1), 'cap', round(cap, 1))
