# REVIEW — round 2

## 1. Verdict

**Ship after the listed fixes.** The poster's structure, typography and build are close to the contract, but the three-computer diagram contains a wrong data-flow arrow, the task drawing does not support the reach and sightlines it implies, and several Pass fields and automated checks do not test what they claim. These are concrete, local fixes; none requires a new concept or layout.

**Counts:** 1 Blocker, 13 Major, 3 Minor (17 findings).

## 2. Findings, ordered by severity

Severity: **Blocker** = false science, misleads a student, or breaks the contract; **Major** = clearly weakens understanding or beauty; **Minor** = polish.

### 2-A1 — The `datasets` link is drawn bidirectional
- **Severity:** Blocker
- **Area:** A (truth) / D (contract)
- **Location:** Band C, panel 1, `lerobot-roadmap.svg:84-86`; rendered at x 58–96 mm, y 225 mm; `.tmp/review/C_left-1.png`.
- **Observed:** The Station Orin → DGX Spark link has a head at *both* ends: the SVG polygon at `57.1,224.923` points left into Station Orin and the one at `97.4,224.923` points right into DGX Spark. The same line is labelled `datasets`. BRIEF §4 says `Station Orin → DGX Spark` for datasets; the trained policy return is the separate line below. The student sees data flowing back from the Spark to the station, duplicating the policy-return meaning.
- **Fix:** Remove the left head from the datasets link (or use a one-way arrow Station → Spark). Keep two heads only on the trained-policies return.
- **Status:** Verified (SVG coordinates and rendered crop).

### 2-A2 — The drawn arm cannot reach the cup or button in the pose shown
- **Severity:** Major
- **Area:** A (truth / physical plausibility)
- **Location:** Band C, panel 2, `lerobot-roadmap.svg:100-120`; build note `elbow 125.8 deg, reach 31.34`; `.tmp/review/lidar300b.png`.
- **Observed:** With the build's own coordinates, arm base/shoulder at (32.5, 18.5) in drawing units, cup centre at (87, 9.6), button at (103.6, 11.8). The maximum arm reach is 31.34 mm; the distances are 55.22 mm and 71.41 mm. The chassis front is at U=52 and the near table leg at U=74, so the base can advance at most about 22 mm before the leg; even then the cup is about 33 mm away (just beyond reach) and the button is about 49 mm away. In the drawn pose the gripper is over the table's near edge but nowhere near the cup; the button is across the table at the wall. The poster's headline promises both actions.
- **Fix:** Either lengthen the arm/links or bring the table, cup and button into the drawn workspace; or show separate, dimensioned press/pick poses. A sentence that the drawing is schematic would not be enough for a poster that otherwise computes its geometry.
- **Status:** Distances and maximum reach Verified; that this is a defect (rather than acceptable schematic licence) is Judgment.

### 2-A3 — The cup occludes the button from both cameras
- **Severity:** Major
- **Area:** A (truth) / B (learning design)
- **Location:** Band C, panel 2, `lerobot-roadmap.svg:91-103` and `123-128`; `.tmp/review/lidar300b.png`.
- **Observed:** The head-camera lens is at U=23.4, V=6.8; the cup body spans U 84–90, V 5.2–14.0; the button is at U=103.6, V=11.8. The head-camera line to the button is at V≈10.6–11.0 across the cup, i.e. straight through the cup, and the cup top (V=5.2) is above the camera lens (V=6.8). The wrist camera is similarly low and its line to the button also crosses the cup. The ±30° check in `check_map.py` only measures the axis, not line of sight, so it passes. Stage 10 asks the student to "confirm the light"; Stage 6 presses the button. With the cup in place, neither camera can see the button in this pose.
- **Fix:** Raise the head camera above the cup top (or move the cup aside/lower the button), and check unobstructed sightlines to both the cup and the button, not only angles. If the cup is meant to be placed only after the button press, state that sequencing.
- **Status:** Geometry Verified; the effect on the task is Judgment.

