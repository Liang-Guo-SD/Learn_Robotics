# Design brief: The LeRobot Learning Roadmap

Owner of decisions: the lead professor. This file is the contract for the coding agent and the review agent. Copy in section 4 is final unless a line physically cannot fit; then shorten the fewest words possible and record it.

## 1. Who and what

**Reader.** A student who has mastered ROS 2 and OpenCV, and has never used LeRobot. Assume no PyTorch or imitation-learning experience.

**Goal.** Make a two-wheeled, 6+1 DoF mobile arm press a button and pick up a cup, working inside the LeRobot ecosystem.

**This poster is a learning roadmap.** It answers, in this order:
1. At 2 m: what is the path from start to finish?
2. At 50 cm: what do I learn and do at this stage, on which computer, and how do I prove I have passed?
3. At 25 cm: how does LeRobot work, what does each computer do, what does the lidar see, and how do I truly master this?

**Hardware.** One NVIDIA DGX Spark, two Jetson AGX Orin 64GB, two driven wheels plus a passive caster, a 6+1 DoF arm (6 arm joints + gripper), a matching powered leader arm, a gamepad, wrist and head cameras, and one single-line 2D scanning lidar on the chassis. No Jetson Thor.

**Decisions already made.**
- ROS 2 is not in the control loop. Room navigation is an extension.
- The robot performs a short approach of about 1 m. There is no mapping in the core route.
- "Single-beam lidar" means a single-line scanner sweeping one horizontal plane.

## 2. Taste

Think of one excellent figure from a science journal, crossed with Harry Beck's Underground map and Swiss typographic posters. It should look calm, exact and inevitable, as if nothing could be moved. A student should want it on the lab wall.

**Do**
- Let whitespace and alignment create structure. Use one strict column grid for all bands, with named constants, and really adhere to it. Align baselines across neighbouring columns.
- Make one thing dominant: the metro line of the roadmap. The eye lands on it first.
- Use data ink. Every mark must carry meaning. Use hairline rules only where whitespace is not enough.
- Draw diagrams with correct, computed geometry, consistent stroke weights and hand-placed labels.
- Use one drawing vocabulary everywhere: one arrowhead shape, one line-cap style, at most three stroke weights (0.25, 0.5, 1.6 mm; drawings may also use 0.8).

**Never**
- Drop shadows, gradients, grain, textures, fake paper, rounded card boxes around everything, icons, emoji, decorative illustrations or badges.
- Dashed navigation lines. Lines over a grid. Any line crossing text.
- Star, diamond or similar Unicode glyph ratings. If a symbol is needed, draw it as an SVG shape.
- Centered body text. Rotated text. All-caps body text.
- Filling space because it is empty.

**Type**
- Local fonts only, no network fonts. Text: `"Avenir Next", "Helvetica Neue", Helvetica, Arial, sans-serif`. Code, commands, class and file names: `Menlo, Consolas, monospace`.
- At most five sizes, in mm: title 11, section heading 4.4, stage title 3.6, body 2.75, small 2.45. Nothing smaller than 2.45 mm (about 7 pt). Monospace may be set one size step smaller to match the sans's visual size, but never below 2.45.
- Two weights only: regular and demi. Hierarchy comes from size, weight and position, not color.
- Sentence case. Verify each non-ASCII glyph (`→`, `·`, `π`, `–`) renders from an intended font, with no fallback.

**Color.** The paper is pure white with no background fill. Each color has exactly one meaning:

| Token | Hex | Sole meaning |
|---|---|---|
| ink | `#1B2430` | primary text and drawings |
| muted | `#566070` | secondary text |
| hair | `#C7CDD6` | hairline rules only; never text |
| prepare | `#0B5F9E` | phase: Prepare (stages 0–1) |
| build | `#00695C` | phase: Build the robot (stages 2–5) |
| teach | `#8A2F6B` | phase: Teach (stages 6–9) |
| mission | `#1B2430` | phase: Mission (stage 10), same as ink |
| safety | `#B5420A` | safety and physical limits, and nothing else |
| white | `#FFFFFF` | station numbers only |

