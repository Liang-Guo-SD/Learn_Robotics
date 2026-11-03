# -*- coding: utf-8 -*-
"""All copy for the Mobile Manipulator Learning Map.

Copy is BRIEF.md section 4, transcribed once. Layout lives in build_map.py.
Mathematics uses runs of (kind, text):
    ("i", ..) italic variable      ("n", ..) upright
    ("sub", ..) subscript          ("sup", ..) superscript
"""

# ---------------------------------------------------------------- header
TITLE = "Mobile Manipulator Learning Map"
GOAL = ("From basic Linux and Python to a two-wheeled robot arm that presses a "
        "button and picks up an object.")
HOW_TO = ("Follow the numbers. Do not move on until you meet Pass. Build in "
          "simulation first, then on the real robot.")
PHASE_KEY = [
    ("Prepare", "prepare"),
    ("Build the classical robot", "classical"),
    ("Add learning", "learned"),
    ("Mission", "mission"),
]
SAFETY_KEY = "Safety and limits"

# ---------------------------------------------------------------- section A
A_HEAD = "One robot, one idea"

EQ1 = [
    ("sup", "W"), ("i", "T"), ("sub", "H"), ("n", " = "),
    ("sup", "W"), ("i", "T"), ("sub", "B"),
    ("n", "("), ("i", "x"), ("n", ", "), ("i", "y"), ("n", ", "),
    ("i", "θ"), ("n", ") · "),
    ("sup", "B"), ("i", "T"), ("sub", "H"),
    ("n", "("), ("i", "q"), ("n", ")"),
]
EQ1_PLAIN = "W T_H = W T_B(x, y, \u03b8) \u00b7 B T_H(q)"
EQ1_CAPTION = ("Hand in world = base in world × hand relative to base "
               "(q = joint angles).")
EQ2 = [
    ("sup", "B"), ("i", "T"), ("sub", "O"), ("n", " = "),
    ("sup", "B"), ("i", "T"), ("sub", "C"), ("n", " · "),
    ("sup", "C"), ("i", "T"), ("sub", "O"),
]
EQ2_PLAIN = "B T_O = B T_C \u00b7 C T_O"
EQ2_CAPTION = ("Target from base = camera from base (calibration) × target "
               "from camera (vision).")
KEY_INSIGHT = ("Wheel odometry drifts. So park, look again, and act from the "
               "base frame.")
FRAME_KEY = ("T = pose of one frame in another. W world · B base · C camera · "
             "H hand · O target.")
REF_NOTE = ("Reference robot: two driven wheels and a passive caster, so it "
            "stands still when powered off.")

# physics small multiples
PHYS = [
    dict(
        title="No sideways motion",
        formula=[
            ("i", "v"), ("n", " = "), ("i", "r"), ("n", "("),
            ("i", "ω"), ("sub", "R"), ("n", " + "), ("i", "ω"), ("sub", "L"),
            ("n", ")/2"),
        ],
        formula2=[
            ("i", "ω"), ("n", " = "), ("i", "r"), ("n", "("),
            ("i", "ω"), ("sub", "R"), ("n", " − "), ("i", "ω"), ("sub", "L"),
            ("n", ")/"), ("i", "b"),
        ],
        sentence=("Wheels roll, they do not slide. Moving 5 cm left takes a "
                  "manoeuvre, so choose your parking pose carefully."),
        key_runs=[("i", "r"), ("n", " wheel radius · "), ("i", "b"),
                  ("n", " track width")],
    ),
    dict(
        title="Keep the COM inside",
        formula=[("n", "Stable: centre of mass (COM) ground point inside the "
                       "support polygon.")],
        sentence=("Stow the arm before driving. Low batteries resist tipping "
                  "under braking, but reaching still moves the ground point."),
    ),
    dict(
        title="Count the constraints",
        formula=[("n", "press = 3 position + 2 axis = 5")],
        sentence=("A 5-joint arm has no spare joint for this. Turning the base "
                  "adds one. Counting is necessary, not sufficient."),
    ),
    dict(
        title="Friction holds it",
        formula=[
            ("n", "2 "), ("i", "μ"), ("n", " "), ("i", "F"), ("sub", "n"),
            ("n", " ≥ "), ("i", "m"), ("n", " "), ("i", "g"),
        ],
        sentence=("Squeeze force and surface friction must carry the weight. "
                  "Soft, grippy fingertips help most."),
        key_runs=[("i", "μ"), ("n", " friction coefficient · "), ("i", "F"),
                  ("sub", "n"), ("n", " grip force")],
    ),
]

