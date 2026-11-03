# Coder report — Mobile Manipulator Learning Map

## 1. What is here

| File | What it is |
|---|---|
| `src/content.py` | All copy and stop data, separate from layout. Section 4 of the brief is transcribed here once; `EXACT_COPY` is the list the checker verifies. The two transform equations are stored as runs `(kind, text)` so they can be set with real raised/lowered letters. |
| `src/build_map.py` | Generates `mobile-manipulator-map.svg` and `.html`, then (with `--render`) the PDF and PNG through headless Chrome. Every coordinate is a named constant at the top or is computed from one; the robot's joints are solved with a two-link IK from `SHOULDER`, `L1`, `L2` and the wrist target, and the wheel, caster, COM, battery and frames are all derived from `WHEEL_X`, `CASTER_X`, `COM`, `BATTERY`. |
| `src/check_map.py` | The automated checks. Loads the real HTML in headless Chrome, reads geometry back from the live render with `getBoundingClientRect`, `getExtentOfChar`, `getPointAtLength` and `document.elementFromPoint`, and exits non-zero on any failure. |
| `mobile-manipulator-map.svg` | Standalone, `width="420mm" height="297mm" viewBox="0 0 420 297"`, `<title>`, `<desc>`, inline `<style>`. |
| `mobile-manipulator-map.html` | Minimal wrapper, SVG inline, `@page { size: A3 landscape; margin: 0 }`, white background. |
| `mobile-manipulator-map.pdf` | One A3 landscape page, selectable text, printed by headless Chrome. Canonical print file. |
| `mobile-manipulator-map.png` | 3× preview, 4764 × 3369 px (≈288 dpi). |

Text width is measured in the browser, never guessed: `build_map.py` collects every string it must wrap, measures them with canvas metrics in headless Chrome at ten times size (so no hinting rounding), caches the results in `.tmp/measure.json`, and rebuilds until stable. Wrapping is a dynamic program that finds the fewest lines and then the most even rag; `"·"` is glued to the word before it so no line ever starts with a separator.

## 2. How to reproduce

```
/Users/liang/.venvs/base/bin/python src/build_map.py --render
/Users/liang/.venvs/base/bin/python src/check_map.py
```

`build_map.py` is deterministic: a second run produced a byte-identical SVG (`diff` clean). Delete `.tmp/measure.json` and it re-measures from scratch.

## 3. Final check output

```
page text elements: 215   svg px: 1587.4 x 1122.5
  ok   1  smallest text 2.45 mm, all 215 text elements >= 2.45 mm
  ok   2  no two text boxes overlap (23005 pairs checked)
  ok   3  all text inside x 12-408, y 12-285
  ok   4  every sampled glyph centre is the topmost element
  ok   5  no stroked line or path crosses any text box
  ok   6  all text fills are ink, muted or a phase colour (white only on station numbers)
  ok   6  every text colour clears 4.5:1 on white (min 5.6:1)
  ok   6  white station numbers clear 4.5:1 on the darkest phase colour
  ok   7  SVG uses only the seven palette tokens (8 found)
  ok   7  white is used only for station numbers
  ok   7  no filter, gradient, pattern, image or external URL
  ok   8  all 134 required strings are present, in order and unbroken
  ok   9  nine stations, numbers 0-8 present
  ok   9  stop times total 22 weeks: 2+2+2+3+2+2+3+4+2
  ok  11  COM drop line lands inside the support bracket (x 64.00 in 54.00-82.00); battery
          behind the axle; caster on the reach side; frames placed
  ok  10  PDF is one page, 1190.6 x 841.9 pt (A3 landscape)
  ok  10  PDF text is selectable (4496 text operations, fonts embedded)

all checks passed   (exit 0)
```

## 4. Copy

**No sentence of section 4 was changed, shortened or added to.** Three things about how the copy is set should be on record:

1. **Equations.** `ᵂT_H = ᵂT_B(x, y, θ) · ᴮT_H(q)` and `ᴮT_O = ᴮT_C · ᶜT_O` are set exactly as the brief asks — W and B as raised letters, H, B, O, C as lowered letters, built from positioned `tspan`s with `dy` baseline shifts and no Unicode superscript letters and no spacer glyphs. Because the character stream is therefore `WTH = WTB(x, y, θ) · BTH(q)`, check 8 compares the page against that plain-letter form (the brief's ᶜ is set as capital C, to match the frame key "C camera"). Recorded here as a notation decision, not a copy change.
2. **Panel 1's two formulas** are set as two groups on one line with a 6 mm gap where the brief has five spaces. Same characters, same order; SVG collapses runs of spaces, so a measured gap is the honest equivalent.
3. **Labels that are not prose** were added because the brief asks for them or because the diagram is unreadable without them: frame letters `W B C H O` (required), `support` and `COM` (required), the diagram quantities `v`, `free`, `F_n`, `mg` (the copy names them), and the four row labels `Time Learn Build Pass` in the route's left gutter — those are the field names of the brief's own stop table. No fact, number, tool or date was invented.

## 5. Layout, and the decisions behind it

* 12 mm margins; content 12–408 × 12–285. Section A and C align to a 33 mm column (12 columns); section B uses its own nine-fold rhythm, because the route is a map, not a table. Row labels hang in a 21 mm gutter so the nine stop columns stay equal.
* Bands as in the brief: header 12–36, A 40–112, B 116–208, C 211–278, footer to 285. The route band is the widest and carries the only large colour field, so it dominates. The station discs are 8.5 mm across with 3.6 mm numerals — larger than body text, as specified.
* Type: five sizes only (13 / 4.4 / 3.6 / 2.75 / 2.45 mm), two weights (400, 600), Avenir Next for text and STIX Two Text for mathematics. Both fonts verified present (`document.fonts.check`).
* The metro line is broken into 12 server-drawn segments: one per phase, and a gap wherever a station disc sits, so no line geometry ever passes under a station number. Butt caps, one arrow vocabulary (line + filled triangle), stroke weights 0.25 / 0.5 / 0.8 (robot) / 1.6 (the route).
* White paper, no fills except the phase discs, the swatches, the COM dot, the button and the arrowheads.

## 6. About the checks

* **Check 5 uses no exemption at all.** The brief allows one for an intended contact; none was needed, because the route line stops at each disc and the station ticks begin at the disc edge.
* **Check 6 and white.** Section 3 requires "a white number on the phase color", which the six-token rule cannot express, so the checker allows `#FFFFFF` text only on elements with class `stn-num`, and *then* verifies white-on-phase contrast ≥ 4.5:1 rather than assuming it. Nothing else in the file is white.
* **Check 3** allows 0.02 mm at the margins. Right-aligned blocks end exactly on x = 408; the layout box carries a sub-pixel right side bearing, so the measured box can read 408.0009. The tolerance is four thousandths of a point and does not move any mark.
* **Check 4** samples three painted glyph centres per text line (`getExtentOfChar`), not the bbox centre, because a bbox centre can fall in a word space and hit nothing.
* **Check 11 was added** (not required by the brief) to test the section-5 invariants that are geometric: the COM drop line lies inside the support bracket and reaches the floor, the bracket runs axle to caster, the battery is behind the axle, the caster is on the reach side, and C/H/W sit where the frame key says. I confirmed it has teeth by moving `COM` to x = 40 and watching it fail, then reverting.
* Checks 5, 2 and 3 each caught real defects during the build (the route line passing under station numbers, arrows running into formulas, a title whose font box crossed the goal line), which is why they are trusted.

## 7. Design passes

I viewed the PNG whole and in 1:1 crops (`.tmp/views/`) after every rebuild — robot, hand, wheel, physics panels, route, terminus, section C, footer, header, and the PDF re-rendered to an image.

**Pass 1** (what was wrong): the table's rows overlapped because each row advanced from its first baseline, not its last; mathematics carried visible gaps from spacer glyphs after every superscript; the wheel was drawn with a wrong arc sweep and read as a scallop; the arm was two hairlines with oversized joint circles. Fixed: row cursor, `dy` bookkeeping with no spacer glyphs, wheel redrawn as a circle in a cut-out, links redrawn as tapered outlines that die into the bearing circles.

**Pass 2**: the support triangle was a 30 × 8 mm roof that contradicted the side view; the "forbidden sideways" mark read as a double-headed arrow; the friction arrows sat on the object's top edge instead of its contact faces; the loop's return path arrived on a diagonal. Fixed: triangle re-proportioned and its corner dots removed (fewer marks, less false scale), the rotation redrawn as an ellipse ending in one tangent arrowhead, friction arrows moved onto the two contact faces, return path squared off.

**Pass 3**: rows of the physics block did not share a bottom shelf; the header's phase key and instruction had the same weight; the "typewriter" wheel cap inside the chassis. Fixed: all four diagrams now end on y = 15.0 within their panel, the key went quiet (muted) and the instruction primary (ink), the wheel became a full circle behind an interrupted chassis edge.

## 8. Still unhappy

* **The physics 2 × 2 grid is tight.** Panel 1's key line sits 2.1 mm above panel 2's title. The band is 70 mm and two panels of title + diagram + formula + two-line sentence + key need 30 mm each. I chose alignment (all four formulas on one baseline) over air.
* **The two top-view diagrams are not to the same scale as the side view.** The side view's support base is 28 mm axle-to-caster; the top view's triangle is 24 mm wide and 9 mm deep. They are small multiples, drawn for legibility inside 69 mm panels, not one orthographic projection — a physicist could fairly ask for them scaled to match, and the honest answer is that they cannot be at this page size without shrinking the diagrams to nothing.
* **The arm's elbow-up pose is tall.** It is the true two-link solution (L1 = 38, L2 = 30, wrist 51 mm away) and a folded arm has its elbow high; but the left third of section A is a large "Λ", and the drawing's balance relies on the chassis being light and the links heavy.
* **Fonts are local only.** If `Avenir Next` is missing, `Helvetica Neue` takes over, the wrap changes and the checker will find the collisions it causes — the layout is measured, not fixed.
* **The station numbers are white**, technically one colour outside the six-token list. Section 3 asks for it and check 6 documents and verifies the contrast; I would rather the brief had listed white as a token.

## 9. One disclosure

While orienting myself in an empty working directory I ran `ls _archive_v7 | head -3`, which printed two file names. No file in `_archive_v7/` was opened or read, and nothing from it influenced the design or the copy.
