"""Compose tools/edition.json for one day from the research files.

python -I tools/edition.py
  research/ioda.json      IODA daily medians for Gaza and the West Bank (read 24 Oct 2026)
  research/news-*.json    sourced entries for the five desks
  tools/curate.json       which entries make the board rows, the counts and the creators band
"""
import glob
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(ROOT, *p)  # noqa: E731

DAY = '2026-10-24'
READ_UTC, READ_LOCAL = '09:30', '12:30'      # IODA data to about 09:30Z; Gaza is UTC+3 until 31 Oct

io = json.load(open(R('research', 'ioda.json'), encoding='utf-8'))
gz, wb = io['regions']['Gaza Strip'], io['regions']['West Bank']


def daily(region, sig):
    return [(d['date'], d['median']) for d in region['daily_24_sep_to_24_oct_2026'][sig]]


g_bgp, g_ping = daily(gz, 'bgp'), daily(gz, 'ping-slash24')
w_bgp = daily(wb, 'bgp')
pre_g = round(gz['baseline_1_6_oct_2023']['bgp']['mean'])
pre_ga = round(gz['baseline_1_6_oct_2023']['ping-slash24']['mean'])
pre_w = round(wb['baseline_1_6_oct_2023']['bgp']['mean'])
today_r, today_a = int(g_bgp[-1][1]), int(round(g_ping[-1][1]))
first_r = int(g_bgp[0][1])
w_today = int(w_bgp[-1][1])


def days_since(iso):
    return (date.fromisoformat(DAY) - date.fromisoformat(iso)).days


def alert_bars(dates, hits):
    return {'bars': [1] * len(dates), 'hits': [i for i, (d, _) in enumerate(dates) if d in hits]}


gaza_alert_day = '2026-09-16'
wb_blip_day = '2026-10-13'
DATES = [d for d, _ in g_bgp]

network_rows = [
    {'code': 'gz-routed', 'status': 'degraded', 'name': 'Gaza · routed address blocks',
     'ctx': f'Blocks the wider internet can still reach. {first_r} on 24 September, {today_r} since 9 October.',
     'reading': str(today_r), 'unit': f'{round(today_r / pre_g * 100)}% of pre-war', 'spark': [v for _, v in g_bgp],
     'ref': pre_g, 'src': 'IODA · BGP', 'at': f'24 Oct, {READ_UTC} UTC', 'href': 'row/gz-routed.html'},
    {'code': 'gz-answering', 'status': 'down', 'name': 'Gaza · blocks answering probes',
     'ctx': 'Blocks with at least one device replying to a ping. Seven to nine every day this month.',
     'reading': str(today_a), 'unit': f'about {round(today_a / pre_ga * 100)}% of pre-war', 'spark': [v for _, v in g_ping],
     'ref': pre_ga, 'src': 'IODA · active probing', 'at': f'24 Oct, {READ_UTC} UTC', 'href': 'row/gz-answering.html'},
    {'code': 'gz-alerts', 'status': 'steady', 'name': 'Gaza · last outage alert',
     'ctx': '35 minutes of lost routes from 04:10 UTC. The one before, on 14 August, lasted 70.',
     'reading': '16 Sep', 'unit': f'{days_since(gaza_alert_day)} days without an alert',
     'spark': alert_bars(g_bgp, set()), 'src': 'IODA · outage alerts', 'at': f'24 Oct, {READ_UTC} UTC',
     'href': 'row/gz-alerts.html'},
    {'code': 'wb-routed', 'status': 'steady', 'name': 'West Bank · routed address blocks',
     'ctx': f'Above the {pre_w:,} it had before the war, and flat all month.',
     'reading': f'{w_today:,}', 'unit': 'above pre-war', 'spark': [v for _, v in w_bgp], 'ref': pre_w,
     'src': 'IODA · BGP', 'at': f'24 Oct, {READ_UTC} UTC', 'href': 'row/wb-routed.html'},
    {'code': 'wb-blip', 'status': 'restored', 'name': 'West Bank · routing dip before dawn',
     'ctx': '60 of 3,016 blocks dropped from the routing tables at 05:25 local time and came back at 05:55.',
     'reading': '13 Oct', 'unit': '30 minutes, then back', 'spark': alert_bars(w_bgp, {wb_blip_day}),
     'src': 'IODA · outage alerts', 'at': '13 Oct, 02:55 UTC', 'href': 'row/wb-blip.html'},
]