# ---------------------------------------------------------------- section B
B_HEAD = "The route"
ROW_LABELS = [("Time", "time"), ("Learn", "learn"), ("Build", "build"),
              ("Pass", "pass")]

STOPS = [
    dict(n=0, phase="prepare", title="Toolbelt", time="3 weeks",
         learn="Git, Python environments, NumPy transforms, ROS 2 nodes and topics.",
         build="Two ROS 2 nodes that talk. A transform library in NumPy.",
         passed="Your composed transforms match a hand calculation."),
    dict(n=1, phase="prepare", title="Describe", time="2 weeks",
         learn="URDF robot models, the TF frame tree, RViz, mass and centre of mass.",
         build="A simulated model of your robot with masses.",
         passed="Full TF tree. COM stays inside support in every planned arm pose."),
    dict(n=2, phase="classical", title="Drive", time="3 weeks",
         learn="Differential drive, encoders, PID wheel control, odometry, ros2_control.",
         build="Velocity-controlled base, in simulation and then real.",
         passed="E-stop and watchdog stop it 5 of 5. Drive a 1 m square 10 times: "
                "closing error ≤ 10 cm."),
    dict(n=3, phase="classical", title="Reach", time="3 weeks",
         learn="Forward and inverse kinematics, joint limits, trajectories, MoveIt 2.",
         build="Arm that moves its tip to commanded points.",
         passed="Touch 5 marked points, 10 times each: mean error ≤ 10 mm, "
                "worst ≤ 20 mm."),
    dict(n=4, phase="classical", title="See", time="2 weeks",
         learn="Camera model, calibration, AprilTag poses, hand–eye calibration, OpenCV.",
         build="Pipeline that gives a target pose in the base frame.",
         passed="Point at a tag in 5 positions: error ≤ 15 mm."),
    dict(n=5, phase="classical", title="Press", time="2 weeks",
         learn="Parking pose, slow approach, contact detection, force limits.",
         build="First task: drive to a panel and press a button.",
         passed="From 1 m away: at least 16 of 20 presses, no tipping."),
    dict(n=6, phase="classical", title="Pick", time="3 weeks",
         learn="Grasp poses, friction, object detection, state machines, recovery on failure.",
         build="Second task: find, grasp and lift one object.",
         passed="At least 14 of 20 picks, with failures logged by cause."),
    dict(n=7, phase="learned", title="Learn", time="6 weeks",
         learn="Teleoperation, demonstration data, PyTorch training basics, ACT and "
               "Diffusion Policy, LeRobot.",
         build="A policy trained from your own demonstrations for the pick.",
         passed="Compare with stop 6 on the same 20 trials. Either result is valid "
                "if you can explain it."),
    dict(n=8, phase="mission", title="Mission", time="2 weeks",
         learn="System integration, behaviour trees, rosbag2 logs, failure analysis.",
         build="Drive, press, pick and return as one program.",
         passed="At least 6 of 10 logged missions succeed, failures classified, "
                "and a demo."),
]

SAFETY_BRACKET = ("Before real motors, test: e-stop in reach, speed and joint "
                  "limits, command watchdog. Stow the arm while driving.")
GPU_NOTE = "GPU needed only at stop 7. LeRobot usually needs a thin bridge to ROS 2."
MEASURE_NOTE = ("Report k of n, not a percentage. 8 of 10 is compatible with a "
                "true rate of 49–94% (95% Wilson interval), so use 20 or more "
                "trials to compare.")

# ---------------------------------------------------------------- section C
C_HEAD = "How it fits"

LOOP_TITLE = "What runs on the robot"
LOOP_NODES = [
    ("Sense", "camera · wheel encoders · joint encoders · servo load"),
    ("Estimate", "odometry · tag pose · TF frames"),
    ("Decide", "state machine · planner · policy"),
    ("Act", "wheel PID · joint control · gripper"),
    ("Physics", "gravity · slip · contact"),
]
RATES = ("Typical rates: control 50–100 Hz · camera 30 Hz · policy 10–30 Hz · "
         "task about 1 Hz")