## 3. Page layout

A3 landscape, 420 × 297 mm, 12 mm margins (content x 12–408, y 12–285).

| Band | y (mm) | Content |
|---|---|---|
| Header | 12–30 | Title left, line below it. Phase key and how-to-use right. |
| A. How LeRobot works | 33–92 | Left: lead sentence and the four-step pipeline with an Improve loop. Middle: the five parts. Right: one time step. |
| B. The roadmap (dominant) | 95–210 | Two rows of six columns on one continuous metro line. |
| C. How to do it | 213–276 | Three panels: three computers; what the lidar sees; how to master it. |
| Footer | 278–285 | Small estimates and version note. |

Treat these as starting values and adjust for optical balance. Keep the order and the dominance of band B.

### Band A
The pipeline is four steps in a row, each with name, one sentence and its command in monospace, joined by arrows. An Improve line returns from Deploy to Record as one clean elbow, with its label placed so that it crosses nothing. It must read in three seconds as a loop.

"One time step" is drawn as a small data table: each feature on one row with a small to-scale segmented bar for `observation.state` (7 + 2 + 16 = 25 segments) and `action` (7 + 2 = 9 segments), so that the student sees the two vectors' structure. Use one segment width in both bars.

### Band B
One continuous thick (1.6 mm) line.
- Row 1 holds stages 0–5, left to right, in six equal columns, with stations **above** their fields.
- After station 5, the line continues right to a channel at the right margin, turns down with a 45° chamfer, runs right to left through a reserved gap below all of row 1's fields, then chamfers down into station 6 from the left. It crosses no text. Row 2 also has stations above their fields.
- Row 2 holds stages 6–10 in the first five columns, on the same column positions. The sixth column holds "After the mission", with no station.
- Station 10 is a terminus, drawn as a double ring.
- A station is a circle with a white number on the phase color. The number is the top-most paint and at least body size.
- The phase color changes at a station's right edge: the link leaving the last stage of a phase takes the next phase's color. No link is split elsewhere.

Under each station, in both rows, are the same fields, with shared baselines across each row of the poster: title with time; Learn; Do; On; Pass; Explain. Row labels sit once in a left gutter for each poster row, aligned to their baselines. "Pass" must be findable at a glance (demi weight, ink). "Explain" is muted. Leave at least 2.5 mm of clear space between fields in every column.

Safety: one slim safety-colored bracket above stations 2–5, with a closing-free right end that stays clear of the turn, meaning it continues. The safety label sits on its own baseline above the bracket, and crosses nothing. There is no second bracket in row 2.

### Band C
**Three computers.** A small flow diagram of three named nodes, without card boxes: `Robot Orin` ↔ `Station Orin` → `DGX Spark`, plus a return arrow from Spark to Orin for the trained policy. Arrows carry short labels as given. Below it, three lines giving each machine's role, then the setup notes.

**What the lidar sees.** A computed side-view drawing, about 110 × 45 mm, in the geometry below, followed by the copy.

**How to master it.** The four-step ladder, then five rules.

