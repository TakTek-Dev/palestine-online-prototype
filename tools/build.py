"""The home page: the board for one day.

python -I tools/build.py   (reads tools/edition.json, writes home.html)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (ROOT, STATUS, chip, day_long, day_mid, day_short, esc, foot, glyph, head, loader,  # noqa: E402
                    mast, scripts, spark, strip, write)
from net import net_svg  # noqa: E402

ED = json.load(open(os.path.join(ROOT, 'tools', 'edition.json'), encoding='utf-8'))
ED.setdefault('spark_from', '8 Sep')
ED.setdefault('spark_to', day_short(ED['date']))
PHOTOS = {}
pj = os.path.join(ROOT, 'tools', 'out', 'photos.json')
if os.path.exists(pj):
    PHOTOS = json.load(open(pj, encoding='utf-8'))


def series(spec):
    """Spark data: a daily list, or {'bars', 'hits'} for an alert row (one bar a day, alert days marked)."""
    if isinstance(spec, list):
        return spec, None
    if isinstance(spec, dict):
        return spec['bars'], spec['hits']
    return [], None


def photo(p, cls='ph', sizes='(max-width: 760px) 100vw, 520px', eager=False):
    if not p:
        return ''
    meta = PHOTOS.get(p['slug'], {'w': 1000, 'h': 667})
    load = 'eager' if eager else 'lazy'
    return (f'<figure class="{cls}"><img src="assets/img/photo/{p["slug"]}.webp" width="{meta["w"]}" height="{meta["h"]}" '
            f'alt="{esc(p["alt"])}" loading="{load}" decoding="async" sizes="{sizes}">'
            f'<figcaption>{esc(p["caption"])}</figcaption></figure>')


# ---------------------------------------------------------------- lead
def scrub(n):
    days = n.get('days')
    if not days:
        return ''
    last = len(days) - 1
    marks = ''
    prev = None
    for i, (d, r, a) in enumerate(days):
        if prev is not None and r != prev:
            marks += f'<i style="--x:{i / last:.4f}" title="{day_short(d)}: {r}"></i>'
        prev = r
    return f'''<div class="scrub" data-scrub>
<label for="scrub-in" class="lbl">Scrub the month</label>
<div class="sc-track"><input id="scrub-in" type="range" min="0" max="{last}" value="{last}" step="1" aria-valuetext="{day_short(days[-1][0])}: {days[-1][1]} routed, {days[-1][2]} answering"><span class="sc-marks" aria-hidden="true">{marks}</span></div>
<p class="sc-ends" aria-hidden="true"><span>{day_short(days[0][0])}</span><span>{day_short(days[-1][0])}</span></p>
<output for="scrub-in">{day_short(days[-1][0])} · {days[-1][1]} of {n["prewar"]} routed · {days[-1][2]} answering</output>
</div>'''


def lead(L):
    n = L['net']
    chips = ''.join(chip(s, t) for s, t in L['chips'])
    paras = ''.join(f'<p>{esc(p)}</p>' for p in L['paras'])
    gone = n['prewar'] - n['routed']
    label = (f"The net: {n['prewar']} knots, one for each Gaza address block routed before the war. "
             f"{n['routed']} hold, {n['answering']} of them answer; {gone} are no longer routed.")
    pct_r = round(n['routed'] / n['prewar'] * 100)
    pct_a = round(n['answering'] / n['prewar_answering'] * 100)
    return f'''<section class="lead" aria-labelledby="lead-h">
<div class="wrap lead-grid">
<header class="lead-head">
<div class="lead-top"><p class="kick"><span>{esc(L["kicker"])}</span><time>{esc(L["at"])}</time></p><div class="chips">{chips}</div></div>
<h1 id="lead-h">{esc(L["headline"])}</h1>
</header>
<div class="lead-text">
<p class="dek">{esc(L["dek"])}</p>
<dl class="meters">
<div class="meter m-routed"><dt>Routed address blocks</dt>
<dd><span class="kn-num" data-count="{n["routed"]}">{n["routed"]}</span><span class="of">of {n["prewar"]} before the war</span>
<span class="bar" style="--p:{n["routed"] / n["prewar"]:.4f}"><i></i></span><span class="pc">{pct_r}%</span></dd></div>
<div class="meter m-answer"><dt>Blocks answering probes</dt>
<dd><span class="kn-num" data-count="{n["answering"]}">{n["answering"]}</span><span class="of">of ≈{n["prewar_answering"]} before the war</span>
<span class="bar" style="--p:{n["answering"] / n["prewar_answering"]:.4f}"><i></i></span><span class="pc">{pct_a}%</span></dd></div>
</dl>
</div>
<div class="lead-more"><p class="via">{esc(L["source"])}</p>{f'<a class="more" href="{L["href"]}">Read the analysis <span aria-hidden="true">→</span></a>' if L.get("href") else ''}</div>
<figure class="lead-net">
<div class="net-frame">
<p class="headrope"><span>Headrope</span> {n["prewar"]} blocks routed on 1–6 Oct 2023</p>
{net_svg(n["prewar"], n["routed"], n["answering"], label=label, days=n.get("days"), note=True)}
<p class="net-tip" role="status" aria-live="polite"></p>
</div>
{scrub(n)}
<figcaption class="net-key">
<span class="nk nk-lit"><i></i>{n["answering"]} answering</span>
<span class="nk nk-held"><i></i>{n["routed"] - n["answering"]} routed, silent</span>
<span class="nk nk-gone"><i></i>{gone} no longer routed</span>
<span class="nk-note">One knot per block of 256 addresses. Order, not a map.</span>
</figcaption>
</figure>
</div>
</section>
'''


# ---------------------------------------------------------------- tally
def tally(board):
    def count(keys):
        c = {}
        for g in board:
            if g['key'] in keys:
                for r in g['rows']:
                    c[r['status']] = c.get(r['status'], 0) + 1
        return c
    net = count({'networks'})
    rest = count({'press', 'speech', 'platforms', 'creators'})
    order_n = ['down', 'degraded', 'steady', 'restored']
    order_p = ['incident', 'open', 'stalled', 'pattern', 'resolved', 'recognised']
    words = {'down': 'down', 'degraded': 'degraded', 'steady': 'steady', 'restored': 'restored',
             'incident': ('incident', 'incidents'), 'open': 'open', 'stalled': 'stalled',
             'pattern': ('pattern', 'patterns'), 'resolved': 'resolved', 'recognised': 'recognised'}

    def label(k, n):
        w = words[k]
        if isinstance(w, tuple):
            w = w[0] if n == 1 else w[1]
        return f'{n} {w}'
    a = ''.join(chip(k, label(k, net[k])) for k in order_n if net.get(k))
    b = ''.join(chip(k, label(k, rest[k])) for k in order_p if rest.get(k))
    return f'''<section class="tally" aria-label="Today on the board"><div class="wrap">
<dl>
<div><dt>Networks</dt><dd>{a}</dd></div>
<div><dt>Press &amp; speech</dt><dd>{b}</dd></div>
</dl>
<a class="tally-go" href="#board">Read the board <span aria-hidden="true">↓</span></a>
</div></section>
'''


# ---------------------------------------------------------------- board
NUM = re.compile(r'[€$]?\d[\d,.]*(?:[–-]\d+)?[m%]?|\d{1,2}:\d{2}')
DATE = re.compile(r'\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)')


def reading(value, unit, cls='c-read'):
    """A count is tied in knots, a date is read off the instrument, a place or a word is set in type."""
    if NUM.fullmatch(value):
        kind, span = 'num', 'kn-num'
    elif DATE.fullmatch(value):
        kind, span = 'date', 'rd'
    else:
        kind, span = 'word', 'rw'
    return (f'<p class="{cls} read r-{kind}"><span class="{span}">{esc(value)}</span>'
            f'<small>{esc(unit)}</small></p>')


def alert_spark(n, hits, label):
    """One tick a day; a full bar only on a day with an outage alert."""
    w, h, gap = 300, 44, 2
    bw = (w - gap * (n - 1)) / n
    bars = ''.join(f'<rect x="{i * (bw + gap):.2f}" y="{0 if i in hits else h - 4:.2f}" width="{bw:.2f}" '
                   f'height="{h if i in hits else 4}" style="--i:{i}"{" class=\"hit\"" if i in hits else ""}/>'
                   for i in range(n))
    return f'<svg class="spark sp-alert" viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img" aria-label="{esc(label)}">{bars}</svg>'


def row(r, key):
    vals, hit = series(r.get('spark'))
    href = r.get('href') or f"#{r['code']}"
    if vals:
        if hit is not None:
            sp = alert_spark(len(vals), set(hit),
                             'One tick a day; ' + (f"{len(hit)} day with an outage alert" if hit else 'no outage alert in 30 days'))
        else:
            sp = spark(vals, r.get('ref'), r['status'],
                       label=f"Daily average over 30 days, ending at {r['reading']}" +
                             (f"; pre-war level {r['ref']:,}" if r.get('ref') else ''))
        sp_cell = f'<div class="c-spark">{sp}<div class="axis"><span>{esc(ED["spark_from"])}</span><span>{esc(ED["spark_to"])}</span></div></div>'
    else:
        sp_cell = f'<div class="c-spark none"><p class="nospark">{esc(r.get("kind", "Single event"))}</p></div>'
    return f'''<li class="row" id="{esc(r["code"])}">
<div class="c-st">{chip(r["status"])}</div>
<div class="c-name"><h4><a href="{esc(href)}">{esc(r["name"])}</a></h4><p class="ctx">{esc(r["ctx"])}</p></div>
{reading(r["reading"], r["unit"])}
{sp_cell}
<p class="c-src"><b>{esc(r["src"])}</b>{esc(r["at"])}</p>
<a class="c-go go" href="{esc(href)}" aria-label="Open: {esc(r["name"])}"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M7 4l6 6-6 6"/></svg></a>
</li>'''


def board(groups):
    gs = ''
    for g in groups:
        rows = '\n'.join(row(r, g['key']) for r in g['rows'])
        gs += f'''<section class="group g-{g["key"]}" aria-labelledby="g-{g["key"]}">
<header class="group-h"><h3 id="g-{g["key"]}"><a href="{g["key"]}.html">{esc(g["title"])}</a></h3><span>{esc(g["by"])}</span></header>
<ul class="rows">
{rows}
</ul>
{f'<button class="unfold" type="button" aria-expanded="false" hidden>Show {len(g["rows"]) - 3} more rows</button>' if len(g["rows"]) > 3 else ''}
</section>
'''
    return f'''<section class="board sec" id="board" aria-labelledby="board-h"><div class="wrap">
<div class="sec-h"><h2 id="board-h">The board</h2>
<p class="legend"><span class="lg-bar">Bars: daily, {esc(ED["spark_from"])} – {esc(ED["spark_to"])}</span><span class="lg-ref">Thread: level on 1–6 Oct 2023</span></p></div>
{gs}</div></section>
'''


DESK = {'networks': 'Networks', 'press': 'Press safety', 'speech': 'Speech & evidence', 'platforms': 'Platforms',
        'creators': 'Creators'}


def byline(text):
    """Keep the date at the end of a source line in one piece."""
    head, sep, tail = text.rpartition(' · ')
    return f'{esc(head)} · <span class="nw">{esc(tail)}</span>' if sep else esc(text)


def story_href(s):
    return s.get('href') or f"report/{s['id']}.html"


def front(stories, n=8):
    """The newest entries for the home page: this month's, photographed ones first among the same day."""
    if ED.get('front'):
        by = {s['id']: s for s in stories}
        return [by[i] for i in ED['front'] if i in by][:n]
    now = [s for s in stories if not s.get('background')]
    now.sort(key=lambda s: (s['date'], bool(s.get('photo'))), reverse=True)
    return now[:n]


