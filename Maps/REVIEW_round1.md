# Review: The LeRobot Learning Roadmap

I rendered the PDF at 110, 300 and 600 dpi with `pdftoppm`, viewed the whole page and crops of every band, the lidar drawing and the three-computer flow, and measured the rendered HTML independently in headless Chrome (`.tmp/review/measure.py`, standard library only). I also rebuilt the project in clean and cached temp copies under `.tmp/review/`.

## 1. Verdict

Ship after the listed fixes: the printed A3 page is scientifically sound and close to the brief, and the route reads as one journey. Do not rework the design, but close the camera-integration gap, put the three bands on one column grid, and make a clean build reproduce; the shipped PDF currently depends on a hidden `.tmp/measure.json` cache.

## 2. Findings, ordered by severity

Evidence marked Verified is measured or derived from the rendered files and code; the severity and the aesthetic adjectives (e.g. "crammed", "floating", "reads as separate") are judgment. Where a finding turns on copy, the quoted text is verified.

### D1 — Blocker — D — The build is not reproducible from a clean copy; a hidden text-width cache decides the line breaks

**Location:** `src/build_map.py:1070-1086` (`render_outputs`, `main`) and `.tmp/measure.json`; deliverables `lerobot-roadmap.svg/html/pdf/png`.

**Evidence (Verified):** I copied the project twice. With the original `.tmp/measure.json`, `python src/build_map.py` reproduces all four deliverables byte-for-byte (SHA-256 SVG `ba05…`, HTML `d433…`, PDF `363c…`, PNG `0af1…`). With an empty `.tmp` (a clean checkout), the same source produces a different SVG (`7d36…`), HTML (`91f0…`), PDF (`d73d…`) and PNG (`0e95…`). The clean build rewraps stage 4 Learn and Pass, stage 6 Pass, stage 9 Do, stage 10 Do, the After list and the footer; the footer becomes two lines (second baseline 283.24) instead of one. The author's `src/check_map.py` passes both builds, and check 15 only compares mtimes, so it cannot see this. The same `main` also calls Chrome without checking its return code and without unlinking old outputs, so a failed print can leave the old PDF and exit 0.

**Fix:** remove the hidden cache dependency. Measure text in the actual SVG/browser at the rendered size (or version and validate the cache), delete the four outputs before rendering, check Chrome's return code, and add a clean-build check that rebuilds in a fresh temp directory and compares the four files. Rebuild the shipped files from that clean state.

### B1 — Major — B — No stage says to add the head and wrist cameras to the robot class, but stage 4's Pass already needs them

**Location:** `src/content.py:81` (stage 2 Do), `src/content.py:105,107` (stage 4 Do/Pass), `src/content.py:111` (stage 5 Do); `BRIEF.md:192,206-208,213`; poster Band B row 1 columns 3, 5, 6.

**Evidence (Verified):** Stage 2's Do lists "6+1 joints, x.vel, theta.vel, hardware e-stop and watchdog" and no cameras. Stage 4's Pass is "You complete both tasks 9 of 10 times, watching only the camera feeds." Stage 5's Do only says "Fix camera mounts and lighting. Record 10 test episodes…" — it assumes the cameras are already in the robot's observations. Band A shows `observation.images.wrist` and `head` as dataset features, and the hardware includes both cameras, but no Learn/Do field tells the student to wire them into `get_observation()` or the robot class before the stage-4 camera-feed test. A student following only the Do fields has no instruction to integrate them; the stage-4 Pass assumes the integration has already happened. This is a weakness in the brief's final copy, not a false statement on the poster.

**Fix (brief):** add "and the wrist and head cameras" to stage 2's Do, or add "add both cameras to the robot class" to stage 5's Do and move the camera-feed test after it. Also state that the camera names are frozen before recording. If the brief is immutable, the student needs a note beside stage 4.

### C1 — Major — C — The "one strict column grid for all bands" is not met: A, B and C use three different column systems

**Location:** `src/build_map.py:65-67` (`A_L/A_M/A_R = 12/178/296`), `src/build_map.py:90-92` (`C_L/C_M/C_R = 12/146/286`), `src/build_map.py:74` (`COL0/COLW`, stage fields at 38.2/100.5/162.9/225.2/287.5/349.9); headings in `lerobot-roadmap.svg`; `BRIEF.md:28`.

