# Coder report — Mobile Manipulator Learning Map (round 2)

Checklist. Every row is marked done only when verified in the final render; the
evidence column names how. Rows are filled in as the work is done, and the report
is rewritten from these rows at the end.

## Section 7 items (binding)

| # | Item | Done | Evidence |
|---|---|---|---|
| 1 | Camera aims at workspace; axis from lens to midpoint of button/object; both within ±30°; C x-axis along axis | | |
| 2 | All 5 joints drawn, counted, unlabelled; base pan turntable visible | | |
| 3 | Elbow 120–150°, ≤22 mm above shoulder, fit band, believable reach | | |
| 4 | Two targets: object block + table, frame O clear, labels object/button/battery/caster | | |
| 5 | H triad clear of button/gripper; wall top return removed; triads ~2 mm; camera reads as camera | | |
| 6 | COM recomputed; drop line inside support bracket | | |
| 7 | Four physics diagrams share frame: width, height, x offset, position vs title/formula | | |
| 8 | No-sideways slash 0.25 mm, 4 mm long | | |
| 9 | COM panel: wheel rectangles + caster mark at apex labelled; 5–6 mm solid arrow; COM label clear | | |
| 10 | Constraints panel: fingertip, contact dot, approach axis, free ring around axis, one figure | | |
| 11 | Friction: arrows from contact faces inside block; one μF_n; both F_n; ≥ has real glyph | | |
| 12 | STIX for variables/digits only; words in sans | | |
| 13 | Route starts at station 0, ends at station 8, terminus double ring, no end bar | | |
| 14 | Phase colour changes at a station edge, no split link | | |
| 15 | Row baselines = row label y; ≥3 mm clear between Learn/Build and Build/Pass in every column | | |
| 16 | One column grid for A/B/C, named constants; C rebalanced; shared row pitch | | |
| 17 | Runtime loop closes: return starts under Physics, arrowhead lands on Sense label, 3 mm above rates | | |
| 18 | Safety sentence inside loop panel, ≥5 mm before "How you improve it" | | |
| 19 | Development cycle return starts and ends on its labels | | |
| 20 | build_map.py always renders every output | | |
| 21 | Check 5 tests every polygon closing edge | | |
| 22 | Check 8 reads copy from BRIEF.md §4/§7; each stop's strings in its own column, in order | | |
| 23 | Check 6 tests white number against its own disc colour | | |
| 24 | Added checks: SVG attrs, HTML @page, PNG scale, station numbers ≥ body, stroke weights, five joints, camera ±30°, pdffonts fallback | | |
| 25 | aria-label on each equation group | | |
| 26 | .tmp cleaned at end of build except measurement cache | | |

## Review findings (rejected list excluded)

| ID | Finding | Done | Evidence |
|---|---|---|---|
| B1 | Camera points away from workspace | | |
| M1 | Four Pass cells had no threshold (copy now has numbers) | | |
| M2 | Safety had no check/time (stop 2 pass now carries it) | | |
| M3 | 6→7 jump / hours (stop 7 now 6 weeks; stop 0 3 weeks) | | |
| M4 | COM panel lost contacts, 1.5 mm stub | | |
| M5 | Safety sentence read as next panel heading | | |
| M6 | Runtime loop did not close | | |
| M7 | Band C 140/171/68, squeezed, uneven pitch | | |
| M8 | Check 5 closing edge | | |
| M9 | Check 8 compared page to content.py | | |
| M10 | Default build left a stale PDF | | |
| m1 | Phase colour changed mid-link | | |
| m2 | Route began in mid-air, ended in a bar | | |
| m3 | Three row labels 0.27 mm low | | |
| m4 | Toolbelt cell crammed | | |
| m5 | Friction arrows crossed the block outline | | |
| m6 | Prohibition slash read as an arrowhead | | |
| m7 | Battery unlabelled, wall return, triads too big | | |
| m8 | "Keep batteries low" claim (copy now correct) | | |
| m9 | Twenty unexpanded names (footer now covers it) | | |
| m10 | Prose set in the maths face | | |
| m11 | Title 13 mm beat the route (now 11 mm) | | |
| m12 | ≥ fell back to Times New Roman | | |
| m13 | Equations do not copy/paste (aria-label; limit stated) | | |
| m14 | Contrast tested against wrong disc; missing attribute checks | | |