def ledger(stories):
    if not stories:
        return ''
    items = ''
    for i, s in enumerate(stories):
        ph = photo(s.get('photo'), 'e-fig', '(max-width: 760px) 100vw, 360px')
        items += f'''<li class="entry{" has-fig" if ph else ""}{" first" if i == 0 else ""}">
<div class="meta">{chip(s["status"])}<time datetime="{s["date"]}">{esc(day_mid(s["date"]))}</time><span class="desk">{esc(DESK[s["desk"]])}</span></div>
<div class="e-text"><h3><a href="{story_href(s)}">{esc(s["headline"])}</a></h3><p>{esc(s["summary"])}</p><p class="via">{byline(s.get("byline") or s["via"])}</p></div>
{ph}
</li>'''
    return f'''<section class="sec behind" id="behind" aria-labelledby="behind-h"><div class="wrap">
<div class="sec-h"><h2 id="behind-h">Behind the rows</h2><a class="more" href="archive.html">Every entry, by date <span aria-hidden="true">→</span></a></div>
<ul class="ledger">
{items}
</ul></div></section>
'''


def counts(cs):
    if not cs:
        return ''
    cells = ''.join(f'''<div class="count">
<p class="c-num"><span class="kn-num">{esc(c["num"])}</span></p>
<h3>{esc(c["unit"])}</h3><p class="c-ctx">{esc(c["ctx"])}</p><p class="c-by">{esc(c["src"])} · <span class="nw">{esc(c["at"])}</span></p>
</div>''' for c in cs)
    return f'''<section class="counts" aria-labelledby="counts-h"><div class="wrap">
<div class="counts-h"><h2 id="counts-h">The press, counted</h2><p>Each monitor counts in its own way, so every figure here carries its source and its date. When two counts differ, we print both.</p></div>
<div class="count-row">{cells}</div>
</div></section>
'''