### 2-A4 — The lidar copy says it sees the button panel, but the drawing's ray stops at the table leg
- **Severity:** Major
- **Area:** B (learning design) / A (truth of the illustration)
- **Location:** Band C, panel 2 copy `lerobot-roadmap.svg:388` versus ray/leg/panel `lerobot-roadmap.svg:106,96,93`; `.tmp/review/C_mid-1.png`.
- **Observed:** The bullets say `Sees: walls, the button panel, table legs, people's legs.` In the pose drawn, the only ray stops at the near table leg (x=235) before the panel (x=262.2); the panel is expressly described in BRIEF §3 as occluded by that leg. The illustration teaches occlusion while the adjacent bullet says the lidar sees the panel. A student can reasonably conclude either that the ray reaches the panel or that the panel is irrelevant.
- **Fix:** Qualify the bullet: `Sees: walls, table legs, people's legs; the button panel only when no leg is in the way.` Or add a second short ray that reaches the panel from another position. BRIEF §4 copy is the source of the contradiction; the professor should approve the qualifier.
- **Status:** Drawing geometry Verified; the pedagogical contradiction is Judgment.

### 2-B1 — Stage 9 has no measurable Pass and omits the prompt action
- **Severity:** Major
- **Area:** B (learning design)
- **Location:** Stage 9, `lerobot-roadmap.svg:324-329`.
- **Observed:** Stage 9 is `One model, two tasks`. Learn mentions `language prompts`; Do only says fine-tune `smolvla_base` and serve it; it never says to define or use the two prompts that select the tasks. Pass says `Compared with your two ACT policies on both tasks. Either result is fine if explained.` There is no trial count, metric, or evidence requirement. A student cannot tell when the stage is passed, and the two-task behaviour has no stated input.
- **Fix:** Add the operational step (`run both prompts, e.g. "press the button" and "pick up the cup"`), and make Pass countable (`on 20 trials per task, log successes and latency; either result is acceptable if explained`).
- **Status:** Copy and omission Verified; severity Judgment.

### 2-B2 — Stage 3's Pass does not test the stage's actual skill
- **Severity:** Major
- **Area:** B (learning design)
- **Location:** Stage 3, `lerobot-roadmap.svg:251-259`.
- **Observed:** Learn is scan timing, masking the body, reducing to 16 sectors; Do is adding `lidar.s00`–`lidar.s15` and stopping `x.vel`; Pass only drives at a wall and checks a 15 cm stop. A student can pass by implementing the stop without ever producing or validating 16 sector distances. The safety behaviour is essential, but it is not the observation skill the stage claims to teach.
- **Fix:** Require a log of 16 finite sector floats at the expected rate and a masked body sector, plus the stop test.
- **Status:** Copy Verified; severity Judgment.

### 2-B3 — Calibration and joint limits are named but never assigned
- **Severity:** Major
- **Area:** B (learning design)
- **Location:** Stage 2, `lerobot-roadmap.svg:240-248`; safety label `lerobot-roadmap.svg:211`.
- **Observed:** Stage 2 Learn includes `calibration`, but the Do only writes the robot class and the Pass only tests e-stop/watchdog and a 1 m square. The global safety rule says `joint and speed limits set`, but no stage says to identify motors, set zeros/signs, record joint limits, or calibrate the arm and wheels. A student who has never used LeRobot could write a class that passes the square test while the 6+1 arm is uncalibrated or its limits unset.
- **Fix:** Add calibration and limit recording to Stage 2 Do and Pass (e.g. every joint moves in the commanded direction within its recorded limits; e-stop and watchdog 5/5).
- **Status:** Copy Verified; severity Judgment.

### 2-B4 — The 7/2/16 structure of the state bar is not visible without counting
- **Severity:** Major
- **Area:** B (learning design)
- **Location:** Band A, time-step bars, `lerobot-roadmap.svg:20-52`; `.tmp/review/A_right-1.png`.
- **Observed:** The state bar has 25 segments with group gaps of 0.9 mm versus 0.35 mm inside groups; the action bar has 9 with a 7/2 split. There are no group labels, brackets or ticks. The student sees a black barcode and must count 25 segments and compare gaps to recover 7/2/16. The adjacent note states the counts, but the bar itself, which the brief says should make the vector structure visible, does not.
- **Fix:** Add small group brackets/ticks labelled `7 arm`, `2 base`, `16 lidar` (and `7 arm`, `2 base` for action), or separate the groups with a clear whitespace gap and a single legend. The brief's "bar and note" should carry the structure, not only the note.
- **Status:** Segment counts/gaps Verified; severity Judgment.

