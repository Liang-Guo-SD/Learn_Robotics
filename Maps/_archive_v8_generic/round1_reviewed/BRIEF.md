# Design brief: Mobile Manipulator Learning Map

Owner of decisions: the lead professor. This file is the contract for both the coding agent and the review agent. Copy in section 4 is final unless a line physically cannot fit; then shorten the fewest words possible and record it.

## 1. Who and what

**Reader.** A student with no robotics background. They know basic Linux and basic Python, and nothing else: no ROS, no linear algebra beyond school, no control theory, no machine learning.

**Their goal.** Build the skills to make a two-wheeled mobile arm do two tasks: **press a button** and **pick up an object**.

**The poster answers three questions, in this order, at three distances.**
1. At 2 m: what will I build, and what is the path?
2. At 50 cm: what do I do at this stop, and how do I know I have passed?
3. At 25 cm: how do the parts fit, and why does the physics force this order?

**Scope is deliberately narrow.** Robot learning for this one robot, not all of robotics. Any item not needed for the two tasks is cut or moved to "After the mission".

**Decision on "two wheels".** The reference robot has two driven wheels plus one passive caster, so it is statically stable. True two-wheel self-balancing is a separate control problem and appears only as a branch.

## 2. Taste

Think of the page as one excellent figure from a science journal crossed with Harry Beck's Underground map and Swiss typographic posters. Edward Tufte's small multiples are the model for the physics panels. It should look calm and inevitable, as if nothing could be moved. A student should want it on the lab wall.

**Do**
- Let whitespace and alignment create structure. Use a strict column grid with every element snapped to it. Align baselines across neighbouring columns.
- Make one thing dominant: the route. The eye lands on it first.
- Use data ink. Every mark must carry meaning. Use hairline rules only where whitespace is not enough.
- Draw the science as real line diagrams with correct geometry, consistent stroke weights and labels placed by hand.
- Use the same drawing vocabulary everywhere: one arrowhead shape, one line-cap style, and at most three stroke weights (0.25, 0.5, 1.6 mm; the robot may use 0.5 and 0.8).

**Never**
- Drop shadows, gradients, grain, textures, fake paper, rounded card boxes around everything, icons, emoji, decorative illustrations or badges.
- Dashed navigation lines. Lines over a grid. Any line crossing text.
- Star, diamond or similar Unicode glyph ratings. If a symbol is needed, draw it as an SVG shape.
- Centered body text. Rotated text. All-caps body text.
- Filling space because it is empty. Empty space is correct.

**Type**
- A local font stack only, with no network fonts: `"Avenir Next", "Helvetica Neue", Helvetica, Arial, sans-serif`. For mathematics, use `"STIX Two Text", "Times New Roman", serif` in italics for variables, with proper subscripts or superscripts made using positioned `tspan`.
- At most five sizes, in mm: title 13, section heading 4.4, stop title 3.6, body 2.75, small 2.45. Nothing smaller than 2.45 mm (about 7 pt).
- Two weights only: regular and one bold or demi. Hierarchy comes from size, weight and position, not from color.
- Sentence case. Use real typographic characters: `→`, `×`, `≥`, `−`, and subscripts where the font supports them. Verify none falls back to a visibly different font.

**Color.** The paper is pure white with no background fill. Each color has exactly one meaning:

| Token | Hex | Sole meaning |
|---|---|---|
| ink | `#1B2430` | primary text and robot drawing |
| muted | `#566070` | secondary text |
| hair | `#C7CDD6` | hairline rules only; never text |
| prepare | `#0B5F9E` | route phase: Prepare (stops 0–1) |
| classical | `#00695C` | route phase: Build the classical robot (stops 2–6) |
| learned | `#8A2F6B` | route phase: Add learning (stop 7) |
| mission | `#1B2430` | route phase: Mission (stop 8), same as ink |
| safety | `#B5420A` | safety and physical limits, and nothing else |

## 3. Page layout

A3 landscape, 420 × 297 mm, 12 mm margins (content x 12–408, y 12–285). Four horizontal bands. Treat these as starting positions and adjust only for optical balance:

| Band | y (mm) | Content |
|---|---|---|
| Header | 12–36 | Title left. Reader and goal line below it. Phase key and "how to use" right. |
| A. The robot and its physics | 40–110 | Left: robot diagram and central equations. Right: four physics small multiples in one row or a 2 × 2 block. |
| B. The route (dominant) | 113–207 | One thick horizontal metro line across the full width with nine stations, numbers legible inside them, colored by phase. Under each station, one column with stop title, time, learn, build and pass. |
| C. How it fits | 211–278 | Four panels: runtime loop; development loop; five ways to decide (table); after the mission. |
| Footer | 280–285 | Small line: estimates, reference kit date, how to read sources. |