### Robot drawing: required geometry
Compute all positions from named variables, and assert the physics in code.
- A floor line. A low chassis with one large drive wheel near the rear and a small caster at the front (right).
- Lidar: a small puck on the chassis's front top edge. The arm's base is behind it, so the stowed and reaching arm stay above the plane. The lidar plane is a thin straight horizontal line at puck height, running right from the puck.
- A wall at the far right, with the button panel on it. The panel extends down across the lidar plane, but in this pose it is occluded by the table leg. The button itself sits above the plane. Label `button`.
- A table between robot and wall. Its top lies above the plane and its legs cross it. A ray stops at the first thing it hits: draw one ray from the lidar to the first table leg, with a small hit mark labelled `ray stops here`. Do not draw a line through a solid object.
- A cup standing on the tabletop, above the plane. Label `cup`.
- The robot is parked for the cup. Arm with exactly six joint marks and a gripper, reaching over the table's near edge, with the open gripper about 4 mm from the cup at the cup's height, touching nothing. The cup stands near the table's near edge, within the arm's computed maximum reach from its shoulder. Elbow angle 120–150°.
- A head camera on a short mast and a wrist camera near the gripper. The head camera sits above the cup's top, with its optical axis pointing at the cup, and the cup within ±30° of the axis. Lines of sight from head and wrist cameras to the cup must be unobstructed. The button need not be visible or reachable in this pose.
- Labels: `lidar`, `lidar plane`, `ray stops here`, `head camera`, `wrist camera`, `cup`, `button`, `table leg`, `caster`. Nothing collides. Hit marks are small and use the safety color only if they represent a limit; use ink otherwise.

## 4. Final copy

Use exactly this copy. Do not invent facts, numbers, tools or dates. Text shown in backticks inside a field and listed as code below uses the monospace face.

### Header
- Title: `The LeRobot Learning Roadmap`
- Line: `From ROS 2 and OpenCV skills to a two-wheeled 6+1 DoF arm that presses a button and picks up a cup.`
- How to use: `Follow the numbers. Move on only when you can meet Pass and answer Explain.`
- Phase key: `Prepare` · `Build the robot` · `Teach` · `Mission`, and one safety swatch: `Safety and limits`

### Band A
Section heading: `How LeRobot works`

Lead: `LeRobot learns a task by copying you. You drive the robot, it saves what the robot sensed and what you commanded, and a neural network learns to produce the same commands from the same observations.`

Pipeline:
| Step | Sentence | Command (monospace) |
|---|---|---|
| Teleoperate | You command the robot with a leader arm and gamepad. Nothing is learned yet. | lerobot-teleoperate |
| Record | Each attempt becomes an episode: video, state and action at every time step. | lerobot-record |
| Train | A policy learns to predict your actions from each recorded observation. | lerobot-train |
| Deploy | The policy drives the robot. You count real successes, not training loss. | lerobot-rollout |

Improve loop label: `Improve: take over when it fails. Your corrections become new data.` with command `--strategy.type=dagger`

Parts heading: `The five parts`
| Part (monospace) | Meaning |
|---|---|
| Robot | Your hardware as a Python class: get_observation() reads it, send_action() moves it. |
| Teleoperator | The human as a Python class: get_action() returns your command. |
| Processor | Converts and limits data between teleoperator, dataset and robot. |
| LeRobotDataset | Numbers in Parquet, video in MP4, schema and statistics in meta/. |
| Policy | A network that turns one observation into a chunk of future actions. |

Time-step heading: `One time step in your dataset`
| Feature (monospace) | Bar and note |
|---|---|
| observation.images.wrist | video |
| observation.images.head | video |
| observation.state | 25 numbers: 7 arm + 2 base + 16 lidar |
| action | 9 numbers: 7 arm + x.vel + theta.vel |

Note: `Predicting a chunk of actions at once keeps motion smooth and limits compounding errors.`

### Band B
Section heading: `The roadmap`

Field labels: `Learn`, `Do`, `On`, `Pass`, `Explain`.

Safety label: `From stage 2 to the end, before any motor moves: e-stop in reach, joint and speed limits set, watchdog armed, arm stowed while driving.`

| # | Phase | Title | Time |
|---|---|---|---|
| 0 | prepare | Set up the machines | 1 week |
| 1 | prepare | Read the framework | 1 week |
| 2 | build | Write the robot driver | 3 weeks |
| 3 | build | Add the lidar | 1 week |
| 4 | build | Connect teleoperation | 2 weeks |
| 5 | build | Record clean data | 1 week |
| 6 | teach | Press the button | 2 weeks |
| 7 | teach | Pick up the cup | 3 weeks |
| 8 | teach | Teach by correcting | 2 weeks |
| 9 | teach | One model, two tasks | 2 weeks |
| 10 | mission | Run the mission | 1 week |

