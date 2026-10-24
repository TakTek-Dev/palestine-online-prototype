"""Shared chrome and drawing helpers for every Palestine Online page.

Pages are static HTML written by tools/build.py (home), tools/pages.py (inner pages) and
tools/book.py (the identity book). Never hand-edit the HTML they write.
"""
import html
import json
import math
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = '1'                      # asset version: bump on any CSS/JS/font change
SITE = 'https://taktek-dev.github.io/palestine-online-prototype/'
NAME = 'Palestine Online'
LINE = 'Press & network status'

MARKS = json.load(open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), encoding='utf-8'))

NAV = [
    ('board', 'Board', 'home.html#board'),
    ('networks', 'Networks', 'networks.html'),
    ('press', 'Press safety', 'press.html'),
    ('speech', 'Speech & evidence', 'speech.html'),
    ('platforms', 'Platforms', 'platforms.html'),
    ('creators', 'Creators', 'creators.html'),
    ('method', 'Method', 'method.html'),
]

STATUS = {
    # key: (label, family)  family drives colour; the glyph comes from the net
    'down': ('Down', 'down'),
    'degraded': ('Degraded', 'deg'),
    'steady': ('Steady', 'up'),
    'restored': ('Restored', 'sea'),
    'incident': ('Incident', 'down'),
    'pattern': ('Pattern', 'deg'),
    'open': ('Open', 'sea'),
    'stalled': ('Stalled', 'mute'),
    'resolved': ('Resolved', 'up'),
    'recognised': ('Recognised', 'sea'),
}

MONTHS = 'January February March April May June July August September October November December'.split()


def esc(s):
    return html.escape(str(s), quote=True)


def d(iso):
    return date.fromisoformat(iso)


def day_short(iso):
    x = d(iso)
    return f'{x.day} {MONTHS[x.month - 1][:3]}'


def day_long(iso):
    x = d(iso)
    return f'{x.strftime("%A")} {x.day} {MONTHS[x.month - 1]} {x.year}'


def day_mid(iso):
    x = d(iso)
    return f'{x.strftime("%a")} {x.day} {MONTHS[x.month - 1][:3]}'


def day_full(iso):
    x = d(iso)
    return f'{x.day} {MONTHS[x.month - 1][:3]} {x.year}'


# ---------------------------------------------------------------- net glyphs
# Every status is drawn from the same net, and no two share a silhouette:
# a cell that holds (four knots), sags, tears open or is mended (one knot on the side);
# one knot for an event, a run of knots for a pattern, a loose end for an open case,
# two paused threads, a thread tied at both ends, a lit knot in the ring of its reply.