### Robot diagram (section A), required geometry
A side view on a floor line, facing right:
- A low rectangular chassis. A large drive wheel beneath it with its axle marked. A small caster at the front (right), under the reach side.
- A low battery block inside the chassis, placed behind the axle.
- A camera on a short rigid mast rising from the rear of the chassis, angled toward the workspace.
- A 5-joint arm mounted on the chassis top, drawn as links with joint circles, reaching forward toward a wall button at the right. A gripper at the tip. Keep proportions plausible: chassis about as wide as the arm's upper link is long.
- A small object on a low table or the floor within reach, not touching the arm.
- Frames as small two-axis triads with labels: W on the floor, B at the base, C at the camera, H at the hand, O at the object or button. Axis arrows must not collide with labels or links.
- A filled safety-colored dot marked "COM" above the chassis, with a thin vertical drop line to the floor. A floor bracket from axle to caster marked "support". The dot's drop line must land inside the bracket.

### Physics small multiples (section A)
Four panels, the same size and drawn in the same style. Each has a title, a tiny exact diagram, one formula and one sentence. Copy is in section 4.

### Route (section B)
Nine equal columns with shared baselines: time, learn, build and pass rows align across all columns. The thick line runs above them, with one continuous segment per phase, meeting cleanly. Stations are circles with a white number on the phase color; the number must be the top-most paint and at least as large as body text. A thin vertical tick connects each station to its column. "Pass" is the visual gate: label and text are bold enough to find instantly. There is no extra box per column. Stop 8 ends in a clear terminus marker.

Show the safety gate as a slim safety-colored bracket on the route spanning stops 2–8, with its short label placed so that it crosses nothing.

## 4. Final copy

Use exactly this copy. Do not invent facts, numbers, tools or dates.

### Header
- Title: `Mobile Manipulator Learning Map`
- Line: `From basic Linux and Python to a two-wheeled robot arm that presses a button and picks up an object.`
- How to use: `Follow the numbers. Do not move on until you meet Pass. Build in simulation first, then on the real robot.`
- Phase key: `Prepare` · `Build the classical robot` · `Add learning` · `Mission`, and one safety swatch: `Safety and limits`

### Section A: The robot and its physics
Section heading: `One robot, one idea`

Central equations, typeset beside the robot:
- `ᵂT_H = ᵂT_B(x, y, θ) · ᴮT_H(q)` with caption `Hand in world = base in world × hand relative to base (q = joint angles).`
- `ᴮT_O = ᴮT_C · ᶜT_O` with caption `Target from base = camera from base (calibration) × target from camera (vision).`
- Key insight beneath, in body weight: `Wheel odometry drifts. So park, look again, and act from the base frame.`
- Frame key, small: `T = pose of one frame in another. W world · B base · C camera · H hand · O target.`

Type the leading superscripts properly with positioned `tspan`, for example W as a small raised letter before T and H as a lowered subscript after it. Do not rely on Unicode superscript letters.

Reference robot note below the equations, small: `Reference robot: two driven wheels and a passive caster, so it stands still when powered off.`

Physics panels:

1. **`No sideways motion`** Diagram: top view of two wheels and an axle with a forward velocity arrow, and a sideways arrow crossed out in safety color. Formula: `v = r(ω_R + ω_L)/2     ω = r(ω_R − ω_L)/b`. Sentence: `Wheels roll, they do not slide. Moving 5 cm left takes a manoeuvre, so choose your parking pose carefully.` Add small key: `r wheel radius · b track width`.
2. **`Keep the COM inside`** Diagram: top view of the support triangle through two wheel contacts and the caster contact, with a COM dot inside and an arrow showing the dot moving toward the caster edge as the arm reaches. Formula, as text: `Stable: COM ground point inside the support polygon.` Sentence: `Reaching and braking shrink the margin. Keep batteries low and stow the arm before driving.`
3. **`Count the constraints`** Diagram: fingertip on a button with position dot and an approach axis arrow, with a curved arrow around the axis marked `free`. Formula: `press = 3 position + 2 axis = 5`. Sentence: `A 5-joint arm has no spare joint for this. Turning the base adds one. Counting is necessary, not sufficient.`
4. **`Friction holds it`** Diagram: two fingers squeezing a block, with normal forces `F_n` inward, friction arrows up and weight `mg` down. Formula: `2 μ F_n ≥ m g`. Sentence: `Squeeze force and surface friction must carry the weight. Soft, grippy fingertips help most.` Add small key: `μ friction coefficient · F_n grip force`.