**Evidence (Verified):** The Band A headings are at x = 12, 178, 296; the Band C headings at x = 12, 146, 286. "The five parts" and "What one lidar plane sees" are both middle columns but are 32 mm apart; "One time step in your dataset" and "How to master it" are both right columns but 10 mm apart. The Band B stage columns are at 38.2, 100.533, 162.867, 225.2, 287.533, 349.867: the Band C middle edge at 146 is 16.9 mm left of the stage-2 edge, and the Band A middle edge at 178 is 15.1 mm right of it. The vertical seams do not run through the page, so the bands read as three separate layouts rather than one Swiss grid. `src/check_map.py:571-592` only tests Band B's stage fields and stations, so it reports "one grid" while this is true.

**Fix:** derive the Band A and Band C panel boundaries from the same six-column grid as Band B (use spans of the stage grid, or at least one common left edge for the middle and right panels, and one common gutter). Then add a check that every band heading and panel edge lies on that one set of x constants.

### C2 — Major — C — Band C's bottom is crammed in the middle panel and floats in the right panel

**Location:** Band C bottom: last line of "What one lidar plane sees" (`LeRobot has no lidar class…`, line box bottom 277.04) vs footer right (line box top 277.62); last rule of "How to master it" (line box bottom 272.20); footer left (top 277.62); `src/build_map.py` `build_band_c`.

**Evidence (Verified):** The last lidar-copy line overlaps the footer horizontally from x = 250 to 264 and has only 0.58 mm between its line box and the footer's line box (about 1.3 mm of ink gap). The left panel's last setup line ends at 276.20; the middle panel at 277.04; the right panel's last rule at 272.20. So the middle panel is 0.8 mm lower than the left, the right is 4.8 mm higher, and the right panel has a visible empty band above the footer while the middle nearly touches it. This is the crammed/floating contrast the brief warns against.

**Fix:** raise the lidar drawing or its copy by about 2 mm, increase the right panel's rule spacing (or add a final line) so its last baseline matches the left/middle, align all three panel bottoms, and keep at least 3 mm between the lowest Band C line box and the footer.

### A1 — Minor — A (brief) — The brief asks for both a panel/wall hit and a leg hit, but the leg occludes the panel

**Location:** `BRIEF.md:104-105` (the panel "extends down across the lidar plane, so the plane visibly ends on the panel or wall" and later "choose the leg as the visible hit"); the drawing ray from u = 51.5 to the leg at u = 70, panel at u = 101.5–106.

**Evidence (Verified):** The panel does cross the plane (panel v = 9.8–21.6, plane v = 20.9), and the button is above it (v = 12), but the first table leg at u = 70 is between the lidar and the panel and also crosses the plane. A single horizontal ray cannot hit both; the drawn ray correctly stops at the leg. The poster's choice is physically honest, but the brief's first sentence ("so the plane visibly ends on the panel or wall") is not satisfied; the copy's "Sees: … the button panel" is only a general statement, not this pose. This is a brief contradiction, not a drawing error.

**Fix (brief):** say that the panel crosses the plane but is occluded by the leg in this view; either state that the lidar sees the leg here, not the panel, or add a second pose/view if the panel hit must be shown. Do not ask for both in one ray.

### C3 — Minor — C — "After the mission" sits 1.0 mm above the row-2 stage titles

**Location:** `src/build_map.py:762` (`at = row2_y[0] - TITLE_GAP2`); `lerobot-roadmap.svg` `after-head` baseline y = 163.301 vs `stage-title-9/10` y = 164.301.

**Evidence (Verified):** The probe's line-box tops are 159.597 for "After the mission" and 160.597 for "One model, two tasks"/"Run the mission"; the two headings use the same 3.6 mm size. The eye sees the sixth-column heading slightly high. The 7.6 mm `TITLE_GAP2` is there for the terminus ring, but the After column has no ring.

**Fix:** use `TITLE_GAP` (6.6) for the After heading, i.e. `at = row2_y[0] - TITLE_GAP`, so its baseline matches the stage titles.

### C4 — Minor — C — The "One time step" note column is ragged

**Location:** `src/build_map.py:573,578,581` (`BAR_X = A_R + 44.0`; video notes at `MR` right-aligned; state/action notes at `BAR_X`); Band A right panel.

**Evidence (Verified):** The two `video` notes occupy x = 401.74–408 (flush to the page margin), while the `25 numbers…` and `9 numbers…` notes and both bars start at x = 340. The video rows therefore float at the far right, the state/action rows start at the bar origin, and the table's right edge is ragged. The eye reads the video notes as a separate column.