lead = {
    'id': 'gaza-net', 'desk': 'networks', 'kicker': 'Analysis · our reading of IODA data', 'at': f'24 Oct, {READ_UTC} UTC',
    'chips': [['degraded', 'Routing degraded'], ['down', 'Answering down']],
    'headline': f"Gaza's internet by IODA's count: {today_r} of {pre_g} pre‑war address blocks routed, eight answering",
    'dek': ("IODA, the outage observatory at Georgia Tech, counts blocks of internet addresses, not people. "
            "Read as a trend, the count says how much of Gaza's network the rest of the internet can still reach."),
    'paras': [
        f"Routed blocks rose this month, from {first_r} in the last week of September to 151 on 4 October and "
        f"{today_r} on 9 October, and have held there since. Answering blocks have not moved: seven to nine on every "
        f"day of the month, against about {pre_ga} on 1–6 October 2023.",
        "There has been no outage alert for Gaza since 16 September. The West Bank, measured the same way, has held "
        "flat apart from a 30-minute routing dip before dawn on 13 October.",
    ],
    'source': (f"IODA signals for the Gaza Strip (region 1226) and West Bank (4581), daily medians 24 Sep – 24 Oct 2026, "
               f"read 24 Oct, {READ_UTC} UTC. Pre-war levels are means over 1–6 Oct 2023."),
    'net': {'prewar': pre_g, 'routed': today_r, 'answering': today_a, 'prewar_answering': pre_ga,
            'days': [[d, int(r), int(round(a))] for (d, r), (_, a) in zip(g_bgp, g_ping)]},
}

ed = json.load(open(R('tools', 'edition.json'), encoding='utf-8'))
ed.update({'date': DAY, 'read_utc': READ_UTC, 'read_local': READ_LOCAL, 'lead': lead,
           'spark_from': '24 Sep', 'spark_to': '24 Oct'})
groups = {g['key']: g for g in ed['board']}
groups['networks'] = {'key': 'networks', 'title': 'Networks', 'by': 'IODA, Georgia Tech', 'rows': network_rows}

news = []
for f in sorted(glob.glob(R('research', 'news-*.json'))):
    news += json.load(open(f, encoding='utf-8'))
if news and os.path.exists(R('tools', 'curate.json')):
    cur = json.load(open(R('tools', 'curate.json'), encoding='utf-8'))
    by = {n['id']: n for n in news}
    photos = json.load(open(R('tools', 'photos.json'), encoding='utf-8')) if os.path.exists(R('tools', 'photos.json')) else {}
    stories = []
    for n in news:
        n['status'] = cur.get('status', {}).get(n['id'], n['status'])
        n.update(cur.get('fix', {}).get(n['id'], {}))
    for n in sorted((n for n in news if n['id'] not in cur.get('drop', [])), key=lambda n: n['date'], reverse=True):
        s = {k: n.get(k) for k in ('id', 'desk', 'status', 'date', 'published', 'place', 'headline', 'summary', 'body',
                                   'people', 'source', 'via', 'url', 'more_urls', 'reading', 'reading_unit',
                                   'reading_note', 'background', 'area')}
        src = n.get('source') or n.get('via') or ''
        own = [t.strip() for t in src.split(';')]
        via = '; '.join(t for t in (x.strip() for x in (n.get('via') or '').split(';')) if t and t not in own and t != src)
        s['via'] = via
        s['byline'] = src + (f', via {via}' if via else '') + f" · {int(n['date'][8:])} {date.fromisoformat(n['date']).strftime('%b')} 2026"
        s['outlet'] = n.get('via')
        if n['id'] in photos:
            s['photo'] = {'slug': n['id'], 'alt': photos[n['id']]['alt'], 'caption': photos[n['id']]['caption'],
                          'kind': photos[n['id']].get('kind', 'subject')}
        stories.append(s)
    ed['stories'] = stories
    for key, rows in cur['rows'].items():
        title = {'press': 'Press safety', 'speech': 'Speech & evidence', 'platforms': 'Platforms', 'creators': 'Creators'}[key]
        out = []
        for r in rows:
            n = by[r['id']]
            out.append({'code': n['id'], 'status': n['status'], 'name': r['name'], 'ctx': r['ctx'],
                        'reading': r.get('reading', n.get('reading') or ''), 'unit': r.get('unit', n.get('reading_unit') or ''),
                        'kind': r.get('kind', 'Single event'), 'src': r.get('src', n.get('source') or n.get('via')),
                        'at': r.get('at', date.fromisoformat(n['date']).strftime('%-d %b') if os.name != 'nt' else f"{int(n['date'][8:])} {date.fromisoformat(n['date']).strftime('%b')}"),
                        'href': f"report/{n['id']}.html"})
        groups[key] = {'key': key, 'title': title, 'by': cur['by'][key], 'rows': out}
    ed['counts'] = cur.get('counts', ed.get('counts', []))
    ed['front'] = cur.get('front', [])
    if cur.get('lead_story'):
        ed['lead']['href'] = f"report/{cur['lead_story']}.html"
    ed['creators'] = cur.get('creators', [])
    ed.pop('provisional', None)

ed['board'] = [groups[k] for k in ('networks', 'press', 'speech', 'platforms', 'creators') if k in groups]
json.dump(ed, open(R('tools', 'edition.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('edition', DAY, 'gaza', today_r, today_a, 'stories', len(ed['stories']), 'groups', [g['key'] for g in ed['board']])