### 2-C1 — The left end of the snake is a 180° hairpin, with the safety bracket squeezed inside it
- **Severity:** Major
- **Area:** C (beauty / route readability)
- **Location:** Band B, left return, `lerobot-roadmap.svg:59`; `.tmp/review/st6b.png`.
- **Observed:** The return runs left at y=148.871, turns down at x=26.4, goes to x=24, descends to y=153.772, then turns back right to station 6 at x=30. That is a narrow U-turn, not a single 45° chamfer into station 6. The row-2 safety bracket starts at x=26.4, y=152.622, inside the U. At page scale the result is a small magenta hook with an orange line trapped in it; it interrupts the "one continuous journey" reading exactly where the line should turn into the second row.
- **Fix:** Replace the notch with one clean 45° descent from the return line into station 6 (or a vertical descent into the station), and let the safety bracket sit clearly above it. Keep the station-6 disc on the route.
- **Status:** Path and bracket coordinates Verified; visual effect Judgment.

### 2-C2 — Station 10's "double ring" is not visible
- **Severity:** Major
- **Area:** C (beauty) / D (contract)
- **Location:** Band B, station 10, `lerobot-roadmap.svg:74-75`; `.tmp/review/st10b.png`.
- **Observed:** The outer ring has r=3.0 and a 0.5 mm black stroke; the disc has r=2.7. The white gap between disc edge (2.7) and ring inner edge (2.75) is only 0.05 mm, under one pixel at 300 dpi. The rendered station reads as a single black disc with the number `10`; the required terminus cue is effectively absent. The `10` itself is white and legible.
- **Fix:** Make a real double ring: e.g. a 0.6–0.8 mm white gap and an outer black ring at r≈3.4, or a white inner ring within the disc. Add a check for the gap, not just the existence of a `stn-ring` element.
- **Status:** Coordinates/gap Verified; visual absence Verified in the 300 dpi crop.

### 2-C3 — Band C panel 3 floats while panel 1 is packed
- **Severity:** Major
- **Area:** C (whitespace rhythm)
- **Location:** Band C, `How to master it`, `lerobot-roadmap.svg:393-403`; build note `band C natural bottoms 276.10, 274.52, 267.85, target 276.10`; `.tmp/review/C_left-1.png` and `C_right-1.png`.
- **Observed:** Panel 1's setup copy uses 3.19–4.25 mm leading; panel 3's five single-line rules sit on 8.696 mm baselines (241.317, 250.013, 258.710, 267.407, 276.103). The build log confirms panel 3 naturally ends at 267.85 mm and is stretched to the common 276.10 mm bottom. The result is a visibly airy right panel next to a dense left panel, with the bullets looking like a list of footnotes rather than a ladder.
- **Fix:** Add a short second column or a short explanatory line per rule, or reduce the rule spacing and give panel 3 a deliberate internal block. Do not force the common bottom by stretching only the bullets; the common bottom can be met by content.
- **Status:** Baselines and build note Verified; visual Judgment.

### 2-D1 — The automated checks do not inspect the `datasets` direction
- **Severity:** Major
- **Area:** D (engineering / check integrity)
- **Location:** `src/check_map.py:770-808` (check 19) and `src/check_map.py:903-950` (check 10).
- **Observed:** Check 19 collects only elements with a `data-head` attribute; only the trained-policies return heads have that attribute. The top `datasets` link has two unlabelled heads and is never inspected. I built a temp copy with the datasets link corrected to one head: `check_map.py` still passed all checks. Thus the current wrong double-headed link passes the official suite, and a future regression in that link would too.
- **Fix:** Add a geometry check for panel-1 flow links: Robot↔Station has two heads; Station→Spark has exactly one head at Spark; Spark→both Orins has exactly two heads at the Orins, and no third.
- **Status:** Verified by source inspection and a temp build/check.

### 2-D2 — The checks do not require Station 10 to be a double ring
- **Severity:** Major
- **Area:** D (contract check)
- **Location:** `src/check_map.py:631-642` (stations) and `src/check_map.py:950-1070` (robot/geometry); `lerobot-roadmap.svg:74`.
- **Observed:** Check 9 verifies eleven discs 0–10; check 10 verifies the metro line; check 13 verifies grid; none checks the `stn-ring` or its gap. I removed the `stn-ring` from a temp source, rebuilt, and `check_map.py` passed all checks. The rendered deliverable still has the ring, but it is 0.05 mm from the disc, so the check would not protect the terminus cue even if it existed.
- **Fix:** Assert a `stn-ring` at station 10 with an outer radius at least 0.6 mm greater than the disc and a visible white gap; sample the rendered pixels or compute the geometry.
- **Status:** Verified by temp build/check and geometry.

