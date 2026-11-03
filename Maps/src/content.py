# -*- coding: utf-8 -*-
"""All copy for the poster, kept apart from layout.

Backticks mark inline code: the text is rendered in the monospace face, the
backticks themselves never appear on the page.  Nothing here may drift from
section 4 of BRIEF.md; check_map.py reads the brief, never this file.
"""

# ---------------------------------------------------------------- header
TITLE = "The LeRobot Learning Roadmap"

SUBTITLE = ("From ROS 2 and OpenCV skills to a two-wheeled 6+1 DoF arm that "
            "presses a button and picks up a cup.")

HOWTO = "Follow the numbers. Move on only when you can meet Pass and answer Explain."

PHASES = [("prepare", "Prepare"), ("build", "Build the robot"),
          ("teach", "Teach"), ("mission", "Mission")]
SAFETY_KEY = "Safety and limits"

# ---------------------------------------------------------------- band A
A_HEAD = "How LeRobot works"

A_LEAD = ("LeRobot learns a task by copying you. You drive the robot, it saves "
          "what the robot sensed and what you commanded, and a neural network "
          "learns to produce the same commands from the same observations.")

PIPELINE = [
    ("Teleoperate",
     "You command the robot with a leader arm and gamepad. Nothing is learned yet.",
     "lerobot-teleoperate"),
    ("Record",
     "Each attempt becomes an episode: video, state and action at every time step.",
     "lerobot-record"),
    ("Train",
     "A policy learns to predict your actions from each recorded observation.",
     "lerobot-train"),
    ("Deploy",
     "The policy drives the robot. You count real successes, not training loss.",
     "lerobot-rollout"),
]

LOOP_LABEL = "Improve: take over when it fails. Your corrections become new data."
LOOP_CMD = "--strategy.type=dagger"

PARTS_HEAD = "The five parts"
PARTS = [
    ("Robot",
     "Your hardware as a Python class: `get_observation()` reads it, "
     "`send_action()` moves it."),
    ("Teleoperator",
     "The human as a Python class: `get_action()` returns your command."),
    ("Processor",
     "Converts and limits data between teleoperator, dataset and robot."),
    ("LeRobotDataset",
     "Numbers in Parquet, video in MP4, schema and statistics in `meta/`."),
    ("Policy",
     "A network that turns one observation into a chunk of future actions."),
]

TIME_HEAD = "One time step in your dataset"
TIME_ROWS = [
    ("observation.images.wrist", None, "video"),
    ("observation.images.head", None, "video"),
    ("observation.state", "state", "25 numbers: 7 arm + 2 base + 16 lidar"),
    ("action", "action", "9 numbers: 7 arm + x.vel + theta.vel"),
]
TIME_NOTE = ("Predicting a chunk of actions at once keeps motion smooth and "
             "limits compounding errors.")

# ---------------------------------------------------------------- band B
B_HEAD = "The roadmap"

FIELD_LABELS = ["Learn", "Do", "On", "Pass", "Explain"]

SAFETY_LABEL = ("From stage 2 to the end, before any motor moves: e-stop in "
                "reach, joint and speed limits set, watchdog armed, arm stowed "
                "while driving.")