Stage 0
- Learn: `Python 3.12 environments, CUDA wheels on ARM, why versions must match.`
- Do: `Install LeRobot v0.6.0 on the Spark and both Orins. Keep ROS 2 outside the environment.`
- On: `Spark · Robot Orin · Station Orin`
- Pass: `A real CUDA computation runs on all three, with the same LeRobot version.`
- Explain: `Why can a generic torch wheel fail on Orin?`

Stage 1
- Learn: `Dataset format, ACT, action chunks, normalization statistics.`
- Do: `Load a public dataset in Python, train ACT on it, and trace one frame from dataset to predicted action.`
- On: `Spark`
- Pass: `Plot predicted against recorded actions on an episode kept out of training.`
- Explain: `Why is low training loss not the same as task success?`

Stage 2
- Learn: `Robot class, motor bus, calibration, plugin packaging, two-wheel kinematics.`
- Do: `Write lerobot_robot_mobile_arm: 6+1 joints, x.vel, theta.vel, both cameras, calibration, joint limits, hardware e-stop, watchdog.`
- On: `Robot Orin`
- Pass: `Joints stay within limits. E-stop and watchdog stop it 5 of 5. Ten 1 m squares each close within 10 cm.`
- Explain: `Why is there no y.vel in your action?`

Stage 3
- Learn: `Scan timing, masking the robot's body, reducing a scan to 16 sectors.`
- Do: `Add lidar.s00 to lidar.s15 to the observation. Slow and stop x.vel inside send_action, whatever a policy asks.`
- On: `Robot Orin`
- Pass: `All 16 sectors log at scan rate with the body masked. Driven at a wall 10 times at top speed, it stops at least 15 cm away.`
- Explain: `What can a single lidar plane never see?`

Stage 4
- Learn: `Teleoperator class, processors, robot host and client over a network.`
- Do: `Combine the powered leader arm and gamepad into one 9-number action. Run the host on Robot Orin.`
- On: `Robot Orin · Station Orin`
- Pass: `You complete both tasks 9 of 10 times, watching only the camera feeds.`
- Explain: `If you cannot do it from the sensors alone, why can the policy not?`

Stage 5
- Learn: `Episodes, replay, the dataset visualizer, what makes a good demonstration.`
- Do: `Fix camera mounts and lighting. Record 10 test episodes and move them to the Spark.`
- On: `Station Orin → Spark`
- Pass: `Parked-base replay repeats the task. Feature and camera names are frozen.`
- Explain: `Why does renaming a camera break a trained policy?`

Stage 6
- Learn: `Demonstration variety, ACT training, rollout, reading failures from recorded episodes.`
- Do: `Three steps: parked base, small start offsets, approach from 1 m. Start with 50 demos; add more where it fails.`
- On: `Station Orin → Spark → Robot Orin`
- Pass: `From 1 m: at least 16 of 20 presses, with no tipping.`
- Explain: `Which failures come from data, and which from hardware?`

Stage 7
- Learn: `Grasp variety, friction, ACT against Diffusion Policy on the same trials.`
- Do: `Empty opaque cup, side grasp, same three steps. Add harder cups only after it passes.`
- On: `Station Orin → Spark → Robot Orin`
- Pass: `At least 14 of 20: lifted 5 cm, upright, held for 3 s.`
- Explain: `Why compare policies on identical trials?`

Stage 8
- Learn: `DAgger, compounding errors, merging datasets, fine-tuning.`
- Do: `Roll out with --strategy.type=dagger, take over before failure, and fine-tune on demos plus corrections.`
- On: `Robot Orin · Station Orin → Spark`
- Pass: `Beats the earlier policy on the same 20 trials, or you can explain why not.`
- Explain: `Why do corrections teach what demonstrations cannot?`