def _knot(x, y, r=1.5, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<path{c} d="M{x} {y - r}L{x + r} {y}L{x} {y + r}L{x - r} {y}Z"/>'


def glyph(status, cls='gl'):
    """A 16 px status glyph in currentColor."""
    D = 5.4
    cell = f'M0 {-D}L{D} 0L0 {D}L{-D} 0Z'
    if status == 'steady':
        body = f'<path d="{cell}" class="t"/>' + ''.join(_knot(x, y) for x, y in ((0, -D), (D, 0), (0, D), (-D, 0)))
    elif status == 'degraded':
        # the cell sags: the top holds, the bottom hangs slack, the side knots are working loose
        body = (f'<path d="M{-D} 0L0 {-D}L{D} 0Q0 {D * 1.9} {-D} 0" class="t"/>' + _knot(0, -D)
                + _knot(D, 0, 1.4, 'o') + _knot(-D, 0, 1.4, 'o'))
    elif status == 'down':
        # torn open: the top holds, the lower threads hang loose and never meet
        body = (f'<path d="M{-D} 0L0 {-D}L{D} 0M{-D} 0L-2.6 2.8M{D} 0L2.6 2.8" class="t"/>'
                '<path d="M-2.6 2.8L-2.1 4.2M-2.6 2.8L-3.4 4.1M2.6 2.8L2.1 4.2M2.6 2.8L3.4 4.1" class="f"/>')
    elif status == 'restored':
        # mended: the cell closes again around one new knot on its torn side
        body = (f'<path d="M{D} 0L0 {-D}L{-D} 0L0 {D}L1.5 3.9M3.9 1.5L{D} 0" class="t"/>' + _knot(2.7, 2.7, 1.9, 'm'))
    elif status == 'incident':
        body = '<path d="M-5.2 -5.2L5.2 5.2M5.2 -5.2L-5.2 5.2" class="t"/>' + _knot(0, 0, 2.9)
    elif status == 'pattern':
        body = '<path d="M-7 0H7" class="t"/>' + ''.join(_knot(x, 0, 2.1) for x in (-4.8, 0, 4.8))
    elif status == 'open':
        # a loose end: a thread from a knot, frayed where it was cut
        body = ('<path d="M-5.5 0H3.2" class="t"/><path d="M3.2 0L6.4 -2.2M3.2 0L6.6 0.4M3.2 0L5.8 2.6" class="f"/>'
                + _knot(-5.4, 0, 2.4))
    elif status == 'stalled':
        body = '<path d="M-2.4 -5.6V5.6M2.4 -5.6V5.6" class="t w"/>'
    elif status == 'resolved':
        # a thread tied off at both ends
        body = '<path d="M-4.4 0Q0 -3.4 4.4 0" class="t"/>' + _knot(-5, 0.6, 2.3) + _knot(5, 0.6, 2.3)
    elif status == 'recognised':
        # a lit knot inside the ring of its reply
        body = '<circle r="5.6" class="t"/>' + _knot(0, 0, 2.6, 'm')
    else:
        body = ''
    return f'<svg class="{cls}" viewBox="-8 -8 16 16" aria-hidden="true" focusable="false">{body}</svg>'


def chip(status, text=None, cls=''):
    label, fam = STATUS[status]
    return (f'<span class="st st-{fam} st-{status}{(" " + cls) if cls else ""}">'
            f'{glyph(status)}<span>{esc(text or label)}</span></span>')


def mark_svg(cls='mark', lit=True, title=None):
    """The net cell mark as inline SVG, coloured by CSS (.th threads, .kn knots, .lit)."""
    G, L, W, K = MARKS['G'], MARKS['L'], MARKS['W'], MARKS['K']
    E = MARKS['E']
    lines = ''.join(f'M{p:.2f} {-L:.2f}V{L:.2f}M{-L:.2f} {p:.2f}H{L:.2f}' for p in (-G, G))
    kn = ''
    for i, (x, y) in enumerate(((-G, -G), (G, -G), (-G, G), (G, G))):
        c = 'kn lit' if (i == 0 and lit) else 'kn'
        kn += f'<rect class="{c}" x="{x - K / 2:.2f}" y="{y - K / 2:.2f}" width="{K}" height="{K}"/>'
    t = f'<title>{esc(title)}</title>' if title else ''
    aria = f'role="img" aria-label="{esc(title)}"' if title else 'aria-hidden="true" focusable="false"'
    return (f'<svg class="{cls}" viewBox="{-E:.2f} {-E:.2f} {2 * E:.2f} {2 * E:.2f}" {aria}>{t}'
            f'<g transform="rotate(45)"><path class="th" d="{lines}" stroke-width="{W}"/>{kn}</g></svg>')


def word_svg(cls='word'):
    adv, cap = MARKS['advance'], MARKS['cap']
    return (f'<svg class="{cls}" viewBox="0 {-cap * 1.02:.1f} {adv:.1f} {cap * 1.36:.1f}" aria-hidden="true" '
            f'focusable="false"><path d="{MARKS["word"]}"/></svg>')


def brand(rel, cls='brand', sub=True, tag='a'):
    inner = (f'{mark_svg()}<span class="brand-t">{word_svg()}<span class="sr">{NAME}</span>'
             + (f'<span class="brand-s">{esc(LINE)}</span>' if sub else '') + '</span>')
    if tag == 'a':
        return f'<a class="{cls}" href="{rel}home.html" aria-label="{NAME}, home">{inner}</a>'
    return f'<div class="{cls}">{inner}</div>'


# ---------------------------------------------------------------- sparks
def spark(values, ref=None, status='steady', w=300, h=44, label=''):
    """Daily bars with the pre-war level as a thread across them."""
    if not values:
        return ''
    top = max(max(values), ref or 0) * 1.08 or 1
    n = len(values)
    gap = 2
    bw = (w - gap * (n - 1)) / n
    bars = ''
    for i, v in enumerate(values):
        bh = max(1.2, v / top * h)
        bars += (f'<rect x="{i * (bw + gap):.2f}" y="{h - bh:.2f}" width="{bw:.2f}" height="{bh:.2f}" '
                 f'style="--i:{i}"/>')
    line = ''
    if ref:
        y = h - ref / top * h
        line = f'<line class="ref" x1="0" x2="{w}" y1="{y:.2f}" y2="{y:.2f}"/>'
    fam = STATUS.get(status, ('', 'up'))[1]
    return (f'<svg class="spark sp-{fam}" viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img" '
            f'aria-label="{esc(label)}">{bars}{line}</svg>')


# ---------------------------------------------------------------- chrome
def head(title, desc, rel='', path='home.html', body_cls='', og=None, extra=''):
    full = title if title.startswith(NAME) else f'{title} · {NAME}'
    og = og or f'{SITE}assets/og.png'
    return f'''<!doctype html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(full)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#F4F2EB" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0F1012" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(full)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{rel}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{rel}apple-touch-icon.png">
<link rel="manifest" href="{rel}manifest.webmanifest">
<link rel="preload" href="{rel}assets/fonts/schibsted.woff2?v={V}" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{rel}assets/fonts/handjet.woff2?v={V}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{rel}assets/css/po.css?v={V}">
<script>(function(h){{h.classList.add('js');try{{var t=localStorage.getItem('po-theme');if(t)h.dataset.theme=t}}catch(e){{}}
try{{var f=/[?&]loader\\b/.test(location.search);if(f||(!sessionStorage.getItem('po-cast')&&!document.hidden&&!matchMedia('(prefers-reduced-motion: reduce)').matches))h.classList.add('js-loading')}}catch(e){{}}}})(document.documentElement)</script>
{extra}</head>
<body class="{body_cls}">
<a class="skip" href="#main">Skip to content</a>
'''


def loader():
    """The first-visit loader: a hash sign turns into a net cell, the net is cast, one knot answers."""
    return f'''<div class="loader" id="loader" aria-hidden="true">
<div class="ld-stage"><svg class="ld-net" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid slice"></svg>
{mark_svg('ld-mark')}<p class="ld-word"><span class="kn-ar" lang="ar" dir="rtl">شبكة</span><span>net · network</span></p></div>
</div>
'''


def strip(ed, rel=''):
    return f'''<div class="strip" role="region" aria-label="Board status"><div class="wrap">
<p class="live"><span class="pulse" aria-hidden="true"></span><span class="hide-s">Board read</span><span class="d-s">Read</span><b>{esc(ed["read_utc"])} UTC</b><span class="hide-s">·&nbsp;{esc(ed["read_local"])} in Gaza</span></p>
<p class="r"><span class="d-l">{esc(day_long(ed["date"]))}</span><span class="d-s">{esc(day_mid(ed["date"]))}</span><a class="hide-s" href="{rel}method.html">Method &amp; corrections</a><a class="hide-s" href="{rel}report.html">Report an outage</a></p>
</div></div>
'''


def mast(rel='', active='board'):
    items = ''.join(
        f'<li><a href="{rel}{href}"{" aria-current=\"page\"" if key == active else ""}>{esc(label)}</a></li>'
        for key, label, href in NAV)
    return f'''<header class="mast"><div class="wrap">
{brand(rel)}
<nav class="nav" aria-label="Sections"><ul>{items}</ul><span class="cue" aria-hidden="true"></span></nav>
<div class="tools">
<a class="icon-btn" href="{rel}search.html" aria-label="Search"><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.5" cy="8.5" r="5.6"/><path d="M12.6 12.6L17 17"/></svg></a>
<button class="icon-btn theme" type="button" aria-label="Switch to night" data-theme-toggle><svg viewBox="0 0 20 20" aria-hidden="true"><path class="sun" d="M10 3v2M10 15v2M3 10h2M15 10h2M5 5l1.4 1.4M13.6 13.6L15 15M5 15l1.4-1.4M13.6 6.4L15 5"/><circle class="sun" cx="10" cy="10" r="3.2"/><path class="moon" d="M14.8 12.6A6 6 0 0 1 7.4 5.2a6 6 0 1 0 7.4 7.4z"/></svg></button>
<a class="btn" href="{rel}alerts.html" aria-label="Status alerts">{mark_svg("mark b-mark", lit=False)}<span>Status alerts</span></a>
</div>
</div></header>
'''


def foot(rel=''):
    cols = [
        ('Board', [('Networks', 'networks.html'), ('Press safety', 'press.html'), ('Speech & evidence', 'speech.html'),
                   ('Platforms', 'platforms.html'), ('Creators', 'creators.html')]),
        ('Desk', [('Method', 'method.html'), ('Corrections', 'method.html#corrections'), ('Report an outage', 'report.html'),
                  ('Status alerts', 'alerts.html')]),
        ('About', [('Who we are', 'about.html'), ('Archive', 'archive.html'), ('Search', 'search.html'),
                   ('Identity book', 'index.html'), ('Privacy', 'privacy.html')]),
    ]
    c = ''.join(f'<div><h2>{esc(h)}</h2><ul>' + ''.join(f'<li><a href="{rel}{u}">{esc(t)}</a></li>' for t, u in links)
                + '</ul></div>' for h, links in cols)
    return f'''<footer class="foot">
<div class="selvage" aria-hidden="true"></div>
<div class="wrap">
<div class="f-top">{brand(rel, 'brand f-brand')}<p class="f-say">One word in Arabic, <span lang="ar">شبكة</span>, means a fishing net and a phone network. We report where Palestine's holds and where it is torn.</p></div>
<div class="f-cols">{c}</div>
<div class="f-bot"><p>© 2026 {NAME} · palestineonline.co · Prototype by TakTek</p><p>Network data: IODA, Georgia Tech · Photos: Wikimedia Commons, credited on each picture</p></div>
</div>
</footer>
'''


def scripts(rel='', extra=()):
    s = f'<script src="{rel}assets/js/po.js?v={V}" defer></script>\n'
    for e in extra:
        s += f'<script src="{rel}assets/js/{e}?v={V}" defer></script>\n'
    return s + '</body>\n</html>\n'


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
