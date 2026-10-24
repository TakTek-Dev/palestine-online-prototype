# Palestine Online — design system

## Idea
شبكة (shabaka) is one Arabic word for a fishing net and for a phone or internet network. The keffiyeh carries the fisherman's net. Everything on the site is drawn from that net: the mark, the status glyphs, the lead chart, the selvage on the footer, the loader.

## Mark
A hash sign turned 45° into one net cell. Drawn on a 100-unit square before the turn: threads at ±17, running 11 past the knots (cut ends), thread 5.6, knot 10.4. Only the top knot changes colour (sea blue, `#0D5BA1`; night `#6AB0F2`). Never upright, never all knots lit, never coloured by status. Source of truth: `tools/brand.py` → `assets/brand/*.svg`, `favicon.svg`, `tools/out/marks.json`.

## Colour (`assets/css/po.css` `:root`)
| Token | Day | Night | Use |
|---|---|---|---|
| `--cotton` | #F4F2EB | #0F1012 | page |
| `--cloth` | #FCFBF7 | #17181B | panels, the board |
| `--thread` | #121315 | #F1EEE6 | ink, the net |
| `--sea` | #0D5BA1 | #6AB0F2 | the answering knot, links, the one button |
| `--down` / `--deg` / `--up` | #B0261D / #8A5000 / #1C6A45 | lighter set | status only |
| `--night-band` | #141517 | #08090A | counts band, footer, no-photo plates |

## Type
- Schibsted Grotesk 400–900: voice. Headlines 760, tracking −0.03em. Body 17–19 px / 1.6.
- Azeret Mono 300–700: sources, times, labels (uppercase, +0.08em).
- Handjet with `ELSH 15, wght 800` (`.kn-num`): counts drawn in diamond knots. Display sizes only (≥40 px).
- Beiruti: Arabic inside English text. Handjet `.kn-ar` for large Arabic display.

## Status glyphs (`common.glyph`)
Networks: down (torn cell), degraded (sagging cell, hollow knots), steady (whole cell), restored (cell with a sea knot).
Press & speech: incident (one knot), pattern (run of three knots), open (loose end), stalled (two paused threads), resolved (closed cell), recognised (lit knot in a ring).
Chips: `.st` + family class (`st-down`, `st-deg`, `st-up`, `st-sea`, `st-mute`); incident and pattern are outlined.

## The net as a chart (`tools/net.py`)
One knot per pre-war /24 block, 22 columns, diamond lattice, laid from the headrope down. First `routed` knots hold; `answering` of them are lit (spread evenly); the rest are a dashed ghost with their count written in. Order, not a map. JS `knit()` in `po.js` redraws any day for the scrubber.

## Motion
Cast (loader, once per session, `?loader` forces), tear (lead net whole, then torn), mend (scrub), ping (one answering knot rings every 1.5 s), tie (hover the name), rows' bars rise on view. All off under reduced motion.

## Layout
`.wrap` 1320 px, gutter 32 / 16 px. Board row grid: status 138 · name · reading 158 · bars 220 · source 176 · go 44. Phones: rows stack, long groups fold to three rows.