Stage 9
- Learn: `SmolVLA, language prompts, async inference, Real-Time Chunking.`
- Do: `Fine-tune smolvla_base on the Spark with one prompt per task. Serve it from Station Orin to the robot.`
- On: `Spark → Station Orin → Robot Orin`
- Pass: `On 20 trials per task, compared with your two ACT policies. Either result is fine if explained.`
- Explain: `What does RTC fix, and what does async inference fix?`

Stage 10
- Learn: `Sequencing policies, success checks with OpenCV, failure analysis.`
- Do: `Write a Python script: approach, press, confirm the light, pick up the cup. Log every run.`
- On: `Robot Orin · Station Orin`
- Pass: `At least 6 of 10 full missions, failures classified by cause, and a live demo.`
- Explain: `Where would your next 50 demonstrations go, and why?`

Column 6 of row 2. Heading: `After the mission`. List:
- `Navigate a room: ROS 2 and Nav2 with the lidar.`
- `Learn on the robot: HIL-SERL for short arm-only tasks.`
- `Try larger models: Pi0.5 fits in Spark memory, but expect long runs.`
- `Share it: publish your dataset and model card on the Hub.`

### Band C

**Panel 1.** Heading: `Three computers, three jobs`

Flow labels: Robot Orin ↔ Station Orin: `wired network`; Station Orin → DGX Spark: `datasets`; DGX Spark → both Orins: `trained policies`.

Roles:
- `Robot Orin`, `on the chassis`: `Motors, cameras, lidar and safety. Runs ACT directly. Budget its power on the battery.`
- `Station Orin`, `on the bench`: `Leader arm, gamepad, monitor. Records datasets to an added NVMe drive. Serves large policies.`
- `DGX Spark`, `in the lab`: `Trains every policy, one job at a time, and keeps the master datasets. Never in the control loop.`

Work pattern: `Most stages: record on Station Orin, train on the Spark, run on Robot Orin.`

Timing note: `Plan overnight runs: one published SmolVLA example, 20,000 steps at batch 64, took about 30 h on a Spark. Time your own first run.`

Setup, with commands in monospace:
- `Spark: uv venv --python 3.12, then install from the v0.6.0 tag.`
- `Orin: JetPack 7.2 and Python 3.12. Install the Jetson torch wheel first, then pip install lerobot==0.6.0 --no-deps and its dependencies by hand. This recipe was tested on Orin NX, so verify it on AGX.`
- `Both are ARM machines, so LeRobot decodes video with PyAV.`

**Panel 2.** Heading: `What one lidar plane sees`
- `It scans one horizontal slice at chassis height. The drawing shows the robot parked for the cup; it drives elsewhere to press the button.`
- `Sees: walls, table legs, people's legs, and the button panel when nothing blocks it.`
- `Misses: the cup, the tabletop, the arm, stairs and drop-offs.`
- `So cameras find the targets. The lidar keeps distance and stops the base.`
- `LeRobot has no lidar class. Your driver reports 16 sector distances as floats, and they join observation.state.`

**Panel 3.** Heading: `How to master it`

Ladder, four steps joined by arrows: `Run it` → `Explain it` → `Change it` → `Debug it`, with one short definition under each step:
- Run it: `The command works.`
- Explain it: `You can say what it wrote and why.`
- Change it: `You alter one part on purpose.`
- Debug it: `You fix a failure from the logs.`

Rules:
- `Trace one frame by hand before you trust a command.` then, muted: `Follow it from get_observation() to the dataset row to the policy output.`
- `Watch your dataset before you train on it.` then, muted: `A bad episode teaches bad behavior.`
- `Change one thing per experiment, and write it down.` then, muted: `Otherwise you cannot tell what helped.`
- `Count real successes as k of n.` then, muted: `8 of 10 still allows a true rate of 49–94% (95% Wilson interval).`
- `When the docs and the robot disagree, read the source.` then, muted: `LeRobot changes quickly, and the code is the final word.`