### 2-D3 — Check 6 tests palette membership, not the declared role of each text colour
- **Severity:** Major
- **Area:** D (check integrity)
- **Location:** `src/check_map.py:492-526`.
- **Observed:** Check 6 only rejects fills outside `TEXT_COLORS`; it never asserts that `Pass` is ink/demi, that `Explain` is muted, that times are muted, or that the safety label is safety. A build in which `Pass` was muted would still pass, despite BRIEF §3's "Pass must be findable at a glance (demi weight, ink)." The current poster is correct, but the check cannot detect the regression it claims to guard.
- **Fix:** Build an expected style map from `content.py` or block IDs (`s-*-pass` -> ink/600; `s-*-explain` -> muted/400; `safety-label` -> safety; station numbers -> white/600) and assert it exactly.
- **Status:** Code Verified; no temp mutation needed (the condition is explicit).

### 2-C4 — Ladder arrows are prefixes, not joins, and sit 0.8 mm from the next heading
- **Severity:** Minor
- **Area:** C (beauty / diagram syntax)
- **Location:** Band C, panel 3, `lerobot-roadmap.svg:129-133`; `.tmp/review/p3top.png`.
- **Observed:** The three arrows are 1.2 mm shafts at x=311.3–313.7, 343.8–346.2, 376.3–378.7. Each tip is 0.8 mm before the next heading (314.5, 347.0, 379.5), while the preceding definition (`The command works.`) ends at 305.9, 5.4 mm to the left. The arrow is therefore much closer to the heading than to the step it is supposed to join and reads as a `→ Explain it` prefix; it does not read as four joined steps.
- **Fix:** Place each arrow at the midpoint of the inter-column gap (or draw one thin connecting rule with arrowheads at the column seams), with ≥1.5 mm clearance to both heading and preceding definition.
- **Status:** Coordinates Verified; visual Judgment.

### 2-C5 — The header rule and the safety label are both too close to neighbouring type
- **Severity:** Minor
- **Area:** C (beauty / alignment)
- **Location:** Header, `lerobot-roadmap.svg:11,141`; Band B, `lerobot-roadmap.svg:199,211`; `.tmp/review/bhead.png`.
- **Observed:** The subtitle's descender box ends at y=31.534; the header rule is at y=31.682, only 0.148 mm below it. The rule reads as an underline on the `p`/`g` descenders rather than a separator. In Band B the safety label (`Before any motor moves…`) and the 4.4 mm `The roadmap` heading share baseline y=86.356, 144 mm apart; the safety label appears as a small right-hand continuation of the section heading. The label is only 1.2 mm above its bracket.
- **Fix:** Lower the header rule by about 1 mm, or raise the subtitle; give the safety label its own baseline above the bracket (or place it under the heading at x=12) so it is clearly an annotation, not part of the heading line.
- **Status:** Bboxes and baselines Verified; visual effect Judgment.

### 2-D4 — Residual engineering and contract defects
- **Severity:** Minor
- **Area:** D (engineering / contract)
- **Location:** `src/check_map.py:741-751` (check 17); `src/build_map.py:1248-1251` (render deletion); `lerobot-roadmap.html:10-11` (XML declaration); Band C panel 2 (`lerobot-roadmap.svg:91-127`; `CODER_REPORT.md` §7).
- **Observed:**
  - **Check 17 is weaker than its label.** `NUM_END` only flags a line ending in a bare number; it does not flag a line that ends `1 m` and leaves the noun `square` on the next line, which is exactly what Stage 2 does (`A 1 m` / `square closes…`; `lerobot-roadmap.svg:246-247`). The check reports “no line ends between a number and its unit or noun”, but the noun case is not tested.
  - **Only PDF and PNG are deleted before rendering.** `render_outputs()` unlinks `OUT_PDF` and `OUT_PNG`; the SVG and HTML are overwritten later. If `assemble()` or `b.svg()` raises before the writes, stale SVG/HTML remain. The brief says the build “deletes old outputs first”; the stale-PDF requirement is met, the general statement is not.
  - **The inline HTML carries the standalone XML declaration.** `<?xml version="1.0" encoding="UTF-8"?>` appears inside `<body>`; browsers tolerate it, but it is invalid HTML content and unnecessary in the inline wrapper.
  - **The lidar figure is 30.4 mm tall, not “about 110 × 45”.** `CODER_REPORT.md` §7 states 110 × 30.4 and explains the choice; the figure is legible, but it is a deliberate contract deviation, and it is why the three labels around the ray are the tightest on the page.
