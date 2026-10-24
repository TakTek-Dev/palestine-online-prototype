"""Choose one Commons photo per entry from the research, and the brand-story photos.

python -I tools/photopick.py   -> tools/photos.json (then run tools/photos.py to fetch them)
The first photo the researcher listed is the one they judged closest to the entry.
"""
import glob
import json
import os
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {                # entry ids whose photo was judged not close enough to the entry on review
    'el-gouna-citizen-osama-golden-star',   # shows another director from the same festival
    'addameer-files-seized-ramallah-raid',  # shows a hospital gate, not Addameer's office
    'rsf-bayeux-memorial-2026',             # same memorial already carries the Bayeux prize entry
}
PLACE = {               # photos that show the place, not the person or the event: cropped wide on entry pages
    'ashtiyeh-beaten-aqraba', 'atiq-abed-detained-anza', 'ribeiro-deported-rantis', 'heidi-levine-beaten-abu-falah',
    'arrests-after-levine-attack', 'hazem-nasser-released', 'saleh-shawka-arrested', 'naqaa-hamed-released',
    'kafr-ad-dik-home-camera-footage-seized', 'tuqu-schools-flags-bethlehem-student-phone',
    'pps-field-interrogations-phones-seized', 'settlers-whatsapp-stop-the-harvest',
    'pps-incitement-surveillance-al-eizariya-principal', 'murtaja-killed-gaza-city', 'deir-samit-arrest-october-7-anniversary-post',
}
BRAND = {               # brand-story photos: slug -> Commons file name
    'nets-gaza': 'Gaza_Sea_Port_12.jpg',
    'keffiyeh-net': 'Kuffieyeh_(cropped).PNG',
    'hirbawi': 'Palestinian_keffiyeh_loom.jpg',
}


def entry(p):
    url = p['file']
    title = unquote(url.split('/wiki/', 1)[1]).replace('_', ' ')
    year = (p.get('taken') or '')[:4]
    cap = p['caption'].rstrip('.')
    tail = f" Photo: {p['author']} / Wikimedia Commons, {p['licence']}."
    return {'file': title, 'page_url': url, 'author': p['author'], 'license': p['licence'], 'date': p.get('taken', ''),
            'alt': cap, 'caption': cap + '.' + tail, 'place': p.get('place', ''), 'year': year}


out = {}
DROP = set(json.load(open(os.path.join(ROOT, 'tools', 'curate.json'), encoding='utf-8')).get('drop', []))
for f in sorted(glob.glob(os.path.join(ROOT, 'research', 'news-*.json'))):
    for n in json.load(open(f, encoding='utf-8')):
        if n['id'] in SKIP or n['id'] in DROP or not n.get('photos'):
            continue
        out[n['id']] = entry(n['photos'][0])
        out[n['id']]['kind'] = 'place' if n['id'] in PLACE else 'subject'
bp = os.path.join(ROOT, 'research', 'brand-photos.json')
if os.path.exists(bp):
    pool = json.load(open(bp, encoding='utf-8'))
    for slug, name in BRAND.items():
        p = next((p for p in pool if p['file'].endswith('/File:' + name)), None)
        if p:
            out[slug] = entry(p)
json.dump(out, open(os.path.join(ROOT, 'tools', 'photos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'photos chosen')
