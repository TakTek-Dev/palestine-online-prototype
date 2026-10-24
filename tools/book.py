"""The identity book: index.html, the first page a client opens.

python -I tools/book.py   (after brand.py, build.py and pages.py)
"""
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # noqa: E402
from common import (MARKS, NAME, ROOT, SITE, STATUS, V, brand, chip, esc, glyph, mark_svg, spark, word_svg,  # noqa: E402
                    write)
from net import net_svg  # noqa: E402

ED = B.ED
G, L, W, K, E = MARKS['G'], MARKS['L'], MARKS['W'], MARKS['K'], MARKS['E']


def hexrgb(h):
    h = h.lstrip('#')
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def lum(h):
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in hexrgb(h)]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------------------------------------------------------------- construction drawing
def construction():
    """Four steps from a hash sign to the mark, drawn on the same 100-unit grid."""
    def step(rot, knots, lit, label, n):
        lines = ''.join(f'M{p} {-L}V{L}M{-L} {p}H{L}' for p in (-G, G))
        kn = ''
        if knots:
            for i, (x, y) in enumerate(((-G, -G), (G, -G), (-G, G), (G, G))):
                c = 'kl' if (i == 0 and lit) else 'kk'
                kn += f'<rect class="{c}" x="{x - K / 2}" y="{y - K / 2}" width="{K}" height="{K}"/>'
        guide = ('<g class="gd"><circle r="47"/><path d="M-50 0H50M0 -50V50"/></g>')
        return (f'<figure class="cs"><svg viewBox="-52 -52 104 104" aria-hidden="true">{guide}'
                f'<g transform="rotate({rot})"><path class="tt" d="{lines}" stroke-width="{W}"/>{kn}</g></svg>'
                f'<figcaption><b>{n}</b>{label}</figcaption></figure>')
    return ('<div class="cs-row">'
            + step(0, False, False, 'A hash sign: the mark of a post, a tag, a voice online.', '1')
            + step(45, False, False, 'Turned forty-five degrees, it becomes one cell of a net.', '2')
            + step(45, True, False, 'Where the threads cross, they are knotted.', '3')
            + step(45, True, True, 'The top knot answers, in sea blue. That is the mark.', '4')
            + '</div>')


def spec_drawing():
    lines = ''.join(f'M{p} {-L}V{L}M{-L} {p}H{L}' for p in (-G, G))
    kn = ''.join(f'<rect class="{"kl" if i == 0 else "kk"}" x="{x - K / 2}" y="{y - K / 2}" width="{K}" height="{K}"/>'
                 for i, (x, y) in enumerate(((-G, -G), (G, -G), (-G, G), (G, G))))
    dim = lambda x1, y1, x2, y2, t, tx, ty, a='': (f'<path class="dm" d="M{x1} {y1}L{x2} {y2}"/>'  # noqa: E731
                                                   f'<text class="{a}" x="{tx}" y="{ty}">{t}</text>')
    return f'''<svg class="spec" viewBox="-62 -50 124 100" aria-label="Construction of the mark on a 100-unit square">
<g class="gd"><rect x="-50" y="-50" width="100" height="100"/><path d="M-50 0H50M0 -50V50"/></g>
<g><path class="tt" d="{lines}" stroke-width="{W}"/>{kn}</g>
{dim(-G, -40, G, -40, f'2 × {G:g} between threads', 0, -43)}
{dim(G, 38, L, 38, f'{L - G:g} cut end', (G + L) / 2, 45)}
{dim(L + 3, -G - W / 2, L + 3, -G + W / 2, f'thread {W:g}', L + 5, -G + 1.2, 'l')}
{dim(-L - 3, G - K / 2, -L - 3, G + K / 2, f'knot {K:g}', -L - 5, G + 1.2, 'r')}
</svg>'''


# ---------------------------------------------------------------- chapters
def swatch(name, hexv, role, on=None, light_text=False):
    on = on or ('#F4F2EB' if lum(hexv) < .25 else '#121315')
    r = ratio(hexv, '#F4F2EB')
    r2 = ratio(hexv, '#121315')
    return (f'<li class="sw" style="--c:{hexv};--on:{on}"><span class="sw-chip"><b>{esc(name)}</b><code>{hexv}</code></span>'
            f'<span class="sw-role">{esc(role)}</span><span class="sw-ratio">{r:.1f}:1 on cotton · {r2:.1f}:1 on thread</span></li>')


