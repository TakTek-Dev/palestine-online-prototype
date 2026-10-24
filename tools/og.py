"""Link card, app icon and manifest.

python -I tools/og.py   -> tools/out/og.html, tools/out/icon.html (then shot.mjs renders them to assets/og.png, apple-touch-icon.png)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build as B  # noqa: E402
from common import NAME, ROOT, brand, chip, esc, mark_svg, write  # noqa: E402
from net import net_svg  # noqa: E402

L = B.ED['lead']
n = L['net']
css = '<link rel="stylesheet" href="../../assets/css/po.css">'
write('tools/out/og.html', f'''<!doctype html><html lang="en" data-theme="day"><head><meta charset="utf-8">{css}
<style>html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#F4F2EB}}
.og{{display:grid;grid-template-columns:600px 600px;height:630px}}
.l{{padding:56px 56px 50px;display:flex;flex-direction:column;justify-content:space-between}}
.l .mark{{width:44px;height:44px}}.l .word{{height:26px}}.l .brand-s{{font-size:12px;margin-top:9px}}
h1{{margin:0;font:760 46px/1.06 var(--sans);letter-spacing:-.032em}}
.s{{display:flex;gap:10px;align-items:center;font:500 14px var(--mono);color:#5C6066}}
.r{{background:#FCFBF7;border-left:1px solid #D8D4C9;padding:56px 48px;display:flex;flex-direction:column;justify-content:center;gap:14px}}
.r .headrope{{font-size:13px}}
.js .net:not(.torn) .k.gone{{fill:none}}</style></head><body><div class="og">
<div class="l">{brand('', 'brand', tag='div')}<h1>{esc(L["headline"])}</h1><p class="s">{chip("down", "Answering down")}IODA · {esc(L["at"])}</p></div>
<div class="r"><p class="headrope"><span>Headrope</span> {n["prewar"]} blocks before the war</p>{net_svg(n["prewar"], n["routed"], n["answering"], cls="net torn", note=True)}</div>
</div></body></html>''')
write('tools/out/icon.html', f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=180">{css}
<style>html,body{{margin:0;width:180px;height:180px;background:#121315;display:grid;place-items:center}}
.mark{{width:118px;height:118px;color:#F4F2EB}}.mark .kn.lit{{fill:#6AB0F2}}</style></head><body>{mark_svg()}</body></html>''')
write('manifest.webmanifest', json.dumps({
    'name': NAME, 'short_name': NAME, 'description': 'The status of the press and the networks in Palestine.',
    'start_url': 'home.html', 'display': 'standalone', 'background_color': '#F4F2EB', 'theme_color': '#121315',
    'icons': [{'src': 'apple-touch-icon.png', 'sizes': '180x180', 'type': 'image/png'},
              {'src': 'favicon.svg', 'sizes': 'any', 'type': 'image/svg+xml'}]}, indent=1))
print('og.html, icon.html, manifest')
