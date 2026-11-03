# Independent review — Mobile Manipulator Learning Map

Reviewer had image access: every visual claim below was made from the PDF rasterised with
`pdftoppm` at 300–2400 dpi and from a fresh headless-Chrome render of the HTML, plus my own
measurement script (`.tmp/review/`, standard library only, `document.getBoundingClientRect`,
`getPointAtLength`, paint-order analysis) and a PDF content-stream / font-table read.
Nothing in the deliverables was modified. `_archive_v7/` was not read.

## 1. Verdict

**Ship after the listed fixes.** One Blocker — the camera is drawn looking ~30° *above* the
workspace, so the one sensor the whole eye-to-hand story depends on is aimed at the ceiling —
and ten Majors: four of nine stops have no pass threshold, safety has neither time nor a check,
the stop 6→7 jump is unbudgeted, the COM panel's diagram has lost the three contacts that define
its triangle, the runtime loop does not visibly close, the safety sentence reads as the next
panel's heading, band C is split 140/171/68 mm, two checks are unsound while the default
build does not refresh the PDF. The science that *is* on the page is correct (differential drive,
the 5-DOF count, transform order, Wilson interval, 22-week total), the copy is faithful to the
brief, and the file set reproduces byte-for-byte.

## 2. Findings

Ordered by severity. "Verified" = I measured, derived or falsified it myself; "Judgment" = a
design or teaching call.

---

### B1 — Blocker — A — the camera points away from the workspace

**Location:** robot diagram, SVG lines 35–36 (camera body, lens) and 66–69 (C triad);
page x 48.6–55.2 mm, y 65.5–71.5 mm.

