# Palestine Online — product notes

**What it is.** An English news site that reports, every day, whether Palestine's internet and phone networks can be reached and whether its journalists are safe to work, plus what happens to Palestinian speech, platforms and creators online. One board, five desks: Networks, Press safety, Speech & evidence, Platforms, Creators.

**Client brief.** No logo; identity built from zero. Three homepage samples were shown (Claude Design artifact, 7 Oct 2026): 1 · Signal (status board, Geist), 2 · Feed Check, 3 · Index. The client chose 1 · Signal. This prototype keeps Signal's structure (strip, tally, lead analysis, the board of graded rows with 30-day bars against the pre-war level, "behind the rows", alerts and method) and builds a full identity and site around it. None of the samples' fonts or colours are reused.

**Identity: «Shabaka».** شبكة means both a fishing net and a phone/internet network. The keffiyeh carries the fisherman's net. The mark is a hash sign turned 45° into one net cell (two threads each way, four knots); the top knot, in sea blue, is the one that answers. Every status glyph is drawn from the net (cell holds / sags / tears / mended; one knot; a run of knots; a loose end; two paused threads; a lit knot).

**The lead.** Gaza's 704 pre-war address blocks drawn as a net of 704 knots: routed blocks hold, answering ones are lit, the rest are the ghost of the pre-war net. Real IODA data, scrubbable over 30 days.

**Type.** Schibsted Grotesk (voice), Azeret Mono (instruments), Handjet ELSH 15 (counts drawn in knots), Beiruti (Arabic in running text).

**Colour.** Cotton #F4F2EB, thread #121315, sea #0D5BA1 (night #0F1012 / #6AB0F2); status red #B0261D, amber #8A5000, green #1C6A45.

**Build.** `python -I tools/fonts.py` → `brand.py` → `edition.py` → `photopick.py` → `photos.py` → `build.py` → `pages.py` → `book.py`. Never hand-edit the HTML. Bump `V` in tools/common.py on any asset change.
