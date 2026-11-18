# news-image-20261117 — notes

Entry: a pure-stdlib Python program (`main.py`) that draws a 1024x1024
front-page image summing up Tuesday 17 November 2026 world news.

## The six stories (researched 2026-11-18 ~00:00 WIB, from that day's reporting)

1. EUROPE - CONFLICT: Ukraine strike collapses a road span of the Kerch
   Bridge to Crimea; Russian missiles hit two bridges over the Dnipro in Kyiv.
2. MIDDLE EAST - ENERGY: Two oil tankers hit mines near the Strait of
   Hormuz; a third US carrier (USS Theodore Roosevelt) arrives in the region.
3. ASIA - DIPLOMACY: Trump arrives in Manila for the ASEAN summit; Xi, Trump
   and Putin are set to meet Thursday in Shenzhen on the APEC sidelines.
4. EUROPE - MIGRATION: Five EU states (Germany, Denmark, Austria, Greece,
   Netherlands) announce a joint migrant return hub in Rwanda.
5. SPACE - TECHNOLOGY: A ULA Vulcan rocket fails in flight, destroying 40
   Amazon Leo internet satellites.
6. BUSINESS - TECH: JPMorgan Chase blames a software bug, not a cyberattack,
   for Monday's banking outage (online banking, branches, Zelle).

## Verification (local, 2026-11-18 ~00:07 WIB)

- `python3 -m py_compile main.py`: OK.
- Two runs with different output dirs: byte-identical entry.png,
  sha256 f730667f2c9570ff27d46e33137c331d15dee35a6bd58674e3e2be969b91b50d.
- PNG valid (signature + IHDR 1024x1024), 39,410 bytes (cap 1,048,576).
- Rendered image inspected visually: masthead date legible, all six
  headlines + subheads legible, scenes read (bridge gap, tanker, flags,
  stars+arrow+pin, rocket, bank+lightning).
- Fixes applied after first render: tanker hull redrawn as a flat hull with
  a bow instead of a sloped triangle; bank pediment flipped to apex-up.

## Repo

- jekglory/news-image-20261117, PUBLIC, MIT (SPDX line), created
  2026-11-18T00:08:36Z (after the 2026-11-17T23:43:00Z opening).
- Files: main.py, LICENSE, README.md, NOTES.md, .makefun/owner.json.