def chapter(n, cid, title, intro, body, cls=''):
    return (f'<section class="ch {cls}" id="{cid}" aria-labelledby="{cid}-h"><header class="ch-h"><p class="ch-n">{n:02d}</p>'
            f'<h2 id="{cid}-h">{esc(title)}</h2><p class="ch-i">{intro}</p></header>{body}</section>')


def main():
    n = ED['lead']['net']
    photos = B.PHOTOS
    brand_ph = [p for p in ('nets-gaza', 'keffiyeh-net', 'hirbawi') if p in photos]

    caps = json.load(open(os.path.join(ROOT, 'tools', 'photos.json'), encoding='utf-8'))

    def ph(slug, cap=''):
        if slug not in photos:
            return ''
        cap = cap or caps.get(slug, {}).get('caption', '')
        m = photos[slug]
        return (f'<figure class="bk-ph"><img src="assets/img/photo/{slug}.webp" width="{m["w"]}" height="{m["h"]}" alt="" '
                f'loading="lazy"><figcaption>{esc(cap)}</figcaption></figure>')

    chapters = []
    chapters.append(chapter(1, 'word', 'One word, two nets',
        'In Arabic, <span lang="ar">شبكة</span> (shabaka) is a fishing net and it is a phone or internet network. '
        'In Gaza, when the signal goes, people say there is no shabaka. The keffiyeh carries the fisherman\'s net in its weave. '
        'Palestine Online is built from that one word.',
        f'''<div class="word-hero"><p class="kn-ar" lang="ar" dir="rtl">شبكة</p>
<dl class="two-nets"><div><dt>The net</dt><dd>Threads crossed and knotted at every crossing. It holds because every knot holds its neighbours. Torn, it lets things through.</dd></div>
<div><dt>The network</dt><dd>Addresses joined by routes. It holds while the routes are carried. Cut, a place drops off the map of the internet.</dd></div></dl></div>
<div class="word-ph">{ph("nets-gaza")}<div class="word-ph2">{ph("hirbawi")}{ph("keffiyeh-net")}</div></div>'''))

    chapters.append(chapter(2, 'mark', 'The mark',
        'A hash sign is how a voice is tagged online. Turn it forty-five degrees and it is a cell of the net: two threads '
        'each way, four knots, eight cut ends. The knot at the top is the one that answers.',
        construction() + f'''<div class="mk-spec">{spec_drawing()}
<div class="mk-notes"><h3>Geometry</h3><p>Drawn on a 100-unit square before the turn. Threads sit {G:g} units either side of the centre and run {L - G:g} units past the knots. A thread is {W:g} units; a knot, {K:g}. The cut ends are the mark's edge: its clear space is one cut end on every side.</p>
<h3>Sizes</h3><p>The mark alone holds down to 16 pixels; the favicon is drawn at that size. With the name, keep the mark at least 24 pixels tall.</p>
<h3>The lit knot</h3><p>Only the top knot changes colour, and only to sea blue. Everything else is thread: ink on cotton, cotton on night.</p></div></div>'''))

    lock = f'''<div class="lk-grid">
<figure class="lk lk-cotton">{brand('', 'brand lk-brand', tag='div')}<figcaption>Lockup on cotton</figcaption></figure>
<figure class="lk lk-night">{brand('', 'brand lk-brand', tag='div')}<figcaption>Lockup on night</figcaption></figure>
<figure class="lk lk-sea"><div class="brand lk-brand">{mark_svg('mark', lit=False)}<span class="brand-t">{word_svg()}<span class="brand-s">Press &amp; network status</span></span></div><figcaption>On sea, the lit knot turns thread</figcaption></figure>
<figure class="lk lk-sq"><img src="assets/brand/avatar.svg" alt="" width="120" height="120"><img src="assets/brand/avatar-cotton.svg" alt="" width="120" height="120"><figcaption>Avatars, night and cotton</figcaption></figure>
</div>
<ul class="donts">
<li><span class="dn"><svg viewBox="-36 -36 72 72"><g><path class="tt" d="{''.join(f'M{p} {-L}V{L}M{-L} {p}H{L}' for p in (-G, G))}" stroke-width="{W}"/></g></svg></span><b>Don't turn it back</b>Upright, it is only a hash sign.</li>
<li><span class="dn">{mark_svg('mark dn-all', lit=True)}</span><b>Don't light every knot</b>One knot answers. That is the point.</li>
<li><span class="dn dn-stretch">{mark_svg('mark')}</span><b>Don't stretch it</b>The cell is square before it is turned.</li>
<li><span class="dn dn-red">{mark_svg('mark')}</span><b>Don't colour it by status</b>The mark is not a status. The board has its own glyphs.</li>
</ul>'''
    chapters.append(chapter(3, 'lockups', 'Lockups', 'The name is set in Schibsted Grotesk at weight 780 and outlined, with the line beneath in Azeret Mono. The mark is twice the cap height and centred on it.', lock))

    sw = ''.join([
        swatch('Cotton', '#F4F2EB', 'The page. The keffiyeh\'s cloth.'),
        swatch('Cloth', '#FCFBF7', 'Panels and the board.'),
        swatch('Thread', '#121315', 'Ink, the net, the name.'),
        swatch('Thread 2', '#383B40', 'Secondary text.'),
        swatch('Mute', '#5C6066', 'Labels, sources, times.'),
        swatch('Sea', '#0D5BA1', 'The knot that answers; links and the one button.'),
    ])
    st = ''.join([
        swatch('Down', '#B0261D', 'A network below a tenth of its level; an incident.'),
        swatch('Degraded', '#8A5000', 'Below its level; a pattern. Bars in #D3982C.'),
        swatch('Steady', '#1C6A45', 'Holding; a case resolved. Bars in #3E9468.'),
    ])
    night = ''.join([
        swatch('Night', '#0F1012', 'The page after dark, the counts band, the footer.'),
        swatch('Night cloth', '#17181B', 'Panels after dark.'),
        swatch('Night sea', '#6AB0F2', 'The lit knot after dark.'),
    ])
    chapters.append(chapter(4, 'colour', 'Colour',
        'Cotton and thread come from the keffiyeh. Sea blue is the Mediterranean of the fisherman\'s net and the blue of a press vest, and it is kept for one thing: what still answers. Status colours are only ever used for status.',
        f'<h3 class="bk-h3">Cloth and thread</h3><ul class="sws">{sw}</ul><h3 class="bk-h3">Status</h3><ul class="sws">{st}</ul>'
        f'<h3 class="bk-h3">Night</h3><ul class="sws night">{night}</ul>'))

    type_html = f'''<div class="ty">
<div class="ty-row"><p class="ty-meta"><b>Schibsted Grotesk</b>Bakken &amp; Bæck for the Schibsted newspapers · 400–900<span>Headlines, reading, navigation</span></p>
<div class="ty-spec"><p class="ty-big">Gaza's internet by IODA's count: {n["routed"]} of {n["prewar"]} blocks routed</p><p class="ty-body">A grotesk cut for newsrooms, with tabular and slashed figures for the board. Headlines at 760 with tight tracking; reading at 400, 17 to 19 pixels, 1.6 line height.</p></div></div>
<div class="ty-row"><p class="ty-meta"><b>Azeret Mono</b>Displaay · 300–700<span>Sources, times, codes, labels</span></p>
<div class="ty-spec"><p class="ty-mono">IODA · BGP · 24 OCT, {ED["read_utc"]} UTC<br>PJS, VIA WAFA · CPJ · PALESTINIAN PRISONERS' SOCIETY</p></div></div>
<div class="ty-row"><p class="ty-meta"><b>Handjet</b>Rosetta · ELSH 15 · 300–800<span>Counts, drawn in knots</span></p>
<div class="ty-spec"><p class="ty-knot"><span class="kn-num">{n["routed"]}</span><span class="kn-num red">{n["answering"]}</span><span class="kn-num">263</span></p><p class="ty-body">Handjet builds every letter from modular elements. With its shape axis at 15 the elements are diamonds, so every count on the board is tied in the same knots as the net.</p></div></div>
<div class="ty-row"><p class="ty-meta"><b>Beiruti</b>Boutros · 400–800<span>Arabic in running text</span></p>
<div class="ty-spec"><p class="ty-ar" lang="ar" dir="rtl">شبكة الصياد، شبكة الإنترنت</p><p class="ty-body">Where an Arabic word sits inside English text, Handjet's knots are too small to read, so it is set in Beiruti, a modern Kufi with an open, even rhythm.</p></div></div>
</div>'''
    chapters.append(chapter(5, 'type', 'Type', 'Three faces and one guest. Each has one job.', type_html))

    states = ''
    for k, (label, fam) in STATUS.items():
        desc = dict(sum([items for _, items in B.GRADES], []))[k]
        states += f'<li class="state st-{fam}">{glyph(k, "big-gl")}<b>{esc(label)}</b><span>{esc(desc)}</span></li>'
    chapters.append(chapter(6, 'states', 'States of the net',
        'The board never uses a generic dot. Every state is drawn from the net: a cell that holds, sags, tears or is mended; a single knot for one event; a run of knots for a pattern; a loose end for an open case; two threads paused for a stalled one.',
        f'<ul class="states">{states}</ul><div class="chips-row">{"".join(chip(k) for k in STATUS)}</div>'))

    chapters.append(chapter(7, 'net', 'The net as a chart',
        f'The lead of the board is drawn as the net itself. One knot for every address block Gaza had before the war: {n["prewar"]}. Today {n["routed"]} hold and {n["answering"]} answer. The rest are drawn as the ghost of the net that was.',
        f'''<div class="nc"><div class="nc-fig">{net_svg(n["prewar"], n["routed"], n["answering"], label="The net today", days=n.get("days"))}</div>
<ul class="nc-rules"><li><b>One knot, one block.</b>A block is 256 addresses. Never round, never scale.</li>
<li><b>Order, not a map.</b>Knots are laid from the headrope down. IODA does not place blocks on a map, and neither do we.</li>
<li><b>Ghost, not gone.</b>Blocks that are no longer routed stay drawn in dashed thread, so the loss keeps its size.</li>
<li><b>Lit means answering.</b>Only knots with a device that replies to IODA's probes are sea blue.</li></ul></div>'''))

    motion = '''<ul class="mo">
<li><b>Cast</b><span>The first visit: a hash sign turns into a cell, its knots are tied, the net spreads from it across the screen, the cell flies to the masthead. 2.7 seconds, once a session, skipped for reduced motion.</span><a class="more" href="home.html?loader">Watch it <span aria-hidden="true">→</span></a></li>
<li><b>Tear</b><span>The lead net first appears whole, as it was before the war. Then the blocks that are no longer routed fall away, row by row, into ghost.</span></li>
<li><b>Mend</b><span>Scrub the month and the net knits and tears to each day's count: 147 in late September, 155 since 9 October.</span></li>
<li><b>Ping</b><span>Every second and a half, one answering knot sends a ring, the way a device answers a probe.</span></li>
<li><b>Tie</b><span>Hover the name and the top knot tightens.</span></li></ul>'''
    chapters.append(chapter(8, 'motion', 'Motion', 'Motion shows what the data does: cast, tear, mend, ping. Nothing moves for decoration, and all of it stops for reduced motion.', motion))

    row0 = B.row(ED['board'][0]['rows'][0], 'networks')
    comp = f'''<div class="cmp"><p class="lbl">A row</p><ul class="rows cmp-row">{row0}</ul>
<p class="lbl">A count</p><div class="cmp-count">{B.counts(ED["counts"][:1]).replace("counts-h", "counts-h sr")}</div></div>'''
    chapters.append(chapter(9, 'parts', 'Parts', 'The board is built from a few parts: the status chip, the row with its bars and the pre-war thread, the entry, the count.', comp))

    chapters.append(chapter(10, 'photos', 'Photographs',
        'Photographs show the person, the place or the thing in the entry, in their own colour, captioned with where and when they were taken. Never a picture of something else. When there is no honest photograph, the entry carries its state on night instead.',
        f'<div class="ph-row">{"".join(ph(s) for s in ("ashtiyeh-beaten-aqraba", "west-bank-4g-still-pending", "bisan-owda-three-years-video"))}</div>'))

    apps = f'''<div class="apps">
<figure class="ap ap-og"><div class="og"><div class="og-l">{brand('', 'brand', tag='div')}<p class="og-h">{esc(ED["lead"]["headline"])}</p><p class="og-s">IODA · {esc(ED["lead"]["at"])}</p></div><div class="og-n">{net_svg(n["prewar"], n["routed"], n["answering"], cls="net og-net")}</div></div><figcaption>Link card, 1200 × 630</figcaption></figure>
<figure class="ap ap-post"><div class="post"><p class="post-k">{chip("down", "Answering down")}</p><p class="post-n"><span class="kn-num">{n["answering"]}</span></p><p class="post-u">Gaza address blocks answering probes, of about {n["prewar_answering"]} before the war</p><p class="post-b">{mark_svg("mark")}<span>palestineonline.co</span></p></div><figcaption>Post, 1080 × 1350</figcaption></figure>
</div>'''
    chapters.append(chapter(11, 'apps', 'Applications', 'The same net on a link card and a post. The count leads; the mark signs it.', apps))

    pages = [('Board', 'home.html'), ('Networks', 'networks.html'), ('Press safety', 'press.html'), ('Speech & evidence', 'speech.html'),
             ('Platforms', 'platforms.html'), ('Creators', 'creators.html'), ('A network row', 'row/gz-routed.html'),
             ('An entry', f'report/{ED["stories"][0]["id"]}.html'), ('Method', 'method.html'), ('Status alerts', 'alerts.html'),
             ('Report an outage', 'report.html'), ('Archive', 'archive.html'), ('Search', 'search.html'), ('Who we are', 'about.html'),
             ('Credits', 'credits.html'), ('Privacy', 'privacy.html'), ('Not found', '404.html')]
    pl = ''.join(f'<li><a href="{u}"><b>{esc(t)}</b><span>{esc(u)}</span></a></li>' for t, u in pages)
    chapters.append(chapter(12, 'site', 'The site', 'Every template, built and linked.', f'<ul class="site-list">{pl}</ul>'))

    toc = ''.join(f'<li><a href="#{c}"{" aria-current=\"true\"" if c == "word" else ""}>{t}</a></li>' for c, t in (
        ('word', 'One word, two nets'), ('mark', 'The mark'), ('lockups', 'Lockups'), ('colour', 'Colour'), ('type', 'Type'),
        ('states', 'States of the net'), ('net', 'The net as a chart'), ('motion', 'Motion'), ('parts', 'Parts'),
        ('photos', 'Photographs'), ('apps', 'Applications'), ('site', 'The site')))

    # brand kit zip
    kit = os.path.join(ROOT, 'assets', 'brand', 'palestine-online-identity.zip')
    with zipfile.ZipFile(kit, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(os.listdir(os.path.join(ROOT, 'assets', 'brand'))):
            if f.endswith('.svg'):
                z.write(os.path.join(ROOT, 'assets', 'brand', f), f)
        z.write(os.path.join(ROOT, 'favicon.svg'), 'favicon.svg')

    html = f'''<!doctype html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{NAME} · Identity</title>
<meta name="description" content="The identity of Palestine Online: one word, شبكة, for a fishing net and a network.">
<link rel="canonical" href="{SITE}">
<meta property="og:title" content="{NAME} · Identity"><meta property="og:image" content="{SITE}assets/og.png"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/schibsted.woff2?v={V}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/po.css?v={V}"><link rel="stylesheet" href="assets/css/book.css?v={V}">
<script>(function(h){{h.classList.add('js');try{{var t=localStorage.getItem('po-theme');if(t)h.dataset.theme=t}}catch(e){{}}}})(document.documentElement)</script>
</head>
<body class="book">
<a class="skip" href="#main">Skip to content</a>
<header class="bk-cover">
<svg class="bk-lattice" aria-hidden="true"></svg>
<div class="wrap bk-cv">
<p class="bk-top">{brand('', 'brand', tag='a')}<span>Identity · October 2026</span><a class="bk-site" href="home.html">Open the board <span aria-hidden="true">→</span></a></p>
<div class="bk-title">{mark_svg('mark bk-mark')}<h1><span class="kn-ar" lang="ar" dir="rtl">شبكة</span><span class="en">A net, a network, a voice that answers.</span></h1></div>
<p class="bk-sub">The identity of {NAME}: the status of Palestine's networks and the safety of its press, on one board.</p>
</div>
</header>
<div class="wrap bk-grid" id="main">
<nav class="bk-toc" aria-label="Chapters"><ol>{toc}</ol><a class="btn bk-dl" href="assets/brand/palestine-online-identity.zip" download>{mark_svg("mark b-mark", lit=False)}<span>Download the marks</span></a></nav>
<main class="bk-main">{''.join(chapters)}</main>
</div>
<footer class="foot bk-foot"><div class="selvage" aria-hidden="true"></div><div class="wrap"><div class="f-bot"><p>© 2026 {NAME} · Identity by TakTek</p><p><a href="home.html">The board</a> · <a href="credits.html">Credits</a></p></div></div></footer>
<script src="assets/js/po.js?v={V}" defer></script>
<script src="assets/js/book.js?v={V}" defer></script>
</body>
</html>
'''
    write('index.html', html)
    print('index.html', len(html) // 1024, 'KB')


if __name__ == '__main__':
    main()