SAFETY_BAND = "Safety overrides everything."

IMPROVE_TITLE = "How you improve it"
IMPROVE_STEPS = ["Model", "Simulate", "Run on robot", "Log", "Measure",
                 "Change one thing"]

TABLE_TITLE = "Five ways to decide"
TABLE_HEAD = ["Method", "You supply", "Breaks when", "Stop"]
TABLE = [
    ("Scripted state machine", "Steps and thresholds",
     "The situation was not planned for", "5–6"),
    ("Model-based planning", "Robot and scene geometry",
     "The model or sensing is wrong", "3–6"),
    ("Imitation learning", "Human demonstrations",
     "The scene differs from the demos", "7"),
    ("Reinforcement learning", "Simulator and reward",
     "The reward or simulator misleads", "Next"),
    ("Foundation models (VLA)",
     "Pretrained vision-language-action model, your data",
     "Too slow, or failures are hard to explain", "Next"),
]

AFTER_TITLE = "After the mission"
AFTER = [
    "Reach while moving: whole-body control",
    "Self-balance on two wheels: inverted pendulum, IMU, LQR",
    "Map the room: SLAM and Nav2",
    "Train in simulation: RL with MuJoCo Playground or Isaac Lab (GPU)",
    "Take instructions: foundation models such as SmolVLA",
]

# ---------------------------------------------------------------- footer
FOOT_L = ("Times are planning estimates at about 8 hours per week, about 26 "
          "weeks in total, not measurements. Pass targets are starter values: "
          "tune them to your hardware and justify the change. Learn lists the "
          "words to search for.")
FOOT_R = ("Reference kit, checked Nov 2026: SO-101 arm (5 joints + gripper) · 2 "
          "geared DC motors with encoders · caster · single-board computer · "
          "camera · Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic. One option, not "
          "an endorsement. Check driver support before choosing a newer ROS 2.")

# ---------------------------------------------------------------- labels
# Words the brief asks for on the drawing: section 3 requires support and COM;
# section 7 item 4 permits object, button, battery and caster; section 4 names
# the quantities v, free, F_n, mg and the frame letters.
LBL = dict(world="W", base="B", cam="C", hand="H", obj="O")


def _runs_text(runs):
    return "".join(t for _, t in runs)


def exact_copy():
    """Every string section 4 requires, as the page renders it.

    The two transform equations are set with raised/lowered letters, so the
    character stream is WTH = WTB(x, y, θ) · BTH(q); that plain form is what the
    page text contains. The checker does not read this function: it derives the
    expected copy from BRIEF.md itself.
    """
    out = [TITLE, GOAL, HOW_TO, SAFETY_KEY, A_HEAD,
           "WTH = WTB(x, y, θ) · BTH(q)", EQ1_CAPTION,
           "BTO = BTC · CTO", EQ2_CAPTION,
           KEY_INSIGHT, FRAME_KEY, REF_NOTE, B_HEAD, SAFETY_BRACKET, GPU_NOTE,
           MEASURE_NOTE, C_HEAD, LOOP_TITLE, RATES, SAFETY_BAND, IMPROVE_TITLE,
           TABLE_TITLE, AFTER_TITLE, FOOT_L, FOOT_R]
    out += [lab for lab, _ in PHASE_KEY]
    for p in PHYS:
        out.append(p["title"])
        out.append(_runs_text(p["formula"]))
        if "formula2" in p:
            out.append(_runs_text(p["formula2"]))
        out.append(p["sentence"])
        if "key_runs" in p:
            out.append(_runs_text(p["key_runs"]))
    for p in PHYS:
        out.append(p["title"])
    out += IMPROVE_STEPS + AFTER + TABLE_HEAD
    for row in TABLE:
        out += list(row)
    for name, parts in LOOP_NODES:
        out += [name, parts]
    for s in STOPS:
        out += [s["title"], s["time"], s["learn"], s["build"], s["passed"]]
    return out