### Section B: The route
Section heading: `The route`

Fields per stop are `Title`, `Time`, `Learn`, `Build`, `Pass`.

| # | Phase | Title | Time | Learn | Build | Pass |
|---|---|---|---|---|---|---|
| 0 | prepare | Toolbelt | 2 weeks | Git, Python environments, NumPy rotations and transforms, ROS 2 nodes and topics. | Two ROS 2 nodes that talk. A transform library in NumPy. | Your composed transforms match a hand calculation. |
| 1 | prepare | Describe | 2 weeks | URDF robot models, the TF frame tree, RViz, mass and centre of mass. | A simulated model of your robot with masses. | Full TF tree. COM stays inside support in every planned arm pose. |
| 2 | classical | Drive | 2 weeks | Differential drive, encoders, PID wheel control, odometry, ros2_control. | Velocity-controlled base, in simulation and then real. | Drive a 1 m square 10 times. Report the closing error. |
| 3 | classical | Reach | 3 weeks | Forward and inverse kinematics, joint limits, trajectories, MoveIt 2. | Arm that moves its tip to commanded points. | Touch 5 marked points, 10 times each. Report mean and worst error. |
| 4 | classical | See | 2 weeks | Camera model, calibration, AprilTag poses, hand–eye calibration, OpenCV. | Pipeline that gives a target pose in the base frame. | Point at a tag in 5 positions. Report the error in mm. |
| 5 | classical | Press | 2 weeks | Parking pose, slow approach, contact detection, force limits. | First task: drive to a panel and press a button. | From 1 m away: at least 16 of 20 presses, no tipping. |
| 6 | classical | Pick | 3 weeks | Grasp poses, friction, object detection, state machines, recovery on failure. | Second task: find, grasp and lift one object. | At least 14 of 20 picks, with failures logged by cause. |
| 7 | learned | Learn | 4 weeks | Teleoperation, demonstration data, ACT and Diffusion Policy, LeRobot, PyTorch. | A policy trained from your own demonstrations for the pick. | Compare with stop 6 on the same 20 trials. Either result is valid if you can explain it. |
| 8 | mission | Mission | 2 weeks | System integration, behaviour trees, rosbag2 logs, failure analysis. | Drive, press, pick and return as one program. | 10 logged missions with a failure breakdown, and a demo. |

Safety bracket label, spanning stops 2–8: `Before real motors: e-stop in reach, speed and joint limits, command watchdog, arm stowed while driving.`

Below the route columns or at the stop 7 column, small note: `GPU needed only at stop 7. LeRobot usually needs a thin bridge to ROS 2.`

Measurement note beneath the route, small: `Report k of n, not a percentage. 8 of 10 is compatible with a true rate of 49–94% (95% Wilson interval), so use 20 or more trials to compare.`

### Section C: How it fits

**Panel: `What runs on the robot`**. A closed loop drawn as a ring or rounded rectangle with arrows, in this order:
- `Sense`: `camera · wheel encoders · joint encoders · servo load`
- `Estimate`: `odometry · tag pose · TF frames`
- `Decide`: `state machine · planner · policy`
- `Act`: `wheel PID · joint control · gripper`
- `Physics`: `gravity · slip · contact`, closing the loop back to Sense.

Rates, small, on one line below: `Typical rates: control 50–100 Hz · camera 30 Hz · policy 10–30 Hz · task about 1 Hz`

A band beneath or around the loop in safety color: `Safety overrides everything.`

**Panel: `How you improve it`**. A small cycle: `Model → Simulate → Run on robot → Log → Measure → Change one thing →` back to Model.

**Panel: `Five ways to decide`**. A clean table with hairline rows only.

| Method | You supply | Breaks when | Stop |
|---|---|---|---|
| Scripted state machine | Steps and thresholds | The situation was not planned for | 5–6 |
| Model-based planning | Robot and scene geometry | The model or sensing is wrong | 3–6 |
| Imitation learning | Human demonstrations | The scene differs from the demos | 7 |
| Reinforcement learning | Simulator and reward | The reward or simulator misleads | Next |
| Foundation models (VLA) | Pretrained vision-language-action model, your data | Too slow, or failures are hard to explain | Next |