def creators(cs):
    if not cs:
        return ''
    by = {s['id']: s for s in ED['stories']}
    cards = ''
    for c in cs:
        s = by.get(c['id'])
        if not s:
            continue
        p = s.get('photo')
        meta = PHOTOS.get(p['slug'], {'w': 800, 'h': 1000}) if p else None
        img = (f'<img src="assets/img/photo/{p["slug"]}.webp" width="{meta["w"]}" height="{meta["h"]}" alt="{esc(p["alt"])}" loading="lazy">'
               if p else f'<span class="cr-ph" aria-hidden="true">{glyph(s["status"], "pl-gl")}</span>')
        cards += f'''<li class="cr"><a href="{story_href(s)}"><span class="cr-img">{img}</span>
<span class="cr-t">{chip(s["status"])}<b>{esc(c["name"])}</b><span class="cr-l">{esc(c["line"])}</span><time datetime="{s["date"]}">{esc(day_mid(s["date"]))}</time></span></a></li>'''
    return f'''<section class="sec creators-band" aria-labelledby="cr-h"><div class="wrap">
<div class="sec-h"><h2 id="cr-h">Creators on the record</h2><a class="more" href="creators.html">The creators desk <span aria-hidden="true">→</span></a></div>
<ul class="cr-row">{cards}</ul>
</div></section>
'''


