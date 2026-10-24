"""Every page behind the board: one per entry, one per desk, the network rows, the desk's own pages.

python -I tools/pages.py   (after tools/build.py; reads tools/edition.json)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # noqa: E402
from common import (NAME, ROOT, SITE, STATUS, chip, day_full, day_long, day_mid, esc, foot, glyph, head,  # noqa: E402
                    loader, mark_svg, mast, scripts, spark, strip, write)
from net import net_svg  # noqa: E402

ED = B.ED
DESK = B.DESK
DESK_LINE = {
    'networks': 'Whether the rest of the internet can still reach Gaza and the West Bank, read from IODA at Georgia Tech.',
    'press': 'Journalists killed, hurt, held or kept from working, as unions, prisoner groups and press-freedom monitors record it.',
    'speech': 'Posts, footage and what is done with them: arrests over words, cameras seized in raids, recordings deleted.',
    'platforms': 'What platforms and governments take down, block or bury, and what they say when asked.',
    'creators': 'The Palestinians who report, film and post for themselves, and what happens to their work and accounts.',
}
STORIES = ED['stories']
BY_ID = {s['id']: s for s in STORIES}


def crumbs(rel, trail):
    items = [f'<li><a href="{rel}home.html">Board</a></li>']
    for label, href in trail:
        items.append(f'<li><a href="{rel}{href}">{esc(label)}</a></li>' if href else f'<li aria-current="page">{esc(label)}</li>')
    ld = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, **({'item': SITE + h} if h else {})}
        for i, (n, h) in enumerate([('Board', 'home.html')] + trail)]}
    return (f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')


def page(path, title, desc, body, active, rel='', cls='', og=None, extra_js=()):
    write(path, head(title, desc, rel, path, cls, og) + loader() + strip(ED, rel) + mast(rel, active)
          + f'<main id="main">\n{body}</main>\n' + foot(rel) + scripts(rel, extra_js))


def fix_rel(html, rel):
    """Point home-relative links and assets one level up for pages in a folder."""
    if not rel:
        return html
    return re.sub(r'(href|src)="(?!https?:|#|mailto:|data:|\.\./)([^"]+)"', lambda m: f'{m.group(1)}="{rel}{m.group(2)}"', html)


# ---------------------------------------------------------------- one entry
def plate(s, rel):
    if s['id'] == (ED['lead'].get('href') or '').split('/')[-1][:-5]:
        n = ED['lead']['net']
        return (f'<figure class="plate plate-knots"><div class="net-frame"><p class="headrope"><span>Headrope</span> {n["prewar"]} blocks routed on 1–6 Oct 2023</p>'
                f'{net_svg(n["prewar"], n["routed"], n["answering"], label="The net today", days=n.get("days"), note=True)}<p class="net-tip" role="status" aria-live="polite"></p></div>'
                f'{B.scrub(n)}</figure>')
    p = s.get('photo')
    if p:
        meta = B.PHOTOS.get(p['slug'], {'w': 1000, 'h': 667})
        return (f'<figure class="plate{" plate-place" if p.get("kind") == "place" else ""}"><img src="{rel}assets/img/photo/{p["slug"]}.webp" width="{meta["w"]}" '
                f'height="{meta["h"]}" alt="{esc(p["alt"])}" fetchpriority="high"><figcaption>{esc(p["caption"])}</figcaption></figure>')
    label, fam = STATUS[s['status']]
    return (f'<figure class="plate plate-net pl-{fam}" aria-hidden="true"><div class="pl-in">{glyph(s["status"], "pl-gl")}'
            f'<p class="pl-place">{esc(s.get("place", ""))}</p><p class="pl-st">{esc(label)} · {esc(day_full(s["date"]))}</p></div></figure>')


def sources(s):
    host = lambda u: re.sub(r'^https?://(www\.)?', '', u).split('/')[0]  # noqa: E731
    links = [(host(u), u) for u in ([s['url']] if s.get('url') else []) + (s.get('more_urls') or [])]
    return ''.join(f'<li><a href="{esc(u)}" rel="noopener" target="_blank">{esc(t)}<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 11L11 5M6 5h5v5"/></svg></a></li>' for t, u in links)


def related(s, rel, n=3):
    same = [x for x in STORIES if x['desk'] == s['desk'] and x['id'] != s['id']][:n]
    if len(same) < n:
        same += [x for x in STORIES if x['id'] != s['id'] and x not in same][:n - len(same)]
    cards = ''
    for x in same:
        p = x.get('photo')
        img = (f'<img src="{rel}assets/img/photo/{p["slug"]}.webp" alt="" loading="lazy" width="300" height="200">' if p
               else f'<span class="rc-ph" aria-hidden="true">{glyph(x["status"], "pl-gl")}</span>')
        cards += (f'<li class="rc"><a href="{rel}report/{x["id"]}.html">{img}<span class="rc-t">{chip(x["status"])}'
                  f'<b>{esc(x["headline"])}</b><time datetime="{x["date"]}">{esc(day_mid(x["date"]))}</time></span></a></li>')
    return f'<section class="related" aria-labelledby="rel-h"><h2 id="rel-h">More from the board</h2><ul>{cards}</ul></section>'


def story_page(s):
    rel = '../'
    paras = ''.join(f'<p>{esc(p.strip())}</p>' for p in re.split(r'\n\s*\n', s.get('body') or s['summary']) if p.strip())
    people = ''.join(f'<li>{esc(p)}</li>' for p in s.get('people', []))
    reading = ''
    on = next((r for g in ED['board'] for r in g['rows'] if r['code'] == s['id']), None)
    val, unit = (on['reading'], on['unit']) if on else (s.get('reading'), s.get('reading_unit') or '')
    if val:
        reading = (f'<div class="on-board"><h2 class="lbl">{"On the board" if on else "The figure"}</h2><p class="ob-st">{chip(s["status"])}</p>'
                   + B.reading(val, unit, 'ob-read')
                   + (f'<p class="ob-note">{esc(s["reading_note"])}</p>' if s.get('reading_note') else '') + '</div>')
    ld = {'@context': 'https://schema.org', '@type': 'NewsArticle', 'headline': s['headline'],
          'datePublished': s.get('published', s['date']), 'dateModified': s.get('published', s['date']),
          'description': s['summary'], 'mainEntityOfPage': f'{SITE}report/{s["id"]}.html',
          'publisher': {'@type': 'Organization', 'name': NAME},
          'author': {'@type': 'Organization', 'name': f'{NAME} desk'}}
    if s.get('photo'):
        ld['image'] = f'{SITE}assets/img/photo/{s["photo"]["slug"]}.webp'
    body = f'''<article class="story" itemscope>
<div class="wrap">
{crumbs(rel, [(DESK[s["desk"]], f'{s["desk"]}.html'), (s["headline"][:48] + ("…" if len(s["headline"]) > 48 else ""), None)])}
<header class="s-head">
<p class="s-meta">{chip(s["status"])}<a class="desk" href="{rel}{s["desk"]}.html">{esc(DESK[s["desk"]])}</a><time datetime="{s["date"]}">{esc(day_long(s["date"]))}</time>{f'<span class="place">{esc(s["place"])}</span>' if s.get("place") else ""}</p>
<h1>{esc(s["headline"])}</h1>
<p class="s-dek">{esc(s["summary"])}</p>
</header>
{plate(s, rel)}
<div class="s-grid">
<div class="s-body">{paras}
<p class="s-via">Reported from {esc(s.get("source") or s.get("via", ""))}{(", via " + esc(s["via"])) if s.get("via") and s.get("via") != s.get("source") else ""}. Filed {esc(day_full(s.get("published", s["date"])))}.</p>
<p class="s-fix">See something wrong? <a href="{rel}method.html#corrections">Ask for a correction</a>; we print every one.</p>
</div>
<div class="s-side">{reading}
<div class="s-src"><h2 class="lbl">Sources</h2><ul>{sources(s)}</ul></div>
{f'<div class="s-people"><h2 class="lbl">Named here</h2><ul>{people}</ul></div>' if people else ''}
<div class="s-share"><h2 class="lbl">Share</h2><button class="share" type="button" data-share>{glyph("steady", "gl")}<span>Copy the link</span></button></div>
</div>
</div>
{related(s, rel)}
</div>
</article>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
'''
    og = f'{SITE}assets/img/photo/{s["photo"]["slug"]}.webp' if s.get('photo') else None
    page(f'report/{s["id"]}.html', s['headline'], s['summary'], fix_body(body, rel), s['desk'], rel, 'p-story', og)


def fix_body(body, rel):
    # chips and glyphs carry no links; only the crumbs/related use rel already
    return body


# ---------------------------------------------------------------- desks
def desk_page(key):
    group = next((g for g in ED['board'] if g['key'] == key), None)
    rows = '\n'.join(B.row(r, key) for r in group['rows']) if group else ''
    own = [s for s in STORIES if s['desk'] == key]
    lead_i = next((i for i, s in enumerate(own) if s.get('photo') and not s.get('background')), None)
    if lead_i:
        own.insert(0, own.pop(lead_i))      # the desk opens on its newest photographed entry
    counts = {}
    for r in (group['rows'] if group else []):
        counts[r['status']] = counts.get(r['status'], 0) + 1
    tally = ''.join(chip(k, f'{n} {STATUS[k][0].lower()}') for k, n in counts.items())
    lead = ''
    if key == 'networks':
        L = ED['lead']
        n = L['net']
        paras = ''.join(f'<p>{esc(p)}</p>' for p in L['paras'])
        lead = f'''<section class="desk-lead"><figure class="desk-net lead-net"><div class="net-frame">
<p class="headrope"><span>Headrope</span> {n["prewar"]} blocks routed on 1–6 Oct 2023</p>
{net_svg(n["prewar"], n["routed"], n["answering"], label=f"{n['routed']} of {n['prewar']} pre-war Gaza address blocks routed, {n['answering']} answering", days=n.get("days"), note=True)}
<p class="net-tip" role="status" aria-live="polite"></p></div>
{B.scrub(n)}</figure>
<div class="dl-text"><p class="kick"><span>{esc(L["kicker"])}</span><time>{esc(L["at"])}</time></p><h2>{esc(L["headline"])}</h2>{paras}<p class="via">{esc(L["source"])}</p></div></section>'''
    body = f'''<div class="wrap">
{crumbs('', [(DESK[key], None)])}
<header class="d-head">
<h1>{esc(DESK[key])}</h1>
<p class="d-line">{esc(DESK_LINE[key])}</p>
<div class="d-tally">{tally}</div>
</header>
{lead}
{f'<section class="group g-{key} d-group" aria-label="{esc(DESK[key])} rows"><header class="group-h"><h2>On the board</h2><span>{esc(group["by"])}</span></header><ul class="rows">{rows}</ul></section>' if group else ''}
</div>
{B.creators(ED.get('creators')).replace('Creators on the record', 'On the record').replace('<a class="more" href="creators.html">The creators desk <span aria-hidden="true">→</span></a>', '') if key == 'creators' else ''}
{B.ledger(own).replace('Behind the rows', 'Every entry').replace('Every entry, by date', 'The whole archive') if own else ''}
{B.counts(ED['counts']) if key == 'press' else ''}
'''
    page(f'{key}.html', DESK[key], DESK_LINE[key], body, key, '', 'p-desk')


# ---------------------------------------------------------------- network rows
IODA = json.load(open(os.path.join(ROOT, 'research', 'ioda.json'), encoding='utf-8'))
ROWDOC = {
    'gz-routed': ('Gaza Strip', 1226, 'bgp',
                  "How many of the Gaza Strip's /24 address blocks (256 addresses each) are visible in the global routing "
                  "tables. A routed block can be reached in principle; one that is not has dropped off the internet's map."),
    'gz-answering': ('Gaza Strip', 1226, 'ping-slash24',
                     "How many Gaza blocks have at least one address that answers IODA's probes. It is the closest IODA comes "
                     "to counting devices that are switched on and connected."),
    'gz-alerts': ('Gaza Strip', 1226, 'alerts',
                  'IODA raises an alert when a signal falls well below its own recent history. Every Gaza outage event since '
                  'August is listed below.'),
    'wb-routed': ('West Bank', 4581, 'bgp',
                  "How many of the West Bank's /24 address blocks are visible in the global routing tables."),
    'wb-blip': ('West Bank', 4581, 'alerts',
                'IODA outage events for the West Bank since August. Two probing gaps that hit the whole region at once are '
                'not counted as local outages.'),
}


CARE = {
    'all': [
        'IODA counts blocks of 256 internet addresses, not people. A block that answers may hold one device or a hundred.',
        'IODA places blocks with a commercial geolocation database. A block registered to a Gaza operator but announced '
        'from elsewhere can be counted in another region, so read the rows as trends, not exact sizes.',
        'Data © Georgia Tech Research Corporation, published here with credit to IODA.',
    ],
    'Gaza Strip': [
        'Routed blocks are the steadier signal. Answering blocks move more from day to day, and on a single day a few '
        'blocks either way is noise.',
    ],
    'West Bank': [
        'Two IODA alerts for the West Bank this month, on 15 October at 22:20 UTC and on 18 October at midnight, were not '
        'outages there: the same drop hit Israel, Jordan, Egypt, Lebanon and Gaza at the same minutes, a gap in IODA\'s '
        'own probing. We do not count them.',
        'West Bank blocks answering probes are about four times their 2023 level. That points to a change in how IODA '
        'probes, not to four times as many people online, so we compare the routed count with the pre-war level instead.',
    ],
}


def big_chart(vals, ref, status, dates, label, hits=None):
    w, h = 1000, 220
    if hits is not None:
        n, gap = len(vals), 4
        bw = (w - gap * (n - 1)) / n
        bars = ''.join(f'<rect x="{i * (bw + gap):.2f}" y="{0 if i in hits else h - 8}" width="{bw:.2f}" '
                       f'height="{h if i in hits else 8}" style="--i:{i}"{" class=\"hit\"" if i in hits else ""}/>' for i in range(n))
        sp = f'<svg class="spark sp-alert" viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img" aria-label="{esc(label)}">{bars}</svg>'
    else:
        sp = spark(vals, ref, status, w, h, label)
    ticks = ''.join(f'<span style="--x:{i / (len(dates) - 1):.4f}">{esc(day_mid(d)[4:])}</span>'
                    for i, d in enumerate(dates) if (i % 7 == 0 and len(dates) - 1 - i > 3) or i == len(dates) - 1)
    top = max(max(vals), ref or 0) * 1.08
    refl = f'<p class="bc-ref" style="--y:{1 - ref / top:.4f}">1–6 Oct 2023 · {ref:,}</p>' if ref else ''
    return f'<figure class="big-chart"><div class="bc-plot">{sp}{refl}</div><p class="bc-x" aria-hidden="true">{ticks}</p></figure>'


def row_page(r):
    region, code, sig, what = ROWDOC[r['code']]
    reg = IODA['regions'][region]
    dates = [d['date'] for d in reg['daily_24_sep_to_24_oct_2026']['bgp']]
    if sig == 'alerts':
        events = [e for e in reg['outage_events_since_1_aug_2026'] if not (e['datasource'] == 'ping-slash24' and region == 'West Bank')]
        hits = [i for i, d in enumerate(dates) if any(e['from'][:10] == d for e in events)]
        chart = big_chart([1] * len(dates), None, 'steady', dates,
                          'One bar a day, 24 Sep – 24 Oct; days with an outage event marked', hits)
        lis = ''.join(f'<li><time>{esc(day_full(e["from"][:10]))} · {e["from"][11:16]}–{e["until"][11:16]} UTC</time>'
                      f'<span>{e["minutes"]} minutes · {"routing (BGP)" if e["datasource"] == "bgp" else "active probing"}</span></li>'
                      for e in events)
        extra = f'<section class="r-sec"><h2>Outage events since 1 August</h2><ul class="events">{lis}</ul></section>'
    else:
        vals = [d['median'] for d in reg['daily_24_sep_to_24_oct_2026'][sig]]
        chart = big_chart(vals, r.get('ref'), r['status'], dates,
                          f'Daily median, 24 Sep – 24 Oct 2026; pre-war level {r.get("ref", 0):,}')
        extra = (f'<section class="r-sec"><h2>The month in figures</h2><dl class="figs">'
                 f'<div><dt>Today</dt><dd>{esc(r["reading"])}</dd></div><div><dt>Lowest day</dt><dd>{min(vals):,.0f}</dd></div>'
                 f'<div><dt>Highest day</dt><dd>{max(vals):,.0f}</dd></div><div><dt>1–6 Oct 2023</dt><dd>{r.get("ref", 0):,}</dd></div>'
                 f'</dl></section>')
    notes = ''.join(f'<li>{esc(n)}</li>' for n in CARE[region] + CARE['all'])
    body = f'''<div class="wrap row-page">
{crumbs('../', [('Networks', 'networks.html'), (r["name"], None)])}
<header class="r-head">
<p class="s-meta">{chip(r["status"])}<span>{esc(r["src"])}</span><time>{esc(r["at"])}</time></p>
<h1>{esc(r["name"])}</h1>
<p class="s-dek">{esc(r["ctx"])}</p>
{B.reading(r["reading"], r["unit"], 'r-read')}
</header>
{chart}
<div class="r-grid">
<section class="r-sec"><h2>What this row measures</h2><p>{esc(what)}</p>
<p>Each bar is the day's median of IODA's samples, every five minutes for routing and every ten for probing. The thread across the bars is the mean over 1–6 October 2023, the last days before the war.</p>
<p><a class="ext" href="https://ioda.inetintel.cc.gatech.edu/region/{code}" rel="noopener" target="_blank">Open {esc(region)} on IODA ↗</a></p></section>
{extra}
<section class="r-sec"><h2>Read it with care</h2><ul class="notes">{notes}</ul></section>
</div>
</div>
'''
    page(f'row/{r["code"]}.html', r['name'], r['ctx'], body, 'networks', '../', 'p-row')


# ---------------------------------------------------------------- the desk's own pages
def prose(path, title, desc, active, sections, lede=''):
    secs = ''.join(f'<section class="pr-sec" id="{sid}"><h2>{esc(h)}</h2>{html}</section>' for sid, h, html in sections)
    toc = ''.join(f'<li><a href="#{sid}">{esc(h)}</a></li>' for sid, h, _ in sections)
    body = f'''<div class="wrap">
{crumbs('', [(title, None)])}
<header class="d-head pr-head"><h1>{esc(title)}</h1><p class="d-line">{esc(lede)}</p></header>
<div class="pr-grid"><nav class="pr-toc" aria-label="On this page"><p class="lbl">On this page</p><ol>{toc}</ol></nav>
<div class="pr-body">{secs}</div></div>
</div>
'''
    page(path, title, desc, body, active, '', 'p-prose')


def grade_table():
    out = ''
    for h, items in B.GRADES:
        out += f'<h3>{esc(h)}</h3><dl class="g-list">' + ''.join(
            f'<div><dt>{chip(k)}</dt><dd>{esc(t)}</dd></div>' for k, t in items) + '</dl>'
    return out


def method_page():
    notes = ''.join(f'<li>{esc(n)}</li>' for n in CARE['all'] + CARE['West Bank'])
    prose('method.html', 'Method', 'How the board is read, graded, sourced and corrected.', 'method', [
        ('board', 'What the board is',
         '<p>The board answers two questions every day: can the rest of the internet reach Palestine, and are the people who '
         'report from it safe to work. Each row is a measurement or a case, with its source, the time it was read and a grade.</p>'
         '<p>We do not grade on feeling. A row changes state only when its source changes, and the change is printed with a date.</p>'),
        ('networks', 'Networks: how a row is read',
         '<p>Network rows come from IODA, the Internet Outage Detection and Analysis project at Georgia Tech. IODA watches '
         'whether a region\'s address blocks are visible in global routing (BGP) and whether devices in them answer probes '
         '(active probing). We use both.</p>'
         '<p>A bar is the median of the day\'s samples. The thread is the mean over 1–6 October 2023. IODA counts blocks of 256 '
         'addresses, not people, and places blocks with a commercial geolocation database, so read the rows as trends.</p>'
         f'<ul class="notes">{notes}</ul>'),
        ('press', 'Press and speech: how an entry is filed',
         '<p>Every entry names who said it: a union, a prisoners\' group, a press-freedom monitor, a wire agency, a court. Counts '
         'carry the date of the count. When two monitors disagree, we print both. We do not publish footage a fact-checker has '
         'found to be altered, not even as a still.</p>'),
        ('grades', 'Grades', '<p>Every state is drawn from the same net: a cell that holds, thins or tears, a single knot, a run '
                             f'of knots, a loose end, two threads paused.</p>{grade_table()}'),
        ('photos', 'Photographs',
         '<p>Photographs come from Wikimedia Commons under open licences. Each shows the person, the place or the thing in the '
         'entry, captioned with where and when it was taken. Without an honest photograph, an entry carries its grade instead.</p>'),
        ('corrections', 'Corrections',
         '<p>We correct errors in the open. A corrected entry says what changed and when, and the change is listed here.</p>'
         '<p class="empty">No corrections in this edition.</p>'
         '<p>To ask for one, write to <a href="mailto:corrections@palestineonline.co">corrections@palestineonline.co</a> with the '
         'entry\'s address and what is wrong.</p>'),
    ], 'How the board is read, graded and corrected, and what it cannot tell you.')


def about_page():
    prose('about.html', 'Who we are', "Palestine Online reports the status of Palestine's networks and the safety of its press.", '', [
        ('name', 'The name and the net',
         '<p class="ar-word"><span lang="ar" dir="rtl">شبكة</span></p>'
         '<p>In Arabic one word, <span lang="ar">شبكة</span> (shabaka), means a fishing net and a phone or internet network. In '
         'Gaza, when the signal is gone, people say there is no shabaka. The keffiyeh carries the fisherman\'s net in its weave.</p>'
         '<p>Our mark is a hash sign, the sign of online speech, turned forty-five degrees until it becomes one cell of that net: '
         'two threads each way, four knots. The knot at the top is in sea blue. It is the one that answers.</p>'),
        ('what', 'What we do',
         '<p>We read the networks every day, we log what happens to the people who report, and we keep both on one board, '
         'because each depends on the other. A reporter without a signal cannot file; a network with no one reporting on it '
         'goes dark twice.</p>'),
        ('who', 'Who we are',
         '<p>Palestine Online is an independent desk. This page belongs to a prototype: the staff list and contact details will '
         'be filled in by the team before launch.</p>'),
        ('contact', 'Contact',
         '<p>Tips and corrections: <a href="mailto:desk@palestineonline.co">desk@palestineonline.co</a>. To tell us where the '
         'network is down, use <a href="report.html">the outage form</a>.</p>'),
    ], "An independent desk that reads Palestine's networks and logs the safety of its press, every day, from named sources.")


def form_page(path, title, desc, lede, form, side=''):
    body = f'''<div class="wrap">
{crumbs('', [(title, None)])}
<header class="d-head pr-head"><h1>{esc(title)}</h1><p class="d-line">{esc(lede)}</p></header>
<div class="form-grid"><div class="form-main">{form}</div>{side}</div>
</div>
'''
    page(path, title, desc, body, '', '', 'p-form')


def alerts_page():
    groups = ''.join(f'<label class="check"><input type="checkbox" name="row" value="{g["key"]}" checked><span><b>{esc(g["title"])}</b>'
                     f'<small>{len(g["rows"])} rows · {esc(g["by"])}</small></span></label>' for g in ED['board'])
    sample = next((r for r in ED['board'][0]['rows'] if r['status'] == 'restored'), ED['board'][0]['rows'][0])
    form = f'''<form class="big-form" action="alerts.html" method="get">
<label><span class="lbl">Email address</span><input type="email" name="email" autocomplete="email" required placeholder="you@example.org"></label>
<fieldset><legend class="lbl">Send me a line when these rows change state</legend>{groups}</fieldset>
<fieldset><legend class="lbl">How often</legend>
<label class="radio"><input type="radio" name="pace" value="now" checked><span>The moment a row changes</span></label>
<label class="radio"><input type="radio" name="pace" value="day"><span>Once a day, at 09:00 in Gaza</span></label></fieldset>
<button class="btn" type="submit">Subscribe</button>
<p class="fine">A prototype: this form sends nothing and stores nothing.</p>
</form>'''
    side = f'''<aside class="mail" aria-label="What an alert looks like"><p class="lbl">What an alert looks like</p>
<div class="mail-card"><p class="m-from">{mark_svg('mark m-mark')}<b>Palestine Online</b><span>alerts@palestineonline.co</span></p>
<p class="m-subj">{chip(sample["status"])}<b>{esc(sample["name"])}</b></p>
<p>{esc(sample["ctx"])}</p><p class="m-src">{esc(sample["src"])} · {esc(sample["at"])}</p>
<p class="m-foot">One line per change. Nothing else.</p></div></aside>'''
    form_page('alerts.html', 'Status alerts', 'One email when a row changes state.',
              'One email when a row on the board changes state: an outage in Gaza, a journalist detained, a platform takedown. Nothing else.',
              form, side)


def report_page():
    places = ['North Gaza', 'Gaza City', 'Deir al-Balah', 'Khan Younis', 'Rafah', 'Jenin', 'Tulkarm', 'Nablus', 'Qalqilya',
              'Salfit', 'Ramallah and al-Bireh', 'Jericho', 'Jerusalem', 'Bethlehem', 'Hebron', 'Tubas']
    opts = ''.join(f'<option>{p}</option>' for p in places)
    form = f'''<form class="big-form" action="report.html" method="get">
<div class="two"><label><span class="lbl">Where</span><select name="where" required><option value="">Choose a place</option>{opts}</select></label>
<label><span class="lbl">Network</span><select name="net"><option>Paltel (fixed line)</option><option>Jawwal (mobile)</option><option>Ooredoo Palestine (mobile)</option><option>An Israeli network</option><option>An eSIM</option><option>Not sure</option></select></label></div>
<fieldset><legend class="lbl">What stopped working</legend>
<label class="check"><input type="checkbox" name="what" value="data"><span><b>Mobile data</b></span></label>
<label class="check"><input type="checkbox" name="what" value="calls"><span><b>Calls and SMS</b></span></label>
<label class="check"><input type="checkbox" name="what" value="fixed"><span><b>Home or office internet</b></span></label></fieldset>
<div class="two"><label><span class="lbl">Since</span><input type="text" name="since" placeholder="For example: today, 14:20"></label>
<label><span class="lbl">How to reach you (optional)</span><input type="text" name="contact" autocomplete="off" placeholder="Email or phone"></label></div>
<label><span class="lbl">Anything else</span><textarea name="note" rows="4"></textarea></label>
<button class="btn" type="submit">Send the report</button>
<p class="fine">A prototype: this form sends nothing. A real report is checked against IODA before it reaches the board.</p>
</form>'''
    side = '''<aside class="mail"><p class="lbl">What happens next</p><ol class="steps">
<li><b>We check IODA</b><span>A report becomes a row only when a measurement agrees.</span></li>
<li><b>We ask a second person</b><span>Someone in the same place, on another network.</span></li>
<li><b>We never print your name</b><span>Reports are kept for seven days, then deleted.</span></li></ol></aside>'''
    form_page('report.html', 'Report an outage', 'Tell us where the network is down.',
              'Tell us where the network has gone. We check every report against IODA before anything reaches the board.', form, side)


def archive_page():
    by = {}
    for s in STORIES:
        by.setdefault(s['date'], []).append(s)
    days = ''
    for d in sorted(by, reverse=True):
        items = ''
        for s in by[d]:
            p = s.get('photo')
            img = (f'<img src="assets/img/photo/{p["slug"]}.webp" alt="" loading="lazy" width="200" height="133">' if p
                   else f'<span class="rc-ph" aria-hidden="true">{glyph(s["status"], "pl-gl")}</span>')
            items += (f'<li class="ar-item"><a href="report/{s["id"]}.html">{img}<span class="ar-t">{chip(s["status"])}'
                      f'<span class="desk">{esc(DESK[s["desk"]])}</span><b>{esc(s["headline"])}</b></span></a></li>')
        days += f'<section class="ar-day"><h2><time datetime="{d}">{esc(day_long(d))}</time></h2><ul>{items}</ul></section>'
    body = f'''<div class="wrap">
{crumbs('', [('Archive', None)])}
<header class="d-head"><h1>Archive</h1><p class="d-line">Every entry on the board, newest first. {len(STORIES)} entries.</p></header>
{days}
</div>
'''
    page('archive.html', 'Archive', 'Every entry on the board, by date.', body, '', '', 'p-archive')


def search_page():
    idx = [{'id': s['id'], 't': s['headline'], 's': s['summary'], 'd': s['date'], 'k': s['desk'], 'st': s['status'],
            'p': s.get('place') or '', 'n': ' '.join(s.get('people') or []),
            'img': s['photo']['slug'] if s.get('photo') else ''} for s in STORIES]
    write('assets/data/search.json', json.dumps(idx, ensure_ascii=False, separators=(',', ':')))
    chips = ''.join(f'<button type="button" class="f-chip" data-desk="{k}" aria-pressed="false">{esc(v)}</button>'
                    for k, v in DESK.items())
    body = f'''<div class="wrap">
{crumbs('', [('Search', None)])}
<header class="d-head"><h1>Search</h1><p class="d-line">Every entry, by name, place, desk or word.</p></header>
<form class="search-box" role="search" action="search.html"><label for="q" class="sr">Search the board</label>
<input id="q" name="q" type="search" placeholder="A name, a place, a word" autocomplete="off">
<div class="f-chips" role="group" aria-label="Filter by desk">{chips}</div></form>
<p class="s-count" role="status" aria-live="polite"></p>
<ul class="results"></ul>
<script type="application/json" id="chips">{json.dumps({k: chip(k) for k in STATUS}, ensure_ascii=False)}</script>
</div>
'''
    page('search.html', 'Search', 'Search every entry on the board.', body, '', '', 'p-search', extra_js=('search.js',))


def simple_pages():
    prose('privacy.html', 'Privacy', 'What this prototype stores.', '', [
        ('stores', 'What we store',
         '<p>Nothing about you. This prototype sets no cookies and loads no trackers or third-party scripts. Your browser keeps '
         'two small notes for this site only: whether you chose the day or the night page, and whether you have already seen '
         'the net cast in this session.</p>'),
        ('forms', 'Forms',
         '<p>The alert and outage forms on this prototype send nothing. On the live site, outage reports will be kept for seven '
         'days, then deleted, and never published with a name.</p>'),
    ], 'This prototype keeps nothing about you.')
    photos = []
    cred = os.path.join(ROOT, 'assets', 'img', 'photo', 'CREDITS.md')
    if os.path.exists(cred):
        for line in open(cred, encoding='utf-8'):
            m = re.match(r'- `([^`]+)` — \[([^\]]+)\]\(([^)]+)\) · (.*)', line.strip())
            if m:
                photos.append(f'<li><a href="{esc(m.group(3))}" rel="noopener" target="_blank">{esc(m.group(2))}</a>'
                              f'<span>{esc(m.group(4))}</span></li>')
    prose('credits.html', 'Credits', 'Data, photographs and type.', '', [
        ('data', 'Data', '<p>Network rows: IODA, Internet Outage Detection and Analysis, © Georgia Tech Research Corporation. '
                         'Read 24 October 2026.</p>'),
        ('photos', 'Photographs', f'<ul class="credits">{"".join(photos) or "<li>Listed here once the edition is built.</li>"}</ul>'),
        ('type', 'Type', '<p>Schibsted Grotesk by Bakken &amp; Bæck for Schibsted; Azeret Mono by Displaay; Handjet by Rosetta; '
                         'Beiruti by Boutros. All under the SIL Open Font License, self-hosted and cut to the characters this '
                         'site uses.</p>'),
    ], 'Who made what you see on the board.')


def not_found():
    rel = SITE
    body = f'''<div class="wrap nf">
<div class="nf-net" aria-hidden="true">{net_svg(88, 52, 3, cls='net nf-svg', cols=11)}</div>
<div class="nf-text"><p class="lbl">404 · Not routed</p><h1>This page fell through the net.</h1>
<p>The address you followed has no path to it. It may have moved, or it was never here.</p>
<p class="nf-go"><a class="btn" href="{rel}home.html">Back to the board</a><a class="more" href="{rel}search.html">Search the board <span aria-hidden="true">→</span></a></p></div>
</div>
'''
    write('404.html', head('Not found', 'This page fell through the net.', rel, '404.html', 'p-404') + strip(ED, rel)
          + mast(rel, '') + f'<main id="main">\n{body}</main>\n' + foot(rel) + scripts(rel))


def main():
    for s in STORIES:
        story_page(s)
    for key in DESK:
        desk_page(key)
    for r in ED['board'][0]['rows']:
        row_page(r)
    method_page()
    about_page()
    alerts_page()
    report_page()
    archive_page()
    search_page()
    simple_pages()
    not_found()
    print(len(STORIES), 'entries,', len(DESK), 'desks,', len(ED['board'][0]['rows']), 'rows')


if __name__ == '__main__':
    main()