**Fix:** put all notes at x = 340 (`BAR_X`), leaving the bar area empty for the video rows, or right-align every note to the bars' right edge (about 401.7). Do not mix the two alignments.

### C5 — Minor — C/A — Two drawing marks are unresolved: the wrist camera floats and the floor line runs past the wall

**Location:** `src/build_map.py:884` (`WRIST_CAM = (59.6, 9.3, 2.2, 1.1)`); `src/build_map.py:930` (`L(4, FLOOR_V, 108, FLOOR_V)` with `WALL_U = 106`); lidar drawing.

**Evidence (Verified):** At u = 59.6 the forearm is at v ≈ 11.35, while the wrist-camera rectangle ends at v = 10.4: a ≈ 0.95 mm gap (≈ 1.0 mm on paper), with no bracket. The head camera has a mast; the wrist camera has none, so it reads as floating. The floor line ends at u = 108, 2 mm to the right of the wall at u = 106, leaving a small stub beyond the wall/floor corner. The 600 dpi crop shows both.

**Fix:** add a short vertical bracket from the forearm/wrist to the wrist camera (or lower the camera to touch the forearm), and trim the floor line at `WALL_U` (or extend the wall to the drawing edge) so the corner is clean.

### D2 — Minor — D — Several checks are narrower than their names and miss contract regressions

**Location:** `src/check_map.py:442` (check 8), `src/check_map.py:394` (check 6), `src/check_map.py:571` (check 13).

**Evidence (Verified):** Check 8 parses backticked strings and the stage table but not the Band A "The five parts" or "One time step" table cells; a temp copy with "Your hardware…" changed to "Your device…" still passes check 8 (the lead-sentence change was caught because the lead is backticked). Check 6 accepts any palette fill for a station disc and does not test the stage's phase colour; a wrong-phase disc would pass. Check 13 only tests the Band B stage fields and stations, so it passes the A/C grid mismatch in C1. The current outputs do satisfy the actual invariants — I verified the disc fills (0–1 blue, 2–5 green, 6–9 magenta, 10 ink), the ray, the copy and the stage fields — so this is a regression/contract risk, not a current false claim.

**Fix:** parse all section 4 tables and copy blocks; test the ray against every solid rectangle/circle; map each station to its stage phase and assert the disc fill; check every band heading/panel edge against the one grid.

## 3. What I tried to break and could not

- **Vector arithmetic:** `observation.state` is 7 + 2 + 16 = 25; `action` is 7 + 2 = 9. The rendered state bar has exactly 25 segments grouped 7/2/16 and the action bar 9 grouped 7/2, with one segment width (2.05). The notes match. Verified.
- **Wilson interval:** 8/10 gives 0.4903–0.9435, i.e. 49–94%; the copy's "49–94%" is correct. Verified.
- **Stage times and stage-10 target:** 1+1+3+1+2+1+2+3+2+2+1 = 19 weeks. Stage 10's 6/10 is 60%, consistent with 16/20 × 14/20 = 56% before retries. Verified.
- **Prerequisites:** stage 6 needs 2–5; stage 8 needs a trained policy from 6/7 and the powered leader arm introduced in stage 4; stage 10 needs 6 and 7. All point backward. Stage 4's teleop Pass can be done before recording (it is a human teleoperation test), provided the cameras are integrated (B1). Stage 8's powered leader is available from stage 4 and Band C; the stage-8 On field includes Station Orin. No forward reference found.
- **Three-computer node labels:** all three labels sit on the same baseline and use the same offset (x = node + 2.3, y = node + 3.7); the apparent DGX Spark offset is only its longer text, not a different rule. No fault.
- **On fields vs the three computers:** stages 0–10 match the roles; DGX Spark is never in the real-time loop; the Band C flow's "trained policies" return goes to Station Orin, which serves large policies. The stage 6/7 On chain "Station Orin → Spark → Robot Orin" reads as a work order, not a direct cable; the stage 9 On shows the full return. I did not find a false claim.
- **Lidar drawing:** the ray starts at the puck and ends on the first table leg; the cup, tabletop and button are above the plane; the leg and panel cross it; the ray passes through no solid. The panel is occluded by the leg (A1), and the author correctly chose the leg. The head camera axis points at the workspace and both cup and button are within ±30°; the elbow is 144.2°; there are six joint marks; the gripper clears the table by ≈1.05 mm; the wheel and caster are tangent to the floor. The drawing is plausible apart from C5.
- **Text:** independent Chrome measurements found no line-box or ink-box overlaps, no text painted under a shape (every character centre), no stroked line/path/polygon edge crossing a text box, and no text outside x 12–408 / y 12–285 except the title's line box at y = 11.99 (0.01 mm over the 12 mm line; the ink is inside, and the check's tolerance accepts it). Minimum declared size is 2.45 mm; text fills are ink, muted, safety and white station numbers only; contrast is ≥5.60:1.
- **Deliverables:** the SVG is 420 × 297 mm with `viewBox`, `<title>` and `<desc>`; the HTML contains the SVG exactly and declares `@page { size: A3 landscape; margin: 0 }`; the PDF is one A3 landscape page with selectable text; the PNG is 4761 × 3369 (3× A3 within rounding); the PDF/SVG/HTML text agrees; `pdffonts` shows only AvenirNext-Regular/DemiBold and Menlo-Regular; stroke weights are 0.25/0.5/0.8/1.6; there are no filters, gradients, patterns, images or external URLs (the only `http://` is the SVG namespace).
- **Facts I checked externally:** LeRobot v0.6.0 (July 2026), `lerobot-rollout`, `--strategy.type=dagger`, JetPack 7.2 with Python 3.12 on Orin, and the SmolVLA example "20,000 steps at batch 64 in about 30 h on a DGX Spark" are all supported by current sources. I found no specific reason to doubt the remaining hardware/software claims (`π0.5` in Spark memory, PyAV on ARM, no LeRobot lidar class), so I did not flag them.