- **Fix:** (a) add a phrase-level number/unit/noun glue and check, not only a bare-number regex, and rephrase to `a 1 m square path`; (b) unlink all four outputs before rendering; (c) strip the XML declaration when interpolating into the HTML shell; (d) either widen the drawing/band C or renegotiate the “about 45 mm” figure with the professor.
- **Status:** Code, HTML and report statements Verified; severity Judgment.

## 3. What I tried to break and could not

- **Clean build:** Copied `src/` and `BRIEF.md` to `.tmp/review/rebuild/`, ran `src/build_map.py`, and compared all four outputs. SVG, HTML, PDF and PNG were byte-identical to the deliverables; the originals' hashes were unchanged. This is stronger than the brief requires.
- **Automated text checks:** Re-ran `check_map.py`; 271 text elements, no bbox overlaps, no out-of-bounds text, minimum font 2.45 mm, and no text under a shape except the station numbers (which are correctly topmost on their discs). My independent Chrome probe found the same, plus only the intended station-number/metro contacts and the 0.15 mm subtitle-rule near-contact.
- **Line-crossing check:** I injected a horizontal line through the Band A lead in a temp source; `check_map.py` failed check 5 with many crossing samples. The check is not disabled for ordinary strokes.
- **Palette/colour:** Computed fills are only ink, muted, safety and white; no off-palette text colour; all white numbers are on phase-coloured discs.
- **Missing-ring and one-way-datasets temp builds:** Both were accepted by `check_map.py` (see D1 and D2); these are the two gaps I could break.
- **PDF facts:** `pdffonts` shows only AvenirNext-Regular, AvenirNext-DemiBold and Menlo-Regular; one A3 landscape page; selectable text. I did not find a font fallback.

## 4. Uncertain factual claims (not scored as findings)

Round 1 reports external checks for LeRobot v0.6.0, JetPack 7.2/Python 3.12 on Orin, and the 30 h SmolVLA example; I did not independently reproduce those sources. I found no specific contradiction, and I treated my own memory as insufficient proof. The claims I could check independently — the 19-week sum, 25/9 vectors, the 56% product, the Wilson interval and the picture geometry — are handled above; the only uncertainty I would still ask the professor to re-confirm is that the v0.6.0 dependency set installs cleanly on AGX Orin from the stated recipe, because the poster itself says the recipe was tested on Orin NX. That is a request for confirmation, not a finding.

## 5. Round 1 accepted findings — resolution check

I read `REVIEW_round1.md` only after writing the findings above. Status is based on the current rendered files, not the coder's report.