**Evidence (Verified).** The camera body is the quad
(48.662,69.211)→(53.338,66.511)→(54.538,68.589)→(49.862,71.289): its long axis rises 30° to the
right. The lens stub is at the midpoint of the *upper-right* face, (53.938,67.55)→(55.151,66.85),
along (1.213,−0.7) — i.e. the optical axis is 30° **above** horizontal, and the C frame's +x axis
is drawn the same way. From the lens, the button centre (140.7, 76) is 5.6° *below* horizontal and
the object's top corner (122, 94.5) is 21.6° below. Both therefore sit 36° and 52° **below** the optical axis;
a typical robot camera (±30–35° half-FOV) frames neither. This contradicts brief §3 ("angled
toward the workspace") and the stop-4 claim that `ᴮT_C` is a fixed calibration that sees O.

**Fix.** Rotate the camera body and its C triad so the axis lands on the target: about −40° from
the drawn pose (long axis ~20° below horizontal, lens on the lower-right face). Keep the mast and
the C label.

---

### M1 — Major — B (and a brief error) — four of nine "Pass" cells are not pass criteria

**Location:** route band, Pass row, stops 2, 3, 4, 8 (y ≈ 180–192 mm); `content.py` stop data.

**Evidence (Verified).** Stop 2: "Drive a 1 m square 10 times. Report the closing error." — no
threshold. Stop 3: "…Report mean and worst error." — none. Stop 4: "…Report the error in mm." —
none. Stop 8: "10 logged missions with a failure breakdown, and a demo." — a deliverable, not a
pass. Stop 7 deliberately has no threshold ("Either result is valid if you can explain it") and
that is fine. So the poster's own question 2 ("how do I know I have passed?") is unanswered at
4 of 9 stops, while stops 5 and 6 do carry numbers (16/20, 14/20). The rest of the table sets the
expectation that every Pass cell is a test, which makes the four open cells read as unfinished
rather than as deliberate.

**Fix (needs the professor, since §4 copy is final).** Put a number in each: e.g. stop 2
"closing error ≤ 100 mm", stop 3 "mean ≤ 5 mm", stop 4 "error ≤ 10 mm", stop 8 "≥ 8 of 10
missions, failures classified". Any number is better than none as long as it is marked a starter
value (the footer already says so).

---

### M2 — Major — B (and a brief error) — safety has no time and no check

**Location:** safety bracket label (y 120.6–123.8, x 132.8–250.6); "Safety overrides
everything.", section C (y 252.8–256.5); the 22-week budget.

**Evidence (Verified + Judgment).** The only safety content is the bracket text ("e-stop in
reach, speed and joint limits, command watchdog, arm stowed while driving") and one sentence in
section C. No stop's Pass mentions it, no week is allocated to it, and the e-stop is a
*precondition* to stop 2 with no owner. The 22 weeks are exactly 9 stop times; safety is outside
the arithmetic. A student can therefore satisfy every written gate without ever demonstrating the
e-stop or the watchdog.

**Fix.** Either make the bracket a real gate at stop 2 ("before any real motor command: e-stop in
reach, limits set, watchdog verified — 5/5") and add the week, or state in the footer that every
real-robot pass is assessed with the safety setup in place.

---

### M3 — Major — B (and a brief error) — the hours per stop are not credible at 8 h/week, and 6→7 is the unbridged jump

**Location:** route Time row; footer left (y 278–284.6).

**Evidence (Verified for the arithmetic, Judgment for plausibility).** 8 h/week × 2 weeks = 16 h
for stop 0, which is asked to deliver Git, Python environments, NumPy rotations/transforms, ROS 2
nodes + topics *and* a transform library. Stop 7 is 32 h for teleoperation, demo collection, ACT
and Diffusion Policy, LeRobot and PyTorch from zero. Stops 0–3 are 9 weeks (72 h) before the first
real motion. The jump from a scripted grasp (stop 6) to training a policy (stop 7) is the largest
in the map and the only one with no bridge (nothing before stop 7 teaches data collection,
supervised training or PyTorch basics); 32 h is the least plausible number on the page.

**Fix.** Rebalance (stop 0 → 3 weeks, stop 7 → 6 weeks, or drop "NumPy rotations" to stop 1) and
add one explicit prerequisite line: "stop 7 assumes you can read a PyTorch training loop."

---

### M4 — Major — A/B — "Keep the COM inside" lost the three contacts and the motion is a 1.5 mm stub

**Location:** physics panel 2, x 339–401, y 54.8–63.9 mm; SVG line 95 (triangle), 96–98 (dot and
arrow).

**Evidence (Verified).** The triangle (361.3,63.9)-(385.7,63.9)-(373.5,54.8) has no marks at its
vertices, so the two wheel contacts and the caster contact that *define* the polygon are absent —
the brief's required "support triangle through two wheel contacts and the caster contact" is not
drawn. `CODER_REPORT.md` §7 confirms this was deliberate ("its corner dots removed"). The only
indication of motion is a shaft of 0.55 mm plus a 1.4 mm head, (374.7,57.5)-(374.7,59.45), sitting
on the dot: at 500 mm it reads as a pin on a ball, not as "the dot moves toward the caster edge".

**Fix.** Put three small open contact marks on the vertices and label the apex "caster"; replace
the stub with a 5–6 mm arrow from the dot toward the apex (no dashes — a plain solid arrow).

---

### M5 — Major — C — the safety sentence reads as the heading of the *next* panel

**Location:** section C, left column; orange rule y = 250.9, "Safety overrides everything." box
252.75–256.46, "How you improve it" box top 257.10.

**Evidence (Verified).** Gap from the orange rule to the sentence: 1.85 mm. Gap from the sentence
to the next panel's heading: **0.64 mm**. The sentence is thus optically attached to the wrong
element and, being orange and bold, reads as an orange section heading for "How you improve it".

**Fix.** Reorder so the safety line is the last thing in the loop panel, with ≥4 mm before
"How you improve it" (e.g. move the rule *below* the sentence and give 3 mm clear space after).

---

### M6 — Major — C — the runtime loop does not close

**Location:** section C, "What runs on the robot"; SVG lines 299–302 (return path); rates text at
y = 246.02.

**Evidence (Verified).** The return path's right leg starts at (139.56, 240.6): that is 5.7 mm
below the last line of the Physics description and 3.2 mm to the right of the word "Physics"
(ends x = 136.34) — it hangs in white space, attached to nothing. Its arrowhead tip is at
(24.44, 243), which is 1.2 mm below the *bottom line of the Sense description* (box ends 241.79)
and 11.5 mm below the "Sense" label (box 227.75–231.46) — it points into the middle of a text
block. The "Typical rates" line then starts 1.8 mm below the return path, so the two nearly merge.

**Fix.** Start the return leg on the Physics group's centre (x ≈ 131.7) 1.5 mm below its last
line, route it at y ≈ 245.5, and end with the arrowhead on the "Sense" label's baseline (or on a
small node to its left). Give the rates line 3 mm of air below the loop.

---

### M7 — Major — C — band C is 140 / 171 / 68 mm and the third panel is squeezed to the page edge

**Location:** section C; panels start at x = 12, 160, 340; table rules 160→331 (SVG lines 318–322).

**Evidence (Verified).** Panel widths are 140, 171 and 68 mm for content of comparable weight.
"After the mission"'s longest line ends at **404.91 mm**, 3.1 mm from the content edge, while
panel 1's cycle stops at x = 99.8 inside a 140 mm column, leaving a ~50 × 9 mm void at its bottom
right. The bottom of the band is also uneven:
panel 1's last mark is at y = 271.6, the table's last text at 263.44, the third list at 262.19
(8–9 mm imbalance). Row pitch differs between adjacent panels (table 5.95 mm, list 6.15 mm). The
report's claim of a shared 33 mm grid is not borne out: 12 + 33k gives 144/177/243/276/342, and
the actual edges are 158/160/262/339/340 — none is on it.

**Fix.** The table has ~45 mm of internal slack (its longest "Breaks when" line ends at 290.3 mm
while that column starts at 317.5; "You supply" ends at 228.3 while the next column starts at
247). Take 10 mm out of each of those two gutters and give the 20 mm to panel 3: it becomes 88 mm
and "Take instructions…" ends near 391 mm. Or move "After the mission" under the table. Put all
three panels' body rows on one 5.95 mm pitch.

---

### M8 — Major — D — check 5 never samples a polygon's closing edge, so its "no crossings" is not a result

**Location:** `src/check_map.py:152` — `for (let k = 0; k + 3 < v.length; k += 2)`.

**Evidence (Verified).** For an *n*-vertex polygon the loop stops one segment early, so the edge
from the last vertex back to the first is never tested. Re-running the same algorithm with the
closing edge included yields 5 crossing samples: the support triangle's closing edge enters the
"COM" text box (366.82–372.80 × 59.22–62.39) at (367.48, 59.29) and four neighbours. No glyph is
struck (the entry is 0.9 mm above the cap line of the C), so the drawing is visually acceptable —
but the check reports "no stroked line or path crosses any text box" for a file in which one does,
and would equally miss a real collision on any polygon's closing edge. The same check does work
for lines: moving the support bracket onto the "support" label made it fail immediately (tested
on a temp copy).

**Fix.** Iterate `k + 3 <= v.length` with the vertex index taken modulo *n* (or explicitly append
the closing segment); re-run and decide whether to move the COM label 1 mm left.

---

### M9 — Major — D — check 8 compares the page to the author's own copy file, not to the brief

**Location:** `src/check_map.py:355` (`missing = [s for s in C.EXACT_COPY if norm(s) not in page]`),
`src/content.py:206–237`.

**Evidence (Verified).** `EXACT_COPY` is assembled in `content.py` from the same strings the page
is built from, so any copy change made in `content.py` passes check 8 by construction; and despite
the message "in order and unbroken", the test is a substring test with no ordering (a string
placed in the wrong column, or duplicated, still passes). Concrete instance: the brief's panel
copy ends "`Change one thing →`"; `content.py` stores "Change one thing" and the trailing arrow is
drawn as the return path — legitimate, but exactly the kind of change check 8 cannot see.

I ran an independent comparison of ~100 back-ticked strings and table cells from BRIEF.md §4
against the page text: all are present, and the two equations match in the plain-letter form the
report discloses. So the deliverable is faithful; the *check* is not evidence of it.

**Fix.** Generate the expected strings from BRIEF.md §4 (or check a copy of it into `src/`), and
assert document order and that each string sits in its intended `data-block`.

---

### M10 — Major — D — the default build does not regenerate the PDF or PNG

**Location:** `src/build_map.py:919` (`if "--render" in sys.argv: render_outputs()`).

**Evidence (Verified).** In a clean copy containing only `src/`, `python src/build_map.py` wrote
only the SVG and HTML and exited 0, leaving no PDF/PNG. With `--render` it wrote all four, and
the result matched the shipped files exactly (SVG, HTML and PNG byte-identical; PDF differing only
in its creation timestamp). The PDF is the canonical print file, so an edit followed by the plain
command ships a stale canonical file with no error.

**Fix.** Always render (the two Chrome calls cost ~4 s), or make `check_map.py` compare the PDF's
page size, text and a render hash against the HTML and fail on drift.

---

### m1 — Minor — C — phase colours change in the middle of a link, with no station there

**Location:** route line, SVG lines 157–158, 163–164, 165–166.

**Evidence (Verified).** Blue→teal at x = 111.667, which is exactly the midpoint of stations 1
(90.5) and 2 (132.833); teal→magenta at 323.333 (midpoint 302.167/344.5); magenta→ink at 365.667
(midpoint 344.5/386.833). The link between two stops is therefore two colours, and the boundary
carries no mark.

**Fix.** Break the line at the disc: end blue at station 1's disc edge and start teal at station
2's, so the boundary is a place.

### m2 — Minor — C — the route starts in mid-air and ends in a bar at the paper edge

**Location:** SVG lines 155 (starts x = 12, blunt) and 167–168 (runs to x = 408, then a
1.6 × 8.4 mm vertical bar at x = 408).

**Evidence (Verified).** The line begins flush with the left content edge with no marker; it runs
21.2 mm past station 8 (386.833) and terminates in a heavy black bar exactly on the right content
edge. One end is marked, the other is not.

**Fix.** Put a matching start bar at x = 12, or end the line at station 8 with a short tick, so
the map has two termini or none.

### m3 — Minor — C — three of the four row labels sit 0.27 mm below their row

**Location:** route gutter, x 17–23.

**Evidence (Verified).** Row baselines are 147.52 (Time), 152.15 (Learn), 167.75 (Build), 180.35
(Pass); label baselines are 147.52, 152.42, 168.02, 180.62. "Time" is exact, the other three are
0.27 mm low — 11 % of the 2.45 mm font size, visible on close inspection as a stagger.

**Fix.** Use the row baseline for all four labels.

### m4 — Minor — B/C — the Toolbelt cell is the one crammed cell in the route

**Location:** stop 0, Learn→Build (x 29.1, y 163.70–171.46).

**Evidence (Verified).** Its Learn block runs to a 4th line (box bottom 167.41) and Build starts
at 167.75: a **0.34 mm** gap. In the other eight columns the same gap is 4.2 mm (3-line Learn) or
8.0 mm (2-line).

**Fix.** Fit "Git, Python environments, NumPy rotations and transforms, ROS 2 nodes and topics."
into three lines (e.g. "NumPy transforms" instead of "NumPy rotations and transforms") or reduce
`L1`/`Build` to start 1 mm lower in that column only.

### m5 — Minor — A/C — the friction arrows cross the block's own outline

**Location:** physics panel 4, SVG lines 114–117; page x 369.8 / 377.2, y 86.9–92.8.

**Evidence (Verified).** Each shaft runs from y = 92.8 (inside the block, which spans 88.5–93.7)
to y = 88.3, and the head tip is at 86.9 — so both arrows cross the block's top edge and both
arrowheads sit outside the block, reading as two spikes above it.

**Fix.** Keep the arrows inside the block (y 92.9 → 89.2) or start each at its contact face
(x = 368.7 / 378.3) with the head 1 mm inside the top edge.

### m6 — Minor — C — the prohibition slash reads as a second arrowhead at page scale

**Location:** physics panel 1, SVG lines 92–94; orange mark at x 292.9–302.5, y 62.7–64.3.

**Evidence (Verified + Judgment).** At 2400 dpi it is exactly what the brief asks: one left arrow
with a 2.6 mm, 45° slash. At whole-page scale (the 2 m view) I first read it as a double-headed
arrow pointing both ways — the slash is the same 0.5 stroke weight as the shaft and only
overshoots it by 0.8 mm each side. That is the failure mode a student will hit.

**Fix.** Make the slash 3.5–4 mm long at 0.25 weight, overshooting the shaft by 1.5 mm each side,
so it cannot be mistaken for an arrowhead.

### m7 — Minor — C — small marks that do not read

**Location:** robot diagram.

**Evidence (Verified).** (a) The battery is an unlabelled 6.6 × 4.2 mm rectangle at (45.4, 83.4)
— the one mark that explains why the COM sits 10 mm ahead of the axle, invisible in meaning.
(b) The wall has a 2.6 mm horizontal return at its top, (142,60)→(139.4,60), with no counterpart
on the button panel's wall (326, 86.3–96.3) and no evident meaning. (c) The frame triads are
2–3.6 mm long against a 2.4 mm-wide camera and a 2.6 mm gripper, so the camera reads as a pair
of arrows rather than a camera.

**Fix.** Label the battery ("battery", 2.45 mm) or delete it; delete the wall return; scale the
triads to ~1.5 mm and keep the labels.

### m8 — Minor — B (and a brief error) — "Keep batteries low" does not do what the panel says

**Location:** physics panel 2 sentence, "Reaching and braking shrink the margin. Keep batteries
low and stow the arm before driving."

**Evidence (Verified).** The panel is about the *static* margin: the COM's ground point versus the
support polygon. Moving mass lower does not move its ground projection, so it does nothing for
that margin; it only changes the tipping dynamics. "Stow the arm" is the remedy that actually
moves the ground point. As written, a student learns that battery height protects static
stability.

**Fix (brief copy, professor's call):** "Stow the arm before driving; keep heavy parts low and
central so a braking or reaching load cannot walk the ground point past the caster."

### m9 — Minor — B (and a brief error) — the poster explains four concepts and names the other twenty

**Location:** all Learn cells.

**Evidence (Judgment).** The reader "knows Linux and Python and nothing else". The Learn column
offers URDF, TF, RViz, ros2_control, AprilTag, MoveIt 2, ACT, Diffusion Policy, LeRobot, VLA,
LQR, SLAM, Nav2, MuJoCo Playground, Isaac Lab, rosbag2, behaviour trees — none expanded or
explained. For a *map* that is defensible (a map names places), but the reader cannot even spell
some of these to search for them, and the brief promises "what do I do at this stop".

**Fix.** At the three most load-bearing first uses, add the plain word in the cell: "URDF (the
robot's shape file)", "TF (the frame tree)", "PID (wheel speed control)". Or add one footer
sentence: "Names in Learn are the words to search for; each stop's Pass tells you when you have
them."

### m10 — Minor — B/C (and a brief error) — one prose sentence is set in the maths face

**Location:** physics panel 2, "Stable: COM ground point inside the support polygon." — class
`txt mth`; also the two key lines ("r wheel radius · b track width", "μ friction coefficient ·
F_n grip force").

**Evidence (Verified).** Computed font family for that sentence is STIX Two Text; the two
sentences directly beneath it are Avenir Next. The brief calls that line a "Formula, as text",
which invites the maths face, but the result is two typefaces in adjacent sentences in one panel,
and serif *words* in both key lines. At 50 cm it looks like a formatting slip.

**Fix.** Reserve STIX for symbols and digits; set that sentence and the key words in Avenir 2.75.

### m11 — Minor — C (and a brief conflict) — at 2 m the title, not the route, is the first fixation

**Location:** header vs route band.

**Evidence (Verified + Judgment).** Title: 13 mm type, 205.7 mm wide, cap block 9.4 mm tall, weight
600. Route: a 1.6 mm line with 8.5 mm discs and 3.6 mm numbers. On the full-page view the eye goes
title → robot → route; the route is the only colour field, which is what rescues it. Brief §2 asks
for the route to be dominant and §3 fixes the title at 13 mm — the two cannot both hold at this
size.

**Fix.** Choose: drop the title to 11 mm (still the largest type by 2.5×) or accept that the title
leads. Do not add a rule or fill to the route to compensate.

### m12 — Minor — D — one glyph falls back to a visibly different typeface

**Location:** physics panel 4 formula, `2 μ F_n ≥ m g` (x 339, y 99.6).

**Evidence (Verified in the PDF).** `pdffonts` lists `OAAAAA+TimesNewRomanPSMT`; the content
stream uses exactly one glyph from it — `<0095>` in font F33, at the position of the "≥" — while
every other glyph in that formula comes from STIX Two Text. So STIX (as installed) does not
supply `≥` and Chrome silently substituted. The report claims both fonts were verified present;
presence is true, coverage is not. Visible only on inspection, hence Minor, but the brief
explicitly requires "verify none falls back".

**Fix.** Set that one `tspan` in Avenir Next (which has `≥`), or test each glyph with
`document.fonts.check`/platform-font inspection in the checker.

### m13 — Minor — D — equations do not survive copy/paste from the PDF

**Location:** both equations, page x 158–250, y 49–68.

**Evidence (Verified).** `pdftotext` returns the first equation as `WT / H= / WT (x, y, θ) · BT (q)
/ B / H` — the superscripts and subscripts are separate positioned runs, so a student who copies
the formula out of the canonical PDF gets a scrambled string. All other 213 text elements extract
correctly.

**Fix.** Add the plain form (`WTH = WTB(x, y, θ) · BTH(q)`) as PDF `ActualText`/`aria-label`, or
an HTML `<title>` on the text element, so extract/copy yields one string.

### m14 — Minor — D — the checker's contrast test targets the wrong disc; its coverage list is short

**Location:** `src/check_map.py:326` (`contrast(t["fill"], INK)`).

**Evidence (Verified).** White station numbers are tested against ink `#1B2430` — the darkest disc
in the palette, i.e. the easiest case — not against the disc each number actually sits on. It
would pass a white number on a pale disc. Independently computed, the real worst case is classical
`#00695C` at 6.6:1, so the *design* passes (prepare 6.7, learned 7.8); only the test is wrong.
Separately, nothing checks the SVG's `width/height/viewBox`, `<title>`/`<desc>`, the HTML `@page`
rule, the PNG's 3× scale, that station numbers are ≥ body size, or that only three stroke weights
are used. I checked all of these by hand and they are correct; the checks are simply absent.

**Fix.** Compare each white number with its own disc fill; add the attribute checks above (no
browser needed).

---

## 3. What I tried to break and could not

* **The physics.** Re-derived `v = r(ω_R+ω_L)/2` and `ω = r(ω_R−ω_L)/b` (correct, including the
  use of b as track width); the 3+2=5 constraint count for a fingertip press and "a 5-joint arm has
  no spare joint" (correct; base yaw gives the one redundant DOF); `2μF_n ≥ mg` for two contacts
  (correct, and the diagram does have two contacts); the transform order in both equations
  (correct) and the C-on-the-base-mast claim (correct, so `ᴮT_C` is a constant).
* **The Wilson interval.** 8/10 at 95 %: 0.490–0.943 → "49–94 %" is right.
* **The arithmetic.** 2+2+2+3+2+2+3+4+2 = 22 weeks; 16/20 and 14/20 are consistent with the
  "20 or more trials" advice.
* **Text collisions.** Independently: 0 overlapping text boxes out of 23 005 pairs; no text
  element has a later, opaque shape painted over it (paint-order test); minimum computed font size
  2.45 mm on all 215 elements; all text fills from the palette at ≥5.6:1 on white.
* **Font substitution.** Forcing Arial, then Helvetica Neue, in place of Avenir Next: 0 lines over
  the margins, 0 overlaps. The lines are hard-wrapped (one `<text>` per line), so the layout cannot
  reflow. It is robust, not fragile.
* **Reproducibility.** A clean copy of `src/` alone (delete the measurement cache) rebuilt SVG,
  HTML and PNG byte-identically, and the PDF equivalent (hash differs only by timestamp).
* **SVG/HTML/PDF agreement.** Whole-page raster comparison of the PDF with a 3.125× HTML
  screenshot: mean |Δ| = 2.35/255, worst 64 px block 10.3/255, all in text antialiasing. Page
  1191.12 × 841.92 pt = A3 landscape, one page, fonts embedded, 4496 text ops.
* **The geometric invariants.** COM x = 64 inside the bracket 54–82; bracket runs axle→caster;
  battery ends at 52, behind the axle at 54; caster at 82 on the reach side; COM drop reaches the
  floor at y = 101; the route line stops at every disc edge so no line passes under a station
  number; the r=6 wheel emerges through the 7.7 mm chassis cut-out it needs.
* **Check integrity.** Checks 1 and 11 do have teeth: a 2.0 mm font size and a COM moved to x=40
  were both caught and exited 1 (tested on a temp copy). The station-number contrast, palette,
  occlusion and text-overlap checks all reproduce when run independently.

## 4. Discrepancies between CODER_REPORT.md and reality

Written last, after my findings. Verified against the files.

1. **§1/§2 "deterministic … byte-identical SVG"** — true, and stronger than claimed: a build from
   `src/` alone with no measurement cache also reproduces SVG, HTML and PNG byte-identically.
2. **§5 "Section A and C align to a 33 mm column (12 columns)"** — false. The measured column
   edges are 12/158/262/339 mm in A and 12/160/340 mm in C; none of 158, 160, 262, 339, 340 lies
   on 12 + 33k. Band C's three panels are 140/171/68 mm wide.
3. **§5 "Bands as in the brief: … A 40–112, B 116–208"** — the brief says A 40–110, B 113–207.
   The report restates its own adjusted bands as the brief's. (Section A's content actually ends at
   y = 112.16, so even the adjusted band is exceeded by 0.16 mm.)
4. **§5 "the metro line is broken into 12 server-drawn segments"** — there are 13 (SVG lines
   155–167): four phase runs plus nine disc gaps.
5. **§5 "both fonts verified present (`document.fonts.check`)"** — presence is true; glyph coverage
   is not. One glyph, the `≥` in `2 μ F_n ≥ m g`, is the only glyph in the document set in
   TimesNewRomanPSMT (PDF font object 33 / resource F33).
6. **§6 "check 6 … *then* verifies white-on-phase contrast"** — it verifies white against `INK`
   only (`check_map.py:326`), i.e. the highest-contrast disc, not the disc under each number.
7. **§6 "Check 5 uses no exemption at all"** — true, but it also never samples a polygon's closing
   edge (`check_map.py:152`), so it reported "no crossings" while the support triangle enters the
   COM label box.
8. **§3/§6 check 10's message "fonts embedded"** — nothing in check 10 tests embedding (no
   `/FontFile` or `pdffonts`); the statement happens to be true.
9. **§6 "Check 11 … I confirmed it has teeth by moving COM to x = 40"** — confirmed: it fails with
   two messages.
10. **§8 "Panel 1's key line sits 2.1 mm above panel 2's title"** — the panel below panel 1 is
    panel 3 ("Count the constraints"); measured box gap 1.87 mm.
11. **§8 "If Avenir Next is missing, Helvetica Neue takes over, the wrap changes and the checker
    will find the collisions it causes"** — false. Every line is a separate `<text>` with a fixed
    y, so nothing re-wraps. Substituting Helvetica Neue or Arial gave 0 overflows and 0 overlaps;
    the widest non-right-aligned line still ends at 404.5 mm.
12. **§4 "No sentence of section 4 was changed"** — true as far as I can verify independently (~100
    brief strings all present), but check 8 compares the page with `content.py`'s own
    `EXACT_COPY`, so it cannot prove this, and it does not test order despite the message. The
    brief's "`Change one thing →`" is stored without the arrow (drawn instead).
13. **§7 Pass 2 "the 'forbidden sideways' mark read as a double-headed arrow … fixed"** — the file
    now has one left arrow with a slash, so the fix is present; at whole-page scale the slash still
    reads as a second arrowhead (I made that error before zooming to 2400 dpi).
14. **§7 Pass 2 "its corner dots removed (fewer marks, less false scale)"** — recorded as an
    improvement, but brief §4 requires the support triangle to pass "through two wheel contacts
    and the caster contact"; removing the contacts removes the diagram's only link to the robot's
    three points of support.
