"""Commons photos -> colour WebP, shown as they are.

python -I tools/photos.py   (reads tools/photos.json, writes assets/img/photo/*.webp + CREDITS.md + tools/out/photos.json)

tools/photos.json maps a slug to a Commons file and the alt/caption the site prints (curated by hand
from research/photos.json). Photos are shown in their own colour, resized to 1000 px and nothing else.
"""
import io, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'img', 'photo')
os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'PalestineOnline-prototype/1.0 (TakTek design prototype; en.developer2 at gmail)'}
STANDARD = [500, 960, 1280, 1920]
NEED = 1000


def api(title, width):
    q = urllib.parse.urlencode({'action': 'query', 'titles': title, 'prop': 'imageinfo', 'iiprop': 'url|size',
                                'iiurlwidth': width, 'format': 'json', 'formatversion': 2})
    req = urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + q, headers=UA)
    for attempt in range(6):
        try:
            return json.load(urllib.request.urlopen(req, timeout=40))['query']['pages'][0]
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(10 + attempt * 10)
    raise SystemExit('Commons API keeps throttling: ' + title)


def fetch(url):
    for attempt in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:
            print('  retry', attempt + 1, e)
            time.sleep(3 + attempt * 4)
    raise SystemExit('could not fetch ' + url)


def main():
    use = json.load(open(os.path.join(ROOT, 'tools', 'photos.json'), encoding='utf-8'))
    only = set(sys.argv[1:])
    meta, credits = {}, []
    for slug, p in use.items():
        out = os.path.join(OUT, slug + '.webp')
        if not os.path.exists(out) and not (only and slug not in only):
            ii = api(p['file'], NEED)['imageinfo'][0]
            url = ii['url'] if ii['width'] <= NEED else ii['thumburl']
            img = Image.open(io.BytesIO(fetch(url)))
            img = ImageOps.exif_transpose(img).convert('RGB')
            img.thumbnail((NEED, NEED))
            img.save(out, 'WEBP', quality=76, method=6)
            print(slug, img.size, os.path.getsize(out) // 1024, 'KB')
            time.sleep(3)
        if not os.path.exists(out):
            continue
        im = Image.open(out)
        meta[slug] = {'w': im.size[0], 'h': im.size[1]}
        credits.append(f"- `{slug}.webp` — [{p['file'][5:]}]({p['page_url']}) · {p['author']} · {p['license']} · "
                       f"{p.get('date', '')} · resized, colour as taken")
    os.makedirs(os.path.join(ROOT, 'tools', 'out'), exist_ok=True)
    json.dump(meta, open(os.path.join(ROOT, 'tools', 'out', 'photos.json'), 'w', encoding='utf-8'), indent=1)
    open(os.path.join(OUT, 'CREDITS.md'), 'w', encoding='utf-8').write(
        '# Photo credits\n\nAll photographs from Wikimedia Commons, used under the licences below. '
        'Each is captioned on the site with its real date and place.\n\n' + '\n'.join(credits) + '\n')


if __name__ == '__main__':
    main()