## 4. Discrepancies between `CODER_REPORT.md` and reality

Read last, after the findings above were written.

1. **"no run can leave a stale PDF" and "Repeated builds produce byte-identical SVG and PDF" (report §1, §6).** True only in the current workspace, with the existing `.tmp/measure.json`. A clean copy without that cache produces a different SVG/HTML/PDF/PNG (SHA-256 SVG `7d36…` instead of `ba05…`), different line breaks and a two-line footer; `main` also ignores Chrome's return code, so a failed print can leave the old PDF. This is D1.
2. **"Every string in section 4 is on the page as written, verified by check 8" (report §3).** Check 8 verifies the 117 backticked strings and the stage table, not the Band A "The five parts" or "One time step" table cells. The current table copy does match the brief (I compared it), but the report's "every string" is broader than the check: a temp copy with "Your hardware…" changed to "Your device…" still passes check 8. This is D2.
3. **"the three band bottoms end within 1.5 mm of each other" (report §5).** False as rendered. The visible line-box bottoms are 276.20 mm (left), 277.04 mm (middle) and 272.20 mm (right) — a range of 4.84 mm — and the middle line is only 0.58 mm above the footer's line box. The report's 1.5 mm comes from the build's internal `p1/p2/p3` notes (275.0/276.2/274.7), not from the rendered text bottoms. This is C2.
4. **"row 2's 7.6 mm title gap" (report §5, pass 3).** The stage titles in *both* rows use `TITLE_GAP = 6.6` (`src/build_map.py:742`); `TITLE_GAP2 = 7.6` sets the row-2 first-field baseline (`src/build_map.py:672`) and is also used, wrongly, for the "After the mission" heading (`src/build_map.py:762`). That is why the After heading is 1.0 mm above the stage titles (C3); the terminus-ring clearance comes from the field top, not a 7.6 mm title gap.
5. **"three deliberate breakages … each was caught" (report §2).** Two breakage tests are shown (moved field, off-palette hex); the third item is the checker's own `TypeError`, not a third breakage. The two tests are valid; the count is wrong. The checks are also not tested against the phase/grid/copy-table cases in D2.
6. **"Every glyph centre is the topmost paint" (report §6).** Check 4 samples three glyph centres per text element (15/50/85%), not every glyph. My independent probe sampled every character's centre and found no occlusion, so the current render is clean, but the report's evidence is narrower than its wording (D2).
7. **Drawing height 38 vs 38.6 mm (report §4 vs §7).** The code gives `DRAW_H * ROBOT_S = 36.8 × 1.05 = 38.64 mm`; §4 rounds it to 38 and §7 says 38.6. Cosmetic inconsistency in the report, not in the poster.