| Round-1 ID | Accepted requirement | Status in this build | Evidence |
|---|---|---|---|
| **D1** | Remove the hidden text-width cache; delete outputs; check Chrome; clean build reproducible | **Resolved in substance; one residual.** The `.tmp/measure.json` cache is gone; a fresh temp copy of `src/` + `BRIEF.md` rebuilt all four outputs byte-identically in my own test (SVG/HTML/PDF/PNG hashes matched; originals unchanged). Check 18 also passes. Residual: only PDF/PNG are unlinked before rendering, not SVG/HTML (2-D4 (b)). | My `.tmp/review/rebuild` hashes; `src/build_map.py:1248-1251`. |
| **B1** | Stage 2 must tell the student to integrate head and wrist cameras | **Resolved.** Stage 2 Do now says `both cameras`; check 8 and the rendered `s-2-do` carry it. | `lerobot-roadmap.svg:242-244`. |
| **C1** | One strict column grid across A, B and C; check panel/heading edges | **Resolved.** Band A and C panels/headings are at 12, 156, 282; stage columns at 30 + 63·i; check 13 passes. | `PANEL_X = [12,156,282]`; SVG headings/panel edges. |
| **C2** | Band C panel bottoms within 0.5 mm and ≥3 mm above footer | **Resolved.** Rendered last boxes are all 276.90 mm; footer top 280.02 mm; 3.12 mm clear; check 20 passes. The fix stretches panel 3’s rules and creates the density issue in 2-C3. | `.tmp/review/audit.json`; `lerobot-roadmap.svg:393-403`. |
| **A1** | Brief asked for both a panel/wall hit and a leg hit; leg occludes panel | **Partially resolved.** BRIEF §3 now says the panel is occluded by the table leg, and the drawing/ray is honest. BRIEF §4 still says `Sees: … the button panel`, and the panel is visible in the drawing; the copy/pose contradiction remains as 2-A4. | BRIEF §3 vs §4; `lerobot-roadmap.svg:388,106,96,93`. |
| **C3** | “After the mission” on the row-2 title baseline | **Resolved.** `after-head`, `stage-title-9`, `stage-title-10` all have baseline 163.222 mm. | `lerobot-roadmap.svg:332,343`. |
| **C4** | “One time step” notes not ragged | **Resolved.** All four notes start at x=320.5, the bar origin; the video notes no longer float at the right margin. | `lerobot-roadmap.svg:190-197`. |
| **C5** | Wrist camera bracketed; floor trimmed at wall | **Resolved.** `wrist-bracket` is vertical from the camera to the forearm; floor ends x=267.00 at the wall x=267.00. | `lerobot-roadmap.svg:91-92,126`. |
| **D2** | Checks as wide as their names: A tables, phase colours, one grid, every glyph, solids | **Resolved for the named items, with new gaps.** Check 8 now parses the A tables; check 6 checks station phase; check 13 checks headings/panels; check 4 samples every glyph; check 11 samples every solid. It still misses the `datasets` direction, the Station-10 ring and per-text colour roles (2-D1–2-D3). | `src/check_map.py`; temp-build tests. |

**Round-1 items that are genuinely fixed:** D1 (cache/reproducibility), B1, C1 (band seams), C2 (bottoms), C3, C4, C5, and the named D2 items. **Not fully fixed:** A1’s copy half (2-A4), and D1’s “delete the four outputs” clause (2-D4 (b)).

## 6. Discrepancies between CODER_REPORT.md and reality

Read last, after all findings above.

1. **“Check 8 parses all section 4 copy, per element” (CODER_REPORT §0, D2; §3).** Check 8 actually compares the 122 backticked strings as page-wide substrings (`page = norm(doc["pageText"]); missing = …`) and parses the A tables and stage blocks. It does not verify a per-element location for the header, footer, Band C roles, or ladder copy; a moved/duplicated string would still satisfy it. The report’s “per element” is true for the tables/stages, not for all copy. This is a check-coverage weakness, not a new rendering fault.
2. **“header rule 32.40” (CODER_REPORT §5).** The SVG and rendered rule are at y=31.682 mm, not 32.40 mm. The subtitle box ends at 31.534 mm, so the actual gap is 0.148 mm, not 0.86 mm; this is the 2-C5 near-contact, and the report’s number would hide it.
3. **“cup moved below lidar plane | 5” (CODER_REPORT §4 breakage table).** Check 5 is the text/stroke crossing test; a cup moved below the plane is a geometry/ray violation, which check 11 handles. The reported firing check is misattributed (the breakage may still have been caught; the table’s check number is wrong).
4. **“D1 done” and “delete outputs” (CODER_REPORT §0, §1).** The report says `render_outputs()` unlinks the PDF and PNG; that is true, but the accepted D1 requirement covered all four outputs. SVG/HTML are not unlinked before rendering; 2-D4 (b).
5. **“A1 done” (CODER_REPORT §0).** The brief’s §3 geometry is fixed, but the §4 bullet still says the lidar sees the button panel while the drawn ray stops at the leg. Calling A1 “done” overstates it; 2-A4 remains.
6. **“C2 done … the shorter panel breathes instead of floating” (CODER_REPORT §0).** The bottoms are aligned, but the build’s own note gives panel 3 a natural bottom at 267.85 mm and stretches it to 276.10 mm through 8.696 mm rule spacing. That is the density contrast in 2-C3, not a resolved visual issue.
7. **No discrepancy found** in the clean-build claim, the 19-week total, the 25/9 vector counts, the Wilson interval, the station phase colours, the fonts, the PDF page count/size, the selectable text, or the four output filenames. My independent rebuild reproduced all four outputs byte-for-byte.