**Panel: `After the mission`**. A short list with a thin branch line from the terminus or a simple list marker:
- `Reach while moving: whole-body control`
- `Self-balance on two wheels: inverted pendulum, IMU, LQR`
- `Map the room: SLAM and Nav2`
- `Train in simulation: RL with MuJoCo Playground or Isaac Lab (GPU)`
- `Take instructions: foundation models such as SmolVLA`

### Footer
Left: `Times are planning estimates at about 8 hours per week, about 22 weeks in total, not measurements. Pass targets are starter values: tune them to your hardware and justify the change.`

Right: `Reference kit, checked Nov 2026: SO-101 arm (5 joints + gripper) · 2 geared DC motors with encoders · caster · single-board computer · camera · Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic. One option, not an endorsement. Check driver support before choosing a newer ROS 2.`

## 5. Science invariants

These must remain true in the drawing and the text. A violation is a blocker.
- Stop prerequisites only point backward. Stops 5 and 6 require 2, 3 and 4. Stop 7 uses the stop 6 baseline.
- Stop times total 22 weeks: 2+2+2+3+2+2+3+4+2.
- COM drop line lands within the support bracket. The caster is on the reach side, the battery is behind the axle.
- `v` and `ω` formulas use `ω_R`, `ω_L`, `r`, `b` as written. Do not "simplify" them.
- Transform order is as written. Frame labels on the drawing match the equations: B at the base, C at the camera, H at the hand, O at the target, W on the floor.
- The camera is on the base's mast, not the hand, so ᴮT_C is a fixed calibration.
- The friction diagram has two contact surfaces, matching the factor of 2. Friction arrows on the object point up, opposing `mg`.
- The constraint diagram's free rotation is around the approach axis.
- Each color is used only for its one meaning.

## 6. Deliverables and engineering

All paths are relative to `/Users/liang/Learn_Robotics/Maps`. Use `/Users/liang/.venvs/base/bin/python` with the standard library only. Chrome is at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, runnable with `--headless=new`.

- `src/content.py`: all copy and stop data, separate from layout.
- `src/build_map.py`: generates the outputs below. Reproducible; no hand-edited output.
- `src/check_map.py`: the automated checks below. Exits non-zero on any failure.
- `mobile-manipulator-map.svg`: standalone, `width="420mm" height="297mm" viewBox="0 0 420 297"`, styles inline or in its own `<style>`, with `<title>` and `<desc>`.
- `mobile-manipulator-map.html`: minimal wrapper containing the SVG inline, `@page { size: A3 landscape; margin: 0 }`, white background.
- `mobile-manipulator-map.pdf`: exactly one A3 landscape page with selectable text, printed by headless Chrome. This is the canonical print file.
- `mobile-manipulator-map.png`: preview at 3× scale.
- `CODER_REPORT.md`: what you ran, the check output, and any copy you changed and why.

Do not touch `_archive_v7/` and do not read it. Do not initialize git. Use no network resources.

### `check_map.py` must test the live browser render, by loading the HTML in headless Chrome and reading measurements back
1. All SVG text has effective computed font size ≥ 2.45 mm.
2. No two text elements' bounding boxes overlap.
3. All text boxes lie within x 12–408 and y 12–285.
4. Occlusion: sample at least the center of every text element and of every station number with `document.elementFromPoint`, and confirm that the topmost element is that text. This catches text painted under a shape.
5. No stroked line or path crosses a text box, sampled along its length. Station ticks and number backgrounds may touch only their own intended element.
6. Computed text fill equals the color declared for it. All text fills come from ink, muted, prepare, classical, learned or safety, with contrast ≥ 4.5:1 on white.
7. Only palette tokens appear anywhere in the SVG. No `filter`, gradient, pattern, `<image>` or external URL.
8. All copy in section 4 is present exactly, except changes listed in `CODER_REPORT.md`.
9. Nine stops; times total 22 weeks; all nine stations are visible with numbers.
10. The PDF has one page at A3 size and contains selectable text.

### Required working method
Do not stop at passing checks. Passing checks does not mean it is beautiful.
1. Write `content.py`, then a first full layout.
2. Render the PNG, then view it with your read tool, as a whole and in zoomed crops. If you cannot view images, say so plainly in `CODER_REPORT.md`.
3. Criticize as a demanding art director and as a physicist. Is the route dominant? Are alignments exact? Does the robot look like a plausible machine? Is there any label that needs a second look?
4. Fix and repeat at least twice more.
5. Finish only when `check_map.py` passes on the final files.