STAGES = [
    dict(n=0, phase="prepare", title="Set up the machines", time="1 week",
         learn="Python 3.12 environments, CUDA wheels on ARM, why versions must match.",
         do="Install LeRobot v0.6.0 on the Spark and both Orins. Keep ROS 2 outside the environment.",
         on="Spark \u00b7 Robot Orin \u00b7 Station Orin",
         passed="A real CUDA computation runs on all three, with the same LeRobot version.",
         explain="Why can a generic torch wheel fail on Orin?"),
    dict(n=1, phase="prepare", title="Read the framework", time="1 week",
         learn="Dataset format, ACT, action chunks, normalization statistics.",
         do="Load a public dataset in Python, train ACT on it, and trace one frame from dataset to predicted action.",
         on="Spark",
         passed="Plot predicted against recorded actions on an episode kept out of training.",
         explain="Why is low training loss not the same as task success?"),
    dict(n=2, phase="build", title="Write the robot driver", time="3 weeks",
         learn="Robot class, motor bus, calibration, plugin packaging, two-wheel kinematics.",
         do="Write `lerobot_robot_mobile_arm`: 6+1 joints, `x.vel`, `theta.vel`, both cameras, calibration, joint limits, hardware e-stop, watchdog.",
         on="Robot Orin",
         passed="Joints stay within limits. E-stop and watchdog stop it 5 of 5. Ten 1 m squares each close within 10 cm.",
         explain="Why is there no `y.vel` in your action?"),
    dict(n=3, phase="build", title="Add the lidar", time="1 week",
         learn="Scan timing, masking the robot's body, reducing a scan to 16 sectors.",
         do="Add `lidar.s00` to `lidar.s15` to the observation. Slow and stop `x.vel` inside `send_action`, whatever a policy asks.",
         on="Robot Orin",
         passed="All 16 sectors log at scan rate with the body masked. Driven at a wall 10 times at top speed, it stops at least 15 cm away.",
         explain="What can a single lidar plane never see?"),
    dict(n=4, phase="build", title="Connect teleoperation", time="2 weeks",
         learn="Teleoperator class, processors, robot host and client over a network.",
         do="Combine the powered leader arm and gamepad into one 9-number action. Run the host on Robot Orin.",
         on="Robot Orin \u00b7 Station Orin",
         passed="You complete both tasks 9 of 10 times, watching only the camera feeds.",
         explain="If you cannot do it from the sensors alone, why can the policy not?"),
    dict(n=5, phase="build", title="Record clean data", time="1 week",
         learn="Episodes, replay, the dataset visualizer, what makes a good demonstration.",
         do="Fix camera mounts and lighting. Record 10 test episodes and move them to the Spark.",
         on="Station Orin \u2192 Spark",
         passed="Parked-base replay repeats the task. Feature and camera names are frozen.",
         explain="Why does renaming a camera break a trained policy?"),
    dict(n=6, phase="teach", title="Press the button", time="2 weeks",
         learn="Demonstration variety, ACT training, rollout, reading failures from recorded episodes.",
         do="Three steps: parked base, small start offsets, approach from 1 m. Start with 50 demos; add more where it fails.",
         on="Station Orin \u2192 Spark \u2192 Robot Orin",
         passed="From 1 m: at least 16 of 20 presses, with no tipping.",
         explain="Which failures come from data, and which from hardware?"),
    dict(n=7, phase="teach", title="Pick up the cup", time="3 weeks",
         learn="Grasp variety, friction, ACT against Diffusion Policy on the same trials.",
         do="Empty opaque cup, side grasp, same three steps. Add harder cups only after it passes.",
         on="Station Orin \u2192 Spark \u2192 Robot Orin",
         passed="At least 14 of 20: lifted 5 cm, upright, held for 3 s.",
         explain="Why compare policies on identical trials?"),
    dict(n=8, phase="teach", title="Teach by correcting", time="2 weeks",
         learn="DAgger, compounding errors, merging datasets, fine-tuning.",
         do="Roll out with `--strategy.type=dagger`, take over before failure, and fine-tune on demos plus corrections.",
         on="Robot Orin \u00b7 Station Orin \u2192 Spark",
         passed="Beats the earlier policy on the same 20 trials, or you can explain why not.",
         explain="Why do corrections teach what demonstrations cannot?"),
    dict(n=9, phase="teach", title="One model, two tasks", time="2 weeks",
         learn="SmolVLA, language prompts, async inference, Real-Time Chunking.",
         do="Fine-tune `smolvla_base` on the Spark with one prompt per task. Serve it from Station Orin to the robot.",
         on="Spark \u2192 Station Orin \u2192 Robot Orin",
         passed="On 20 trials per task, compared with your two ACT policies. Either result is fine if explained.",
         explain="What does RTC fix, and what does async inference fix?"),
    dict(n=10, phase="mission", title="Run the mission", time="1 week",
         learn="Sequencing policies, success checks with OpenCV, failure analysis.",
         do="Write a Python script: approach, press, confirm the light, pick up the cup. Log every run.",
         on="Robot Orin \u00b7 Station Orin",
         passed="At least 6 of 10 full missions, failures classified by cause, and a live demo.",
         explain="Where would your next 50 demonstrations go, and why?"),
]

