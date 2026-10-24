"""Self-hosted WOFF2 subsets of the three brand faces.

python -I tools/fonts.py   (from the project root; sources in research/font-src, gitignored)

Schibsted Grotesk (Bakken & Baeck for the Schibsted newspapers, OFL) sets the voice:
headlines, reading, navigation. Its tabular and slashed-zero figures set the board.
Azeret Mono (Displaay, OFL) sets the instruments: sources, timestamps, codes, labels.
Handjet (Rosetta, OFL) sets the big readings. Every letter is built from modular
elements; with ELSH at 15 the elements are diamonds, so a count is drawn in knots.
ELSH is kept between 12 (crossed threads) and 15 (knots) so a knot can be cut.
"""
import io
import os
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src')
OUT = os.path.join(ROOT, 'assets', 'fonts')
os.makedirs(OUT, exist_ok=True)

# Basic Latin + Latin-1 + Latin Extended-A, typographic punctuation, arrows,
# the minus, multiplication and approximately-equal signs.
TEXT = (
    list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) +
    [0x2009, 0x200A, 0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022,
     0x2026, 0x2030, 0x2032, 0x2033, 0x2039, 0x203A, 0x2044, 0x20AC, 0x2116, 0x2190, 0x2191, 0x2192,
     0x2193, 0x2197, 0x2198, 0x2212, 0x2248, 0x2260, 0x2264, 0x2265, 0x00D7, 0x00B0, 0x00B7]
)
# Handjet: figures and the signs a reading needs, capitals for codes, and the Arabic
# letters of شبكة (net, network), عقدة (knot) and فلسطين أونلاين.
KNOTS = (
    list(range(0x20, 0x7F)) + [0x00A0, 0x00B7, 0x00D7, 0x2013, 0x2014, 0x2019, 0x2212, 0x2248, 0x2026, 0x20AC, 0x2011] +
    [ord(c) for c in 'شبكةعقدفلسطينأوا']
)

# Beiruti (Boutros, OFL) for the few Arabic words in running text, where Handjet's knots
# would be too small to read: the Arabic letters, Arabic-Indic digits and marks.
ARABIC = list(range(0x0600, 0x0700)) + [0x20, 0xA0, 0x200C, 0x200D, 0x200E, 0x200F, 0x2D, 0x2E, 0x2C, 0x3A]

JOBS = [
    # (source, out, axis limits, unicodes)
    ('schibstedgrotesk-SchibstedGrotesk[wght].ttf', 'schibsted.woff2', {'wght': (400, 900)}, TEXT),
    ('schibstedgrotesk-SchibstedGrotesk-Italic[wght].ttf', 'schibsted-italic.woff2', {'wght': (400, 700)}, TEXT),
    ('azeretmono-AzeretMono[wght].ttf', 'azeret-mono.woff2', {'wght': (300, 700)}, TEXT),
    ('handjet-Handjet[ELGR,ELSH,wght].ttf', 'handjet.woff2', {'wght': (300, 800), 'ELSH': (12, 15), 'ELGR': 1}, KNOTS),
    ('beiruti-Beiruti[wght].ttf', 'beiruti.woff2', {'wght': (400, 800)}, ARABIC),
]


def options():
    o = subset.Options()
    o.flavor = 'woff2'
    o.layout_features = ['*']
    o.name_IDs = ['*']
    o.name_languages = ['*']
    o.notdef_outline = True
    o.glyph_names = False
    o.hinting = False
    o.desubroutinize = True
    return o


for src, out, limits, unicodes in JOBS:
    font = TTFont(os.path.join(SRC, src))
    font = instancer.instantiateVariableFont(font, limits)
    buf = io.BytesIO()
    font.save(buf)  # round-trip so the partial instance subsets cleanly
    buf.seek(0)
    font = TTFont(buf)
    sub = subset.Subsetter(options())
    sub.populate(unicodes=unicodes)
    sub.subset(font)
    path = os.path.join(OUT, out)
    subset.save_font(font, path, options())
    print(out, os.path.getsize(path) // 1024, 'KB')

for name, lic in (('SchibstedGrotesk', 'schibstedgrotesk-OFL.txt'), ('AzeretMono', 'azeretmono-OFL.txt'),
                  ('Handjet', 'handjet-OFL.txt'), ('Beiruti', 'beiruti-OFL.txt')):
    with open(os.path.join(SRC, lic), encoding='utf-8') as f, \
            open(os.path.join(OUT, f'OFL-{name}.txt'), 'w', encoding='utf-8') as g:
        g.write(f.read())
