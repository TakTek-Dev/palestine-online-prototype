"""The net: one knot for each address block Gaza's network had before the war.

Knots sit on a diamond lattice, row by row from the headrope down. The first `routed`
knots hold (the routing tables still carry a path to them); `answering` of those are lit
(a device in the block replies to IODA's probes); the rest are drawn as the ghost of the
pre-war net. Position is order, not geography: IODA's blocks are not placed on a map.

The same drawing is made in the browser by knit() in assets/js/po.js, which redraws it
for each day of the scrubber and with fewer columns on phones.
"""

import json

COLS, DX = 32, 20
DY = DX / 2


def lattice(n, cols):
    rows = -(-n // cols)
    pts = []
    for i in range(n):
        r, c = divmod(i, cols)
        pts.append((c * DX + (r % 2) * DX / 2 + DX / 2, r * DY + DY))
    return pts, rows


def neighbours(i, n, cols):
    r, c = divmod(i, cols)
    cand = [(r + 1, c - 1), (r + 1, c)] if r % 2 == 0 else [(r + 1, c), (r + 1, c + 1)]
    return [rr * cols + cc for rr, cc in cand if 0 <= cc < cols and rr * cols + cc < n]


def lit_set(routed, answering):
    """Spread the answering knots through the held part of the net, the same way every time."""
    if not answering:
        return set()
    step = routed / answering
    return {int(step * k + step * 0.5) for k in range(answering)}


def net_svg(prewar, routed, answering, cls='net', label='', days=None, note=False, cols=COLS):
    pts, rows = lattice(prewar, cols)
    lit = lit_set(routed, answering)
    w = cols * DX + DX / 2
    h = rows * DY + DY
    held_t, ghost_t, fray_t = [], [], []
    for i, (x, y) in enumerate(pts):
        for j in neighbours(i, prewar, cols):
            x2, y2 = pts[j]
            seg = f'M{x:.0f} {y:.0f}L{x2:.0f} {y2:.0f}'
            if i < routed and j < routed:
                held_t.append(seg)
            else:
                ghost_t.append(seg)
                if i < routed:
                    # the thread that held this knot to the next one, cut part way down; it hangs
                    fray_t.append(f'M{x:.0f} {y:.0f}Q{x + (x2 - x) * 0.3:.1f} {y + (y2 - y) * 0.45:.1f} '
                                  f'{x + (x2 - x) * 0.55:.1f} {y + (y2 - y) * 0.55 + 2.5:.1f}')
    edge = routed // cols
    rows_g = []
    for r in range(rows):
        ks = []
        for i in range(r * cols, min(prewar, (r + 1) * cols)):
            x, y = pts[i]
            kind = 'lit' if i in lit else ('held' if i < routed else 'gone')
            ks.append(f'<path class="k {kind}" d="M{x:.0f} {y - 4.2:.1f}l4.2 4.2-4.2 4.2-4.2-4.2z" '
                      f'data-x="{x:.0f}" data-y="{y:.0f}" data-i="{i}"/>')
        rows_g.append(f'<g class="nr" style="--d:{max(0, r - edge)}">{"".join(ks)}</g>')
    return (f'<svg class="{cls}" viewBox="0 0 {w:.0f} {h:.0f}" role="img" aria-label="{label}" '
            f'data-prewar="{prewar}" data-routed="{routed}" data-answering="{answering}" data-cols="{cols}" data-dx="{DX}"'
            + (f" data-days='{json.dumps(days, separators=(',', ':'))}'" if days else '') + '>'
            f'<path class="t ghost" d="{"".join(ghost_t)}"/>'
            f'<path class="t was" d="{"".join(ghost_t)}"/>'
            f'<path class="t held" d="{"".join(held_t)}"/>'
            f'<path class="t fray" d="{"".join(fray_t)}"/>'
            f'<g class="knots">{"".join(rows_g)}</g>{gone_label(prewar, routed, w, h, cols) if note else ""}</svg>')


def gone_label(prewar, routed, w, h, cols):
    """The size of the loss, written into the ghost of the net."""
    top = (routed // cols + 1) * DY + DY
    cy = (top + h) / 2 + 8
    return (f'<g class="gone-note" transform="translate({w / 2:.0f} {cy:.0f})">'
            f'<text class="gn-n" y="0" text-anchor="middle">{prewar - routed}</text>'
            f'<text class="gn-t" y="22" text-anchor="middle">blocks no longer routed</text></g>')