### Footer
Left: `Times are planning estimates at about 8 hours per week, about 19 weeks in total. Pass targets are starter values: tune them to your hardware and justify the change.`

Right: `Checked Nov 2026 against LeRobot v0.6 docs. Commands and flags change between releases, so pin one version and use --help.`

## 5. Science and fact invariants

A violation is a blocker.
- Stage times total 19 weeks: 1+1+3+1+2+1+2+3+2+2+1.
- `observation.state` = 7 arm + 2 base + 16 lidar = 25. `action` = 7 arm + 2 base = 9. Bars have exactly those segments.
- Stage 10's 6 of 10 is consistent with stages 6 and 7: 16/20 × 14/20 = 56% before retries.
- Prerequisites only point backward: stage 6 needs 2–5; stage 8 needs a trained policy and a powered leader; stage 10 needs 6 and 7.
- The On field matches the role of each computer. DGX Spark is never drawn in the real-time loop.
- A lidar ray does not pass through a solid object in the drawing.
- Cup, tabletop and button lie above the lidar plane. Table leg and panel cross it.
- Wilson 95% interval for 8 of 10 is 49–94%.

## 6. Deliverables and engineering

All paths are relative to `/Users/liang/Learn_Robotics/Maps`. Use `/Users/liang/.venvs/base/bin/python` with the standard library only. Chrome is at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`, runnable with `--headless=new`.

- `src/content.py`: all copy and stage data, separate from layout.
- `src/build_map.py`: always generates all four outputs in one run. It deletes old outputs first, checks Chrome's return code, and depends on no hidden cache: a clean copy of `src/` and `BRIEF.md` must reproduce byte-identical SVG, HTML and PNG. No flag can leave a stale PDF.
- `src/check_map.py`: the automated checks below; exits non-zero on any failure.
- `lerobot-roadmap.svg`: standalone, `width="420mm" height="297mm" viewBox="0 0 420 297"`, own `<style>`, with `<title>` and `<desc>`.
- `lerobot-roadmap.html`: minimal wrapper containing the SVG inline, `@page { size: A3 landscape; margin: 0 }`, white background.
- `lerobot-roadmap.pdf`: exactly one A3 landscape page, selectable text, printed by headless Chrome. The canonical print file.
- `lerobot-roadmap.png`: preview at 3× scale.
- `CODER_REPORT.md`: what you ran, final check output, any copy you changed and why. Only claims you verified.

Do not read or modify `_archive_v7/`. You may read `_archive_v8_generic/src/` for reusable engineering only: browser text measurement, wrapping and check methods. Do not reuse its layout, content or copy, and do not modify that folder. Do not initialize git. Use no network resources.

### `check_map.py` must test the live browser render
1. All SVG text has effective computed font size ≥ 2.45 mm.
2. No two text elements' boxes overlap.
3. All text boxes lie within x 12–408 and y 12–285.
4. Occlusion: sample the center of every text element and station number with `document.elementFromPoint`; the topmost element must be that text.
5. No stroked line, path or polygon crosses a text box, sampled along its full length, **including every polygon's closing edge**.
6. Computed text fill equals the declared color. Text fills come from ink, muted, a phase color or safety, with contrast ≥ 4.5:1 on white. Each white number is tested against its own disc.
7. Only palette tokens appear in the SVG. No `filter`, gradient, pattern, `<image>` or external URL.
8. **Copy is read from BRIEF.md, not `content.py`.** Parse section 4's backticked strings and tables and confirm each exists on the page. Each stage's strings must have that stage's `data-stage` value, in field order.
9. Eleven stations numbered 0–10; times total 19 weeks; state bar has 25 segments grouped 7/2/16; action bar has 9 grouped 7/2; group gaps are at least twice the gap between segments.
10. Metro line: one continuous path sequence from station 0 to station 10, with no gaps other than station discs; it crosses no text.
11. Robot: exactly six joint marks; cup, tabletop and button above the plane; table leg crosses it; ray stops at its hit point; cup within ±30° of the head camera axis, with unobstructed sightlines from both cameras; cup within the arm's maximum reach; elbow angle within 120–150°.
12. Shared baselines: each field across the columns of a poster row has an identical y value.
13. Column positions come from the one grid: every field's x lies on a grid constant.
14. `pdffonts` shows only intended font families. Each non-ASCII glyph is present in its intended font.
15. PDF: one page at A3 size; selectable text; PDF, PNG and SVG are newer than or the same age as the source files.
16. SVG `width`, `height`, `viewBox`, `<title>`, `<desc>`; HTML `@page`; PNG 3× scale; only permitted stroke weights.

### Required working method
Passing checks does not mean it is beautiful.
1. Write `content.py`, then the checks, then a first full layout.
2. Render the PNG and view it with your read tool, whole and in zoomed crops. If you cannot view images, say so plainly in `CODER_REPORT.md`.
3. Criticize it as a demanding art director and as a roboticist. Name the three worst things, and fix them.
4. Do at least three such passes. Finish only when `check_map.py` passes on the final files.

## 7. Round 2 rulings (binding)

These are the professor's rulings on `REVIEW_round1.md` and on a separate inspection of the build. Where this section differs from the review, this section wins.

### Accepted review findings
D1, B1, C1, C2, A1, C3, C4, C5 and D2 must all be resolved. The copy and geometry changes for B1 and A1 are already in sections 3 and 4.

### Layout
1. **Snake route.** Rebuild band B as section 3 now states, with stations above fields in both rows. Remove the double-line sandwich. Keep every field's text right edge at x ≤ 403, so the right-margin channel stays clear. Band B's dominance must survive: the route should read as one thick journey around the page, not as two separate lines.
2. **One grid, exactly.** Let `G` be the six stage-column left edges. Band A and band C panels must start at x = 12, `G[2]` and `G[4]`, with those same seams in both bands. Add a check that every band heading and panel left edge lies on x = 12 or a value in `G`.
3. **Panel bottoms.** The lowest lines of the three band C panels end on a common baseline, within 0.5 mm, with at least 3 mm of clear space above the footer.
4. **Body size.** Band A's lead, pipeline sentences and the parts table use body size 2.75 mm. Do not shrink them to fit: use the wider panels.

### Drawing and data flow
5. **Trained policies reach both Orins.** Draw one return line from DGX Spark with one branch and two arrowheads, one on Station Orin and one on Robot Orin. Robot Orin runs ACT directly, so a policy must visibly reach it. Nothing connects DGX Spark to the robot's real-time loop other than this file transfer.
6. Fix the wrist camera with a short bracket touching the forearm. Trim the floor line at the wall. Ensure the hit mark sits exactly on the leg.

### Typography
7. **Keep numbers with units.** Never break a line between a number and its unit or noun, such as `1 m`, `5 cm`, `10 cm`, `3 s`, `15 cm`, `9 of 10`, `16 of 20`, `14 of 20`, `6 of 10`, `20 trials`. Use a non-breaking rule in wrapping, and add a check that fails on any such line end.
8. Avoid single-word last lines where wrapping can avoid them.

### Checks
9. Check 8 must parse all section 4 copy, including tables in bands A and C.
10. Check each station disc against its stage's phase color.
11. Check the ray against every solid shape in the drawing.
12. Add a clean-build test: copy `src/` and `BRIEF.md` to a fresh temp directory, build there, and compare SVG, HTML and PNG bytes with the deliverables.
13. Check that exactly two arrowheads terminate the trained-policies return, on the correct nodes.

## 8. Round 3 rulings (binding)

These are the professor's rulings on `REVIEW_round2.md`. Where this section differs from that review, this section wins. Sections 3 and 4 already carry the copy and geometry changes.

### Accepted findings
2-A1, 2-A2, 2-A3, 2-A4, 2-B1, 2-B2, 2-B3, 2-C1, 2-C2, 2-C3, 2-C4, 2-C5, 2-D1, 2-D2, 2-D3 and 2-D4 must be resolved, as ruled below.

### Route
1. **Left turn.** The return line runs left through the corridor, then makes one straight 45° descent down-left into station 6's disc. There is no hook, U-turn or lead-in beyond the disc. Removing the second safety bracket gives the corridor extra clearance: use it, and aim for at least 4 mm of air above and below the return line.
2. **Terminus.** Station 10 has a visible white gap of at least 0.5 mm between disc and outer ring. Check the gap geometrically.

### Band A
3. **State and action bars.** Keep the notes. Do not add labels. Make group gaps at least twice the gap between segments, so 7/2/16 reads without counting. This replaces the labels suggested by 2-B4.

### Band C
4. **Datasets arrow.** Station Orin to DGX Spark has exactly one head, at DGX Spark.
5. **How to master it.** Rule spacing is natural, not stretched. The reasons added to section 4 fill the panel. Bottom alignment with the other panels comes from this content; if it does not fall within 0.5 mm, adjust the ladder-to-rules gap only.
6. **Ladder arrows.** Each arrow sits at the middle of the gap between the end of one step's text and the next heading, clearing both by at least 1.5 mm.
7. **Lidar drawing.** Keep it at least 32 mm tall. With its height given, spread the three labels around the ray so that none needs a second look.

### Header and page
8. Keep at least 1 mm between the subtitle's descenders and the header rule.
9. Row 1's Pass field grows to three lines in stages 2 and 3. Pay for this first from band A's airy parts-table spacing and from the removed bracket. Never go below the type sizes.

### Engineering
10. Check all three flow links' heads: Robot↔Station has 2; Station→Spark has 1, at Spark; Spark→Orins has 2, at the two Orins.
11. Assert each text role's expected style: Pass is ink demi; Explain is muted regular; time is muted; the safety label is safety color; station numbers are white demi.
12. Number-and-noun rule: `1 m squares` stays unbroken. Strengthen check 17 to test the protected phrases listed in section 7 and this one, rather than only a bare-number regex.
13. Unlink all four outputs before rendering. Strip the XML declaration from the SVG when inlining it in HTML.
14. Check 8 verifies location for header, footer, band C roles, ladder and rules, not only page-wide presence.

## 9. Round 4 rulings (binding, narrow)

Only these items change. Do not touch anything else on the page. Section 9 wins over earlier sections.

### Robot drawing: side grasp
Stage 7 teaches a side grasp, so the drawing must show one. The current top-down gripper cluster contradicts it.
1. The final hand link is **horizontal**, entering from the left at cup height. The two jaws lie horizontally, open toward the cup, with about 4 mm clear of the cup's left side. In side view, draw the jaws so that a reader sees a hand approaching the side of a cup. The gripper must not sit above the cup.
2. The hand's top lies below the cup's rim. The wrist joint lets the last link be horizontal, so the forearm may slope down to it.
3. Elbow angle may be 95–150°. Keep exactly six joint marks. The wrist must be within the computed maximum reach.
4. The head camera's mast may be as tall as needed. The lens is high enough that a straight sightline from lens to the cup's rim clears every link and joint of the arm. Assert this in code, and check it against every arm segment. A wrist camera sits on the last link, with a clear view of the cup ahead of the jaws.
5. Figure height may rise to 38 mm. Band C's natural bottoms still align. Pay for this from the lidar panel's own space.
6. Labels: each sits beside its object with no leader lines and needs no second look. Move `wrist camera` clear of the arm. Keep `lidar`, `lidar plane` and `ray stops here` spaced evenly along the ray.
7. Do not add marks. Simplify: fewer small shapes around the hand than now.

### Safety bracket
8. The bracket has a left tick at station 2 and **no** right tick. Its top rule ends above station 5, before the route's turn, so it reads as continuing. Add a check that exactly one tick exists.

### Finish
9. `check_map.py` must assert items 1–4 and 8. Keep every other check passing.