AFTER_HEAD = "After the mission"
AFTER = [
    "Navigate a room: ROS 2 and Nav2 with the lidar.",
    "Learn on the robot: HIL-SERL for short arm-only tasks.",
    "Try larger models: Pi0.5 fits in Spark memory, but expect long runs.",
    "Share it: publish your dataset and model card on the Hub.",
]

# ---------------------------------------------------------------- band C
P1_HEAD = "Three computers, three jobs"
P1_NODES = ["Robot Orin", "Station Orin", "DGX Spark"]
P1_FLOW_LABELS = ["wired network", "datasets", "trained policies"]
P1_ROLES = [
    ("Robot Orin", "on the chassis",
     "Motors, cameras, lidar and safety. Runs ACT directly. Budget its power on the battery."),
    ("Station Orin", "on the bench",
     "Leader arm, gamepad, monitor. Records datasets to an added NVMe drive. Serves large policies."),
    ("DGX Spark", "in the lab",
     "Trains every policy, one job at a time, and keeps the master datasets. Never in the control loop."),
]
P1_WORK = "Most stages: record on Station Orin, train on the Spark, run on Robot Orin."
P1_TIMING = ("Plan overnight runs: one published SmolVLA example, 20,000 steps at "
             "batch 64, took about 30 h on a Spark. Time your own first run.")
P1_SETUP = [
    "Spark: `uv venv --python 3.12`, then install from the v0.6.0 tag.",
    "Orin: JetPack 7.2 and Python 3.12. Install the Jetson torch wheel first, "
    "then `pip install lerobot==0.6.0 --no-deps` and its dependencies by hand. "
    "This recipe was tested on Orin NX, so verify it on AGX.",
    "Both are ARM machines, so LeRobot decodes video with PyAV.",
]

P2_HEAD = "What one lidar plane sees"
P2_COPY = [
    "It scans one horizontal slice at chassis height. The drawing shows the "
    "robot parked for the cup; it drives elsewhere to press the button.",
    "Sees: walls, table legs, people's legs, and the button panel when nothing "
    "blocks it.",
    "Misses: the cup, the tabletop, the arm, stairs and drop-offs.",
    "So cameras find the targets. The lidar keeps distance and stops the base.",
    "LeRobot has no lidar class. Your driver reports 16 sector distances as floats, "
    "and they join observation.state.",
]

P3_HEAD = "How to master it"
P3_LADDER = ["Run it", "Explain it", "Change it", "Debug it"]
P3_LADDER_DEF = ["The command works.",
                 "You can say what it wrote and why.",
                 "You alter one part on purpose.",
                 "You fix a failure from the logs."]
P3_RULES = [
    ("Trace one frame by hand before you trust a command.",
     "Follow it from `get_observation()` to the dataset row to the policy output."),
    ("Watch your dataset before you train on it.",
     "A bad episode teaches bad behavior."),
    ("Change one thing per experiment, and write it down.",
     "Otherwise you cannot tell what helped."),
    ("Count real successes as k of n.",
     "8 of 10 still allows a true rate of 49\u201394% (95% Wilson interval)."),
    ("When the docs and the robot disagree, read the source.",
     "LeRobot changes quickly, and the code is the final word."),
]

# ---------------------------------------------------------------- drawing
# Labels of the lidar drawing (BRIEF section 3, "Robot drawing").
D_LABELS = {
    "lidar": "lidar",
    "plane": "lidar plane",
    "hit": "ray stops here",
    "head": "head camera",
    "wrist": "wrist camera",
    "cup": "cup",
    "button": "button",
    "leg": "table leg",
    "caster": "caster",
}

# ---------------------------------------------------------------- footer
FOOT_LEFT = ("Times are planning estimates at about 8 hours per week, about 19 "
             "weeks in total. Pass targets are starter values: tune them to your "
             "hardware and justify the change.")
FOOT_RIGHT = ("Checked Nov 2026 against LeRobot v0.6 docs. Commands and flags "
              "change between releases, so pin one version and use `--help`.")