GRADES = [
    ('Networks', [('down', 'Below a tenth of its level before the war.'),
                  ('degraded', 'Measurably below its pre-war level.'),
                  ('steady', 'No change worth a headline in 30 days.'),
                  ('restored', 'Back after an outage we reported.')]),
    ('Press & speech', [('incident', 'One event, with a place and a date.'),
                        ('pattern', 'A trend a named monitor documents.'),
                        ('open', 'A case still unresolved.'),
                        ('stalled', 'A case with no progress reported.'),
                        ('resolved', 'A case that ended: a release, a ruling.'),
                        ('recognised', 'Work that won a prize or a hearing.')]),
]


def recent_changes(n=4):
    """The last few state changes on the board: what a subscriber would have been sent."""
    rows = [(r, g) for g in ED['board'] for r in g['rows'] if r['status'] in ('restored', 'resolved', 'incident')]
    def when(r):
        m = re.match(r'(\d+) (\w+)', r['at'])
        return (MONTHS_N.get(m.group(2), 0), int(m.group(1))) if m else (0, 0)
    rows.sort(key=lambda x: when(x[0]), reverse=True)
    items = ''.join(f'<li><a href="{esc(r.get("href") or "#" + r["code"])}">{chip(r["status"])}<span>{esc(r["name"])}</span>'
                    f'<time>{esc(r["at"].split(",")[0])}</time></a></li>' for r, g in rows[:n])
    return f'<div class="recent"><p class="lbl">What you would have been sent this week</p><ul>{items}</ul></div>'


MONTHS_N = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}


def foot_band():
    grades = ''.join(
        f'<div class="grade"><h3>{esc(h)}</h3><dl>' +
        ''.join(f'<div><dt>{chip(k)}</dt><dd>{esc(t)}</dd></div>' for k, t in rows) + '</dl></div>'
        for h, rows in GRADES)
    return f'''<section class="sec foot-band" aria-label="Alerts and method"><div class="wrap fb-grid">
<div class="subscribe" id="alerts">
<h2>Status alerts</h2>
<p>One email when a row changes state: an outage in Gaza, a journalist detained, a platform takedown. Nothing else.</p>
<form class="sub-form" action="alerts.html" method="get">
<label><span class="lbl">Email address</span><input type="email" name="email" autocomplete="email" required placeholder="you@example.org"></label>
<button class="btn" type="submit">Subscribe</button>
</form>
<p class="fine">A prototype: the form opens the alerts page and sends nothing.</p>
{recent_changes()}
</div>
<div class="method">
<h2>How a row is graded</h2>
<p>Every state is drawn from one net: a cell that holds, thins or tears, a knot, a loose end.</p>
<div class="grades">{grades}</div>
<a class="more" href="method.html">The whole method <span aria-hidden="true">→</span></a>
</div>
</div></section>
'''


def main():
    L = ED['lead']
    desc = 'Is Palestine online? The status of its networks, its journalists and its speech, read every day from named sources.'
    page = (head('Palestine Online — the status of the press and the networks', desc, body_cls='home')
            + loader() + strip(ED) + mast('', 'board')
            + '<main id="main">\n' + lead(L) + tally(ED['board']) + board(ED['board']) + ledger(front(ED['stories']))
            + counts(ED['counts']) + creators(ED.get('creators')) + foot_band() + '</main>\n'
            + foot() + scripts())
    write('home.html', page)
    print('home.html', len(page) // 1024, 'KB')


if __name__ == '__main__':
    main()
