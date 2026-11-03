# -*- coding: utf-8 -*-
"""Build the Mobile Manipulator Learning Map.

    python src/build_map.py [--render]

Geometry is computed from named constants; every millimetre on the page is
either a margin, a grid line, or derived from the physics drawn in section A.
"""

import json
import math
import re
import subprocess
import sys
from html import escape
from pathlib import Path

import content as C

# --------------------------------------------------------------------------
# page, grid, palette, type
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / ".tmp"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PW, PH = 420.0, 297.0            # page, mm
M = 12.0                          # margin
CR = PW - M                       # content right edge = 408
GRID = 33.0                       # 12-column grid unit

INK = "#1B2430"
MUTED = "#566070"
HAIR = "#C7CDD6"
PREPARE = "#0B5F9E"
CLASSICAL = "#00695C"
LEARNED = "#8A2F6B"
MISSION = "#1B2430"
SAFETY = "#B5420A"
PHASE_COLOR = dict(prepare=PREPARE, classical=CLASSICAL, learned=LEARNED,
                   mission=MISSION)

SANS = '"Avenir Next","Helvetica Neue",Helvetica,Arial,sans-serif'
MATH = '"STIX Two Text","Times New Roman",serif'

SZ_TITLE, SZ_HEAD, SZ_STOP, SZ_BODY, SZ_SMALL = 13.0, 4.4, 3.6, 2.75, 2.45
LH_BODY, LH_SMALL = 3.85, 3.45

W_HAIR, W_MED, W_BOLD = 0.25, 0.5, 1.6
W_LINK = 0.8

# --------------------------------------------------------------------------
# header
# --------------------------------------------------------------------------
H_TITLE_BASE = 25.3
H_GOAL_BASE = 33.6
H_KEY_BASE = 17.2
H_HOW_X = 286.0
H_HOW_W = CR - H_HOW_X
H_KEY_SW, H_KEY_SWGAP, H_KEY_GAP = 2.6, 1.5, 5.0

# --------------------------------------------------------------------------
# section A — robot, side view, floor on FLOOR
# --------------------------------------------------------------------------
A_HEAD_BASE = 45.0
FLOOR = 101.0
FLOOR_X0, FLOOR_X1 = 22.0, 142.0
CH_X0, CH_X1 = 44.0, 84.0
CH_TOP, CH_BOT = 80.0, 90.4
WHEEL_X, WHEEL_R = 54.0, 6.0
WHEEL_Y = FLOOR - WHEEL_R
CASTER_X, CASTER_R = 82.0, 1.9
CASTER_Y = FLOOR - CASTER_R
BATTERY = (45.4, 83.4, 52.0, 87.6)
MAST_X, MAST_TOP = 50.0, 68.8
CAM_C, CAM_ANG = (51.6, 68.9), -30.0
CAM_W, CAM_H = 5.4, 2.4
BASE_X, BASE_Y = 78.0, 80.0
SHOULDER = (78.0, 76.6)
L1, L2 = 38.0, 30.0
R_SHOULDER, R_ELBOW, R_WRIST, R_ROLL = 3.6, 3.0, 2.2, 1.1
W_UPPER, W_FORE, W_WRIST = 6.0, 4.6, 3.2
WALL_X, WALL_TOP = 142.0, 60.0
BUTTON_FACE, BUTTON_Y, BUTTON_H = 139.4, 76.0, 2.6
WRIST = (129.0, 76.0)
ROLL_X = 132.2
TIP_X = 136.5
COM = (64.0, 77.4)
SUPPORT_Y = 103.4
OBJECT = (116.0, 94.5, 6.0)
OBJECT_FRAME = (122.0, 94.5)

EQ_X, EQ_W = 158.0, 96.0
EQ1_BASE = 52.2
EQ2_BASE = 63.2
INSIGHT_BASE = 75.4
FRAMEKEY_BASE = 88.6
REF_BASE = 97.4

PANEL_X0, PANEL_W, PANEL_GAP = 262.0, 69.0, 8.0
PANEL_ROW_Y = (48.9, 81.3)
PANEL_TITLE_DY = 3.3
DIA_TOP_DY, DIA_BOT_DY = 4.6, 17.0
FORM_DY = 18.3
SENT_DY = 22.6
KEY_DY = 29.6

# --------------------------------------------------------------------------
# section B — the route
# --------------------------------------------------------------------------
B_HEAD_BASE = 116.6
SAFE_LABEL_BASE = 123.0
SAFE_BR_Y, SAFE_BR_TICK = 126.4, 1.8
LINE_Y = 134.4
STN_R = 4.25
TICK_END = 141.2
COL_X0, COL_N = 27.0, 9
COL_W = (CR - COL_X0) / COL_N
TXT_INSET = 2.1
TXT_W = COL_W - 2 * TXT_INSET
ROW_LABEL_X = 23.0
B_TITLE_BASE = 145.4
B_TIME_BASE = 149.9
LEARN_B1 = 154.8
BUILD_B1 = 170.4
PASS_RULE_Y = 179.8
PASS_B1 = 183.0
NOTE_BASE = 199.2

# --------------------------------------------------------------------------
# section C — how it fits
# --------------------------------------------------------------------------
C_HEAD_BASE = 216.8
PANEL_TITLE_BASE = 224.6
C_X0, C_X1 = M, 152.0
TBL_X0, TBL_X1 = 160.0, 331.0
AFT_X0, AFT_X1 = 340.0, CR
LOOP_TOP = 227.6
P1_RATES = 248.4
SAFE_RULE_Y = 250.9
SAFE_TEXT = 255.4
P2_TITLE = 260.8
IMPROVE_BASE = 265.6
IMPROVE_RETURN = 271.6
TBL_HEAD_BASE = 229.9
TBL_RULE_Y = 231.6
TBL_B1 = 235.4
TBL_COLS = [(160.0, 34.0), (198.0, 45.0), (247.0, 66.0), (317.5, 13.0)]
AFT_B1 = 229.9

# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------
F_BASE = 280.4
F_W = 194.0
F_LH = 3.45

# --------------------------------------------------------------------------
# text measurement through headless Chrome
# --------------------------------------------------------------------------
CACHE_FILE = TMP / "measure.json"
_cache = {}
_pending = {}


def _load_cache():
    global _cache
    if CACHE_FILE.exists():
        try:
            _cache = json.loads(CACHE_FILE.read_text())
        except Exception:
            _cache = {}


def measure(text, size, weight="400", family=SANS, ital=False):
    key = "%s|%s|%s|%s|%s" % (family, weight, size, int(bool(ital)), text)
    if key in _cache:
        return _cache[key]
    if key not in _pending:
        _pending[key] = (text, size, weight, family, bool(ital))
    return 0.5 * size * len(text)


def flush_measurements():
    if not _pending:
        return
    TMP.mkdir(exist_ok=True)
    items = list(_pending.items())
    payload = [[t, s * 10.0, w, f, i] for (t, s, w, f, i) in _pending.values()]
    html = """<!doctype html><meta charset="utf-8"><pre id="o">x</pre><script>
const items=%s, out=[];
const c=document.createElement('canvas').getContext('2d');
for (const [t,s,w,f,i] of items){ c.font=(i?'italic ':'')+w+' '+s+'px '+f;
  out.push(c.measureText(t).width/10); }
document.getElementById('o').textContent=JSON.stringify({w:out});
</script>""" % json.dumps(payload)
    f = TMP / "measure.html"
    f.write_text(html)
    dom = _chrome_dump(f)
    m = re.search(r'<pre id="o">(.*?)</pre>', dom, re.S)
    widths = json.loads(m.group(1).replace("&quot;", '"'))["w"]
    for (key, _), w in zip(items, widths):
        _cache[key] = w
    CACHE_FILE.write_text(json.dumps(_cache))
    _pending.clear()


def _chrome_dump(path):
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--virtual-time-budget=4000", "--dump-dom", path.as_uri()]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def wrap(text, width, size, weight="400", family=SANS):
    """Balanced ragged-right wrap: fewest lines, then the most even rag."""
    raw = text.split(" ")
    words = []                       # keep "·" glued to the word before it
    for w in raw:
        if w == "·" and words:
            words[-1] += " ·"
        else:
            words.append(w)
    n = len(words)
    wcache = {}

    def wspan(i, j):
        key = (i, j)
        if key not in wcache:
            wcache[key] = measure(" ".join(words[i:j]), size, weight, family)
        return wcache[key]

    for k in range(1, n + 1):
        memo = {}

        def best(i, left):
            if left == 1:
                w = wspan(i, n)
                return ((width - w) ** 2, [n]) if w <= width else (None, None)
            if (i, left) in memo:
                return memo[(i, left)]
            res = (None, None)
            for j in range(i + 1, n - left + 2):
                w = wspan(i, j)
                if w > width:
                    break
                c, breaks = best(j, left - 1)
                if c is None:
                    continue
                c += (width - w) ** 2
                if res[0] is None or c < res[0]:
                    res = (c, [j] + breaks)
            memo[(i, left)] = res
            return res

        cost, breaks = best(0, k)
        if cost is not None:
            out, s = [], 0
            for e in breaks:
                out.append(" ".join(words[s:e]))
                s = e
            return out
    return [text]


# --------------------------------------------------------------------------
# svg builder
# --------------------------------------------------------------------------
def n(v):
    s = ("%.3f" % v).rstrip("0").rstrip(".")
    return s if s != "-0" else "0"


class Builder:
    def __init__(self):
        self.parts = []
        self.texts = []
        self.stats = []

    # ---- shapes
    def line(self, x1, y1, x2, y2, color=INK, w=W_MED, cap="butt", cls=""):
        c = ' class="%s"' % cls if cls else ""
        self.parts.append(
            '<line%s x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" '
            'stroke-linecap="%s"/>' % (c, n(x1), n(y1), n(x2), n(y2), color, n(w), cap))

    def rect(self, x, y, w, h, color=INK, sw=W_MED, fill="none", cls=""):
        c = ' class="%s"' % cls if cls else ""
        self.parts.append(
            '<rect%s x="%s" y="%s" width="%s" height="%s" fill="%s" stroke="%s" '
            'stroke-width="%s"/>' % (c, n(x), n(y), n(w), n(h), fill, color, n(sw)))

    def circle(self, cx, cy, r, color=INK, sw=W_MED, fill="none", cls=""):
        c = ' class="%s"' % cls if cls else ""
        self.parts.append(
            '<circle%s cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>'
            % (c, n(cx), n(cy), n(r), fill, color, n(sw)))

    def path(self, d, color=INK, sw=W_MED, fill="none", cap="butt", cls=""):
        c = ' class="%s"' % cls if cls else ""
        self.parts.append(
            '<path%s d="%s" fill="%s" stroke="%s" stroke-width="%s" '
            'stroke-linecap="%s" stroke-linejoin="miter"/>'
            % (c, d, fill, color, n(sw), cap))

    def poly(self, pts, fill="none", stroke=INK, sw=W_MED, cls=""):
        c = ' class="%s"' % cls if cls else ""
        p = " ".join("%s,%s" % (n(x), n(y)) for x, y in pts)
        self.parts.append('<polygon%s points="%s" fill="%s" stroke="%s" '
                          'stroke-width="%s"/>' % (c, p, fill, stroke, n(sw)))

    def arrow(self, x1, y1, x2, y2, color=INK, w=W_MED, hl=1.5, hw=1.2):
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1.0
        ux, uy = dx / d, dy / d
        bx, by = x2 - ux * hl, y2 - uy * hl
        self.line(x1, y1, bx, by, color, w)
        self.poly([(x2, y2), (bx - uy * hw / 2, by + ux * hw / 2),
                   (bx + uy * hw / 2, by - ux * hw / 2)], fill=color, sw=0)

    def triad(self, x, y, ang=0.0, ax=3.2, color=INK, lw=W_MED):
        a = math.radians(ang)
        d1 = (math.cos(a), math.sin(a))
        d2 = (math.cos(a - math.pi / 2), math.sin(a - math.pi / 2))
        self.arrow(x, y, x + d1[0] * ax, y + d1[1] * ax, color, lw, 1.15, 0.95)
        self.arrow(x, y, x + d2[0] * ax, y + d2[1] * ax, color, lw, 1.15, 0.95)

    # ---- text
    def text(self, x, y, s, size, fill, weight="400", family=SANS,
             anchor="start", italic=False, block=None, li=None, cls="",
             tspans=None):
        attrs = ['x="%s"' % n(x), 'y="%s"' % n(y), 'font-size="%s"' % n(size),
                 'fill="%s"' % fill, 'font-weight="%s"' % weight]
        if anchor != "start":
            attrs.append('text-anchor="%s"' % anchor)
        if italic:
            attrs.append('font-style="italic"')
        if block:
            attrs.append('data-block="%s"' % block)
            if li is not None:
                attrs.append('data-line="%d"' % li)
        attrs.append('class="%s"' % (("txt " + cls).strip()))
        body = escape(s) if tspans is None else "".join(tspans)
        self.texts.append('<text %s>%s</text>' % (" ".join(attrs), body))
        return self

    def block(self, x, y, s, width, size, fill, weight="400", lh=None,
              family=SANS, block_id=None, anchor="start", cls=""):
        lh = lh or (LH_BODY if size >= SZ_BODY else LH_SMALL)
        lines = wrap(s, width, size, weight, family)
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, size, fill, weight=weight,
                      family=family, anchor=anchor, block=block_id, li=i, cls=cls)
        if block_id:
            self.stats.append((block_id, len(lines),
                               max(measure(l, size, weight, family) for l in lines)))
        return y + (len(lines) - 1) * lh

    def math(self, x, y, runs, size=SZ_BODY, fill=INK, block_id=None):
        """Italic variables, real sub- and superscripts via baseline shifts."""
        out, off = [], 0.0
        for kind, t in runs:
            target = 0.0
            if kind == "sup":
                target = -0.34 * size
            elif kind == "sub":
                target = 0.30 * size
            fs = SZ_SMALL if kind in ("sub", "sup") else size
            style = "italic" if kind == "i" else "normal"
            attrs = 'font-size="%s" font-style="%s"' % (n(fs), style)
            dy = target - off
            if abs(dy) > 1e-6:
                attrs += ' dy="%s"' % n(dy)
            out.append("<tspan %s>%s</tspan>" % (attrs, escape(t)))
            off = target
        attrs = ['x="%s"' % n(x), 'y="%s"' % n(y), 'font-size="%s"' % n(size),
                 'fill="%s"' % fill, 'class="txt mth"']
        if block_id:
            attrs.append('data-block="%s"' % block_id)
        self.texts.append('<text %s>%s</text>' % (" ".join(attrs), "".join(out)))

    def math_w(self, runs, size=SZ_BODY):
        w = 0.0
        for kind, t in runs:
            fs = SZ_SMALL if kind in ("sub", "sup") else size
            w += measure(t, fs, "400", MATH, ital=(kind == "i"))
        return w

    def flush_texts(self):
        self.parts.extend(self.texts)
        self.texts = []

    def svg(self):
        head = ('<svg xmlns="http://www.w3.org/2000/svg" width="420mm" '
                'height="297mm" viewBox="0 0 420 297" version="1.1">\n'
                '<title>Mobile Manipulator Learning Map</title>\n'
                '<desc>A learning map from basic Linux and Python to a '
                'two-wheeled mobile robot arm that presses a button and picks up '
                'an object: the robot and its physics, a nine-stop route with a '
                'pass gate at every stop, and how the parts fit.</desc>\n'
                '<style>text{font-family:%s} .mth{font-family:%s}</style>\n'
                % (SANS, MATH))
        return head + "\n".join(self.parts) + "\n</svg>\n"


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------
def rot_rect(cx, cy, w, h, deg):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + dx * ca - dy * sa, cy + dx * sa + dy * ca)
            for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2),
                           (w / 2, h / 2), (-w / 2, h / 2))]


def ik2(S, T, l1, l2, elbow_up=True):
    dx, dy = T[0] - S[0], T[1] - S[1]
    d = math.hypot(dx, dy)
    base = math.atan2(dy, dx)
    ca = max(-1.0, min(1.0, (d * d + l1 * l1 - l2 * l2) / (2 * d * l1)))
    a = math.acos(ca)
    ang = base - a if elbow_up else base + a
    return (S[0] + l1 * math.cos(ang), S[1] + l1 * math.sin(ang))


def taper(b, p, q, rp, rq, wp, wq, color=INK):
    """A link drawn as two side lines that die into the joint circles."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    d = math.hypot(dx, dy)
    ux, uy = dx / d, dy / d
    nx, ny = -uy, ux
    hp, hq = wp / 2, wq / 2
    sp = math.sqrt(max(rp * rp - hp * hp, 0.0))
    sq = math.sqrt(max(rq * rq - hq * hq, 0.0))
    for s in (1, -1):
        b.line(p[0] + ux * sp + nx * hp * s, p[1] + uy * sp + ny * hp * s,
               q[0] - ux * sq + nx * hq * s, q[1] - uy * sq + ny * hq * s,
               color, W_LINK)


# --------------------------------------------------------------------------
# header
# --------------------------------------------------------------------------
def build_header(b):
    b.text(M, H_TITLE_BASE, C.TITLE, SZ_TITLE, INK, weight="600", block="title")
    b.text(M, H_GOAL_BASE, C.GOAL, SZ_BODY, MUTED, block="goal")

    lines = wrap(C.HOW_TO, H_HOW_W, SZ_SMALL)
    for i, ln in enumerate(lines):
        b.text(CR, H_KEY_BASE + 4.4 + i * LH_SMALL, ln, SZ_SMALL, INK,
               anchor="end", block="howto", li=i)

    items = [(lab, PHASE_COLOR[c]) for lab, c in C.PHASE_KEY]
    items.append((C.SAFETY_KEY, SAFETY))
    widths = [H_KEY_SW + H_KEY_SWGAP + measure(lab, SZ_SMALL) for lab, _ in items]
    x = CR - (sum(widths) + H_KEY_GAP * (len(items) - 1))
    for (lab, col), w in zip(items, widths):
        b.rect(x, H_KEY_BASE - 2.15, H_KEY_SW, H_KEY_SW, color=col, sw=0, fill=col)
        b.text(x + H_KEY_SW + H_KEY_SWGAP, H_KEY_BASE, lab, SZ_SMALL, MUTED)
        x += w + H_KEY_GAP


# --------------------------------------------------------------------------
# section A — the robot
# --------------------------------------------------------------------------
def build_robot(b):
    b.line(FLOOR_X0, FLOOR, FLOOR_X1, FLOOR, INK, W_MED)
    b.line(WALL_X, FLOOR, WALL_X, WALL_TOP, INK, W_MED)
    b.line(WALL_X, WALL_TOP, WALL_X - 2.6, WALL_TOP, INK, W_MED)

    # chassis
    b.line(CH_X0, CH_TOP, CH_X1, CH_TOP, INK, W_MED, cls="chassis-top")
    b.line(CH_X0, CH_TOP, CH_X0, CH_BOT, INK, W_MED)
    b.line(CH_X1, CH_TOP, CH_X1, CH_BOT, INK, W_MED)
    # the bottom edge stops where the wheel rises into the body
    dxw = math.sqrt(max(WHEEL_R ** 2 - (CH_BOT - WHEEL_Y) ** 2, 0.0))
    b.line(CH_X0, CH_BOT, WHEEL_X - dxw, CH_BOT, INK, W_MED)
    b.line(WHEEL_X + dxw, CH_BOT, CH_X1, CH_BOT, INK, W_MED)

    # battery, low and behind the axle
    b.rect(BATTERY[0], BATTERY[1], BATTERY[2] - BATTERY[0], BATTERY[3] - BATTERY[1],
           INK, W_HAIR, cls="battery")

    # drive wheel: tyre, axle
    b.circle(WHEEL_X, WHEEL_Y, WHEEL_R, INK, W_LINK, cls="wheel")
    b.line(WHEEL_X - WHEEL_R * 0.62, WHEEL_Y, WHEEL_X + WHEEL_R * 0.62, WHEEL_Y,
           INK, W_HAIR)
    b.circle(WHEEL_X, WHEEL_Y, 0.7, INK, fill=INK, sw=0, cls="axle")

    # caster: mounting plate, fork, small wheel
    b.rect(CASTER_X - 1.8, CH_BOT, 3.6, 1.3, INK, W_MED)
    for s in (-1, 1):
        b.line(CASTER_X + s * 0.9, CH_BOT + 1.3, CASTER_X, CASTER_Y - CASTER_R + 0.6,
               INK, W_HAIR)
    b.circle(CASTER_X, CASTER_Y, CASTER_R, INK, W_MED, cls="caster")

    # camera mast and camera
    b.line(MAST_X, CH_TOP, MAST_X, MAST_TOP, INK, W_LINK, cls="mast")
    b.poly(rot_rect(CAM_C[0], CAM_C[1], CAM_W, CAM_H, CAM_ANG), sw=W_MED)
    a = math.radians(CAM_ANG)
    nose = (CAM_C[0] + (CAM_W / 2) * math.cos(a), CAM_C[1] + (CAM_W / 2) * math.sin(a))
    b.line(nose[0], nose[1], nose[0] + 1.4 * math.cos(a),
           nose[1] + 1.4 * math.sin(a), INK, W_LINK)

    # arm
    E = ik2(SHOULDER, WRIST, L1, L2, elbow_up=True)
    b.poly([(BASE_X - 4.5, BASE_Y), (BASE_X + 4.5, BASE_Y),
            (BASE_X + 3.4, BASE_Y - 2.6), (BASE_X - 3.4, BASE_Y - 2.6)], sw=W_MED)
    taper(b, SHOULDER, E, R_SHOULDER, R_ELBOW, W_UPPER, W_FORE)
    taper(b, E, WRIST, R_ELBOW, R_WRIST, W_FORE, W_WRIST)
    b.circle(SHOULDER[0], SHOULDER[1], R_SHOULDER, INK, W_MED)
    b.circle(SHOULDER[0], SHOULDER[1], R_SHOULDER * 0.38, INK, W_HAIR)
    b.circle(E[0], E[1], R_ELBOW, INK, W_MED)
    b.circle(WRIST[0], WRIST[1], R_WRIST, INK, W_MED)

    # wrist and parallel-jaw gripper
    b.line(WRIST[0] + R_WRIST * 0.7, WRIST[1], ROLL_X - R_ROLL, BUTTON_Y, INK, W_MED)
    b.circle(ROLL_X, BUTTON_Y, R_ROLL, INK, W_MED)
    b.rect(ROLL_X + R_ROLL, BUTTON_Y - 1.3, 1.8, 2.6, INK, W_MED)
    for s in (-1, 1):
        y = BUTTON_Y + s * 1.0
        b.line(ROLL_X + R_ROLL + 1.8, y, TIP_X - 0.7, y, INK, W_MED)

    # wall button
    b.rect(BUTTON_FACE, BUTTON_Y - BUTTON_H / 2, WALL_X - BUTTON_FACE, BUTTON_H,
           INK, fill=INK, sw=0)

    # object on the floor, inside reach, clear of the arm
    b.rect(OBJECT[0], OBJECT[1], OBJECT[2], FLOOR - OBJECT[1], INK, W_MED)

    # COM, its drop line, and the support bracket from axle to caster
    b.circle(COM[0], COM[1], 1.15, SAFETY, fill=SAFETY, sw=0, cls="com-dot")
    b.line(COM[0], COM[1] + 1.15, COM[0], FLOOR, SAFETY, W_HAIR, cls="com-drop")
    b.line(WHEEL_X, SUPPORT_Y, CASTER_X, SUPPORT_Y, SAFETY, W_MED, cls="support")
    b.line(WHEEL_X, SUPPORT_Y, WHEEL_X, FLOOR + 0.9, SAFETY, W_MED)
    b.line(CASTER_X, SUPPORT_Y, CASTER_X, FLOOR + 0.9, SAFETY, W_MED)
    b.text(WHEEL_X, FLOOR + 6.0, "support", SZ_SMALL, SAFETY, block="support")
    b.text(COM[0] - 1.9, COM[1] + 0.9, "COM", SZ_SMALL, SAFETY, anchor="end",
           block="com")

    # frames: W floor, B base, C camera, H hand, O object
    b.triad(24.0, FLOOR, 0.0, 3.2)
    b.text(17.8, 99.4, "W", SZ_SMALL, INK, family=MATH, italic=True, block="fW")
    b.triad(45.8, 78.6, 0.0, 2.9)
    b.text(47.4, 76.8, "B", SZ_SMALL, INK, family=MATH, italic=True, block="fB")
    b.triad(nose[0], nose[1], CAM_ANG, 3.0)
    b.text(46.4, 65.4, "C", SZ_SMALL, INK, family=MATH, italic=True, block="fC")
    b.triad(TIP_X, BUTTON_Y, 0.0, 3.0)
    b.text(TIP_X + 1.3, BUTTON_Y - 4.2, "H", SZ_SMALL, INK, family=MATH,
           italic=True, block="fH")
    b.triad(OBJECT_FRAME[0], OBJECT_FRAME[1], 0.0, 3.6)
    b.text(OBJECT_FRAME[0] + 1.2, OBJECT_FRAME[1] - 4.6, "O", SZ_SMALL, INK,
           family=MATH, italic=True, block="fO")


# --------------------------------------------------------------------------
# section A — equations and physics small multiples
# --------------------------------------------------------------------------
def build_equations(b):
    b.math(EQ_X, EQ1_BASE, C.EQ1, SZ_STOP, INK, block_id="eq1")
    y = b.block(EQ_X, EQ1_BASE + 4.8, C.EQ1_CAPTION, EQ_W, SZ_SMALL, MUTED,
                block_id="eq1c")
    b.math(EQ_X, EQ2_BASE, C.EQ2, SZ_STOP, INK, block_id="eq2")
    y = b.block(EQ_X, EQ2_BASE + 4.8, C.EQ2_CAPTION, EQ_W, SZ_SMALL, MUTED,
                block_id="eq2c")
    y = b.block(EQ_X, INSIGHT_BASE, C.KEY_INSIGHT, EQ_W, SZ_BODY, INK, weight="600",
                block_id="insight")
    y = b.block(EQ_X, y + 5.6, C.FRAME_KEY, EQ_W, SZ_SMALL, MUTED, block_id="fkey")
    y = b.block(EQ_X, y + 4.4, C.REF_NOTE, EQ_W, SZ_SMALL, MUTED, block_id="refnote")
    if y > 106:
        print("WARNING: equations column ends at %.1f" % y)


def build_physics(b):
    for i, p in enumerate(C.PHYS):
        col, row = i % 2, i // 2
        px = PANEL_X0 + col * (PANEL_W + PANEL_GAP)
        pt = PANEL_ROW_Y[row]
        b.text(px, pt + PANEL_TITLE_DY, p["title"], SZ_STOP, INK, weight="600",
               block="ph%d-t" % i)
        (dia_roll, dia_com, dia_constraints, dia_friction)[i](b, px, pt)
        if "formula2" in p:
            b.math(px, pt + FORM_DY, p["formula"], SZ_BODY, INK, block_id="ph%d-f" % i)
            x2 = px + b.math_w(p["formula"], SZ_BODY) + 6.0
            b.math(x2, pt + FORM_DY, p["formula2"], SZ_BODY, INK, block_id="ph%d-f2" % i)
        else:
            b.math(px, pt + FORM_DY, p["formula"], SZ_BODY, INK, block_id="ph%d-f" % i)
        b.block(px, pt + SENT_DY, p["sentence"], PANEL_W, SZ_SMALL, MUTED,
                block_id="ph%d-s" % i)
        if p["key"]:
            if "key_runs" in p:
                b.math(px, pt + KEY_DY, p["key_runs"], SZ_SMALL, MUTED,
                       block_id="ph%d-k" % i)
            else:
                b.text(px, pt + KEY_DY, p["key"], SZ_SMALL, MUTED, block="ph%d-k" % i)


def dia_roll(b, px, pt):
    """Top view: two wheels, an axle, the body, forward velocity, no sliding."""
    cx = px + PANEL_W / 2
    ay = pt + 10.6
    b.rect(cx - 10.0, ay - 2.2, 20.0, 4.4, INK, W_MED)
    for wx in (cx - 14.8, cx + 13.2):
        b.rect(wx, ay - 3.3, 1.6, 6.6, INK, W_MED)
    b.line(cx - 14.0, ay, cx + 14.0, ay, INK, W_HAIR)
    b.arrow(cx, ay - 2.2, cx, pt + 4.6, INK, W_MED, 1.5, 1.2)
    b.text(cx + 1.4, pt + 6.9, "v", SZ_BODY, INK, family=MATH, italic=True,
           block="ph0-v")
    b.arrow(cx + 6.0, ay + 4.0, cx - 3.6, ay + 4.0, SAFETY, W_MED, 1.7, 1.3)
    mx = cx + 1.3
    b.line(mx - 1.1, ay + 3.2, mx + 1.1, ay + 4.8, SAFETY, W_MED)


def dia_com(b, px, pt):
    """Top view: support triangle, COM inside, the margin the arm eats."""
    cx = px + PANEL_W / 2
    yb = pt + 15.0
    apex = (cx, pt + 5.9)
    left, right = (cx - 12.2, yb), (cx + 12.2, yb)
    b.poly([left, right, apex], sw=W_MED)
    com = (cx + 1.2, pt + 11.8)
    b.circle(com[0], com[1], 1.25, SAFETY, fill=SAFETY, sw=0)
    b.arrow(com[0], com[1] - 1.25, com[0], pt + 8.6, SAFETY, W_MED, 1.4, 1.1)
    b.text(com[0] - 1.9, com[1] + 0.9, "COM", SZ_SMALL, SAFETY, anchor="end",
           block="ph1-com")


def dia_constraints(b, px, pt):
    """Fingertip on a button: 3 position + 2 axis; rotation about the axis free."""
    wall = px + 64.0
    face = wall - 3.6
    y = pt + 10.2
    b.line(wall, pt + 5.0, wall, pt + 15.0, INK, W_MED)
    b.rect(face, y - 1.5, wall - face, 3.0, INK, fill=INK, sw=0)
    b.arrow(px + 47.0, y, face - 1.7, y, INK, W_MED, 1.5, 1.2)
    b.circle(face, y, 1.25, INK, fill=INK, sw=0)
    # rotation about the approach axis: an ellipse seen nearly end-on
    ex, rx, ry = px + 44.0, 1.8, 4.7
    a0, a1 = math.radians(-112.0), math.radians(-68.0)
    p0 = (ex + rx * math.cos(a0), y + ry * math.sin(a0))
    p1 = (ex + rx * math.cos(a1), y + ry * math.sin(a1))
    b.path("M %s %s A %s %s 0 1 0 %s %s" % (n(p0[0]), n(p0[1]), n(rx), n(ry),
                                           n(p1[0]), n(p1[1])), INK, W_MED)
    # arrowhead tangent to the ellipse at its end, counter-clockwise
    tx, ty = rx * math.sin(a1), -ry * math.cos(a1)
    tl = math.hypot(tx, ty)
    b.arrow(p1[0] - tx / tl * 0.01, p1[1] - ty / tl * 0.01,
            p1[0] + tx / tl * 1.8, p1[1] + ty / tl * 1.8, INK, W_MED, 1.2, 1.0)
    b.text(ex - 2.6, y + 0.9, "free", SZ_SMALL, INK, anchor="end", block="ph2-free")


def dia_friction(b, px, pt):
    cx = px + PANEL_W / 2
    top, bot = pt + 7.2, pt + 12.4
    b.rect(cx - 4.8, top, 9.6, bot - top, INK, W_MED)
    for jx in (cx - 5.5, cx + 5.5):
        b.line(jx, pt + 6.2, jx, pt + 13.4, INK, W_LINK)
    b.arrow(cx - 10.8, pt + 9.0, cx - 6.3, pt + 9.0, INK, W_MED, 1.4, 1.1)
    b.arrow(cx + 10.8, pt + 9.0, cx + 6.3, pt + 9.0, INK, W_MED, 1.4, 1.1)
    b.math(cx - 10.8, pt + 7.7, [("i", "F"), ("sub", "n")], SZ_SMALL, INK,
           block_id="ph3-fn")
    for fx in (cx - 3.7, cx + 3.7):
        b.arrow(fx, bot - 0.9, fx, top - 1.6, INK, W_MED, 1.4, 1.1)
    b.arrow(cx, bot + 0.2, cx, pt + 15.0, INK, W_MED, 1.5, 1.2)
    b.math(cx + 1.4, pt + 14.7, [("i", "m"), ("i", "g")], SZ_SMALL, INK,
           block_id="ph3-mg")


# --------------------------------------------------------------------------
# section B — the route
# --------------------------------------------------------------------------
def station_x(i):
    return COL_X0 + COL_W * (i + 0.5)


def column_x(i):
    return COL_X0 + COL_W * i + TXT_INSET


def build_route(b):
    b.text(M, B_HEAD_BASE, C.B_HEAD, SZ_HEAD, INK, weight="600", block="b-head")

    b.text(station_x(2), SAFE_LABEL_BASE, C.SAFETY_BRACKET, SZ_SMALL, SAFETY,
           block="safe-br")
    b.line(station_x(2), SAFE_BR_Y, station_x(8), SAFE_BR_Y, SAFETY, W_MED)
    for i in (2, 8):
        b.line(station_x(i), SAFE_BR_Y, station_x(i), SAFE_BR_Y + SAFE_BR_TICK,
               SAFETY, W_MED)

    # the line: one continuous segment per phase, broken only by the stations
    splits = [((station_x(1) + station_x(2)) / 2, "classical"),
              ((station_x(6) + station_x(7)) / 2, "learned"),
              ((station_x(7) + station_x(8)) / 2, "mission")]
    runs = [(M, CR, C.STOPS[0]["phase"])]
    for sx, ph in splits:
        x1, x2, _ = runs.pop()
        runs += [(x1, sx, _), (sx, x2, ph)]
    final = []
    for x1, x2, ph in runs:
        ivs = [(x1, x2)]
        for i in range(COL_N):
            g0, g1 = station_x(i) - STN_R, station_x(i) + STN_R
            nxt = []
            for s0, s1 in ivs:
                if g1 <= s0 or g0 >= s1:
                    nxt.append((s0, s1))
                else:
                    if g0 > s0:
                        nxt.append((s0, g0))
                    if g1 < s1:
                        nxt.append((g1, s1))
            ivs = nxt
        for s0, s1 in ivs:
            final.append((s0, s1, PHASE_COLOR[ph]))
    for x1, x2, col in final:
        b.line(x1, LINE_Y, x2, LINE_Y, col, W_BOLD)
    b.line(CR, LINE_Y - 4.2, CR, LINE_Y + 4.2, MISSION, W_BOLD)

    for i, s in enumerate(C.STOPS):
        cx = station_x(i)
        col = PHASE_COLOR[s["phase"]]
        b.circle(cx, LINE_Y, STN_R, col, fill=col, sw=0)
        b.line(cx, LINE_Y + STN_R, cx, TICK_END, HAIR, W_HAIR)
        b.text(cx, LINE_Y + 1.2, str(s["n"]), SZ_STOP, "#FFFFFF", weight="600",
               anchor="middle", cls="stn-num", block="stn%d" % i)

    for lab, y, col, wt in ((C.ROW_LABELS[0][0], B_TIME_BASE, MUTED, "400"),
                            (C.ROW_LABELS[1][0], LEARN_B1, MUTED, "400"),
                            (C.ROW_LABELS[2][0], BUILD_B1, MUTED, "400"),
                            (C.ROW_LABELS[3][0], PASS_B1, INK, "600")):
        b.text(ROW_LABEL_X, y, lab, SZ_SMALL, col, weight=wt, anchor="end",
               block="rl-" + lab)

    b.line(ROW_LABEL_X + 1.4, PASS_RULE_Y, CR, PASS_RULE_Y, HAIR, W_HAIR)

    for i, s in enumerate(C.STOPS):
        x = column_x(i)
        b.text(x, B_TITLE_BASE, s["title"], SZ_STOP, INK, weight="600",
               block="t%d" % i)
        b.text(x, B_TIME_BASE, s["time"], SZ_SMALL, MUTED, block="time%d" % i)
        yl = b.block(x, LEARN_B1, s["learn"], TXT_W, SZ_BODY, INK, block_id="l%d" % i)
        yb = b.block(x, BUILD_B1, s["build"], TXT_W, SZ_BODY, INK, block_id="b%d" % i)
        yp = b.block(x, PASS_B1, s["passed"], TXT_W, SZ_BODY, INK, weight="600",
                     block_id="p%d" % i)
        if max(yl, yb, yp) > NOTE_BASE - 5:
            print("WARNING: stop %d text reaches the notes" % i)

    b.text(M, NOTE_BASE, C.GPU_NOTE, SZ_SMALL, MUTED, block="gpu-note")
    b.text(CR, NOTE_BASE, C.MEASURE_NOTE, SZ_SMALL, MUTED, anchor="end",
           block="meas-note")


# --------------------------------------------------------------------------
# section C — how it fits
# --------------------------------------------------------------------------
def build_fits(b):
    b.text(M, C_HEAD_BASE, C.C_HEAD, SZ_HEAD, INK, weight="600", block="c-head")

    # --- what runs on the robot
    b.text(C_X0, PANEL_TITLE_BASE, C.LOOP_TITLE, SZ_STOP, INK, weight="600",
           block="loop-t")
    n_nodes = len(C.LOOP_NODES)
    gap = 3.9
    node_w = (C_X1 - C_X0 - gap * (n_nodes - 1)) / n_nodes
    xs = [C_X0 + k * (node_w + gap) for k in range(n_nodes)]
    y_name = LOOP_TOP + 2.8
    for k, (name, parts) in enumerate(C.LOOP_NODES):
        b.text(xs[k], y_name, name, SZ_BODY, INK, weight="600", block="loop-n%d" % k)
        b.block(xs[k], y_name + 3.7, parts, node_w, SZ_SMALL, MUTED,
                block_id="loop-p%d" % k)
        if k < n_nodes - 1:
            b.arrow(xs[k] + node_w + 0.4, y_name - 0.85,
                    xs[k + 1] - 0.4, y_name - 0.85, INK, W_HAIR, 1.1, 0.9)
    ret = LOOP_TOP + 16.6
    xr, xl = xs[-1] + node_w / 2, xs[0] + node_w / 2
    b.line(xr, LOOP_TOP + 13.0, xr, ret, INK, W_HAIR)
    b.line(xl, ret, xr, ret, INK, W_HAIR)
    b.arrow(xl, ret, xl, LOOP_TOP + 15.4, INK, W_HAIR, 1.1, 0.9)

    b.text(C_X0, P1_RATES, C.RATES, SZ_SMALL, MUTED, block="rates")
    b.line(C_X0, SAFE_RULE_Y, C_X1, SAFE_RULE_Y, SAFETY, W_MED)
    b.text(C_X0, SAFE_TEXT, C.SAFETY_BAND, SZ_BODY, SAFETY, weight="600",
           block="safe-band")

    # --- how you improve it
    b.text(C_X0, P2_TITLE, C.IMPROVE_TITLE, SZ_STOP, INK, weight="600", block="imp-t")
    x = C_X0
    last_end = x
    for k, step in enumerate(C.IMPROVE_STEPS):
        w = measure(step, SZ_SMALL)
        b.text(x, IMPROVE_BASE, step, SZ_SMALL, INK, block="imp%d" % k)
        last_end = x + w
        if k < len(C.IMPROVE_STEPS) - 1:
            ax = x + w + 0.9
            b.arrow(ax, IMPROVE_BASE - 0.85, ax + 2.4, IMPROVE_BASE - 0.85,
                    INK, W_HAIR, 1.0, 0.8)
            x = ax + 2.4 + 0.9
    b.line(last_end + 1.2, IMPROVE_BASE + 1.0, last_end + 1.2, IMPROVE_RETURN,
           INK, W_HAIR)
    b.line(last_end + 1.2, IMPROVE_RETURN, C_X0 + 0.8, IMPROVE_RETURN, INK, W_HAIR)
    b.arrow(C_X0 + 0.8, IMPROVE_RETURN, C_X0 + 0.8, IMPROVE_BASE + 1.5,
            INK, W_HAIR, 1.0, 0.8)

    # --- five ways to decide
    b.text(TBL_X0, PANEL_TITLE_BASE, C.TABLE_TITLE, SZ_STOP, INK, weight="600",
           block="tbl-t")
    for (cx0, cw), head in zip(TBL_COLS, C.TABLE_HEAD):
        b.text(cx0, TBL_HEAD_BASE, head, SZ_SMALL, MUTED, weight="600",
               block="tbl-h-" + head)
    b.line(TBL_X0, TBL_RULE_Y, TBL_X1, TBL_RULE_Y, HAIR, W_HAIR)
    y = TBL_B1
    for r, row in enumerate(C.TABLE):
        bottoms = []
        for c, ((cx0, cw), cell) in enumerate(zip(TBL_COLS, row)):
            last = b.block(cx0, y, cell, cw - 1.2, SZ_SMALL,
                           MUTED if c in (1, 2) else INK,
                           block_id="tbl%d-%d" % (r, c))
            bottoms.append(last)
        y = max(bottoms) + LH_SMALL + 2.5
        if r < len(C.TABLE) - 1:
            b.line(TBL_X0, y - 2.4, TBL_X1, y - 2.4, HAIR, W_HAIR)

    # --- after the mission
    b.text(AFT_X0, PANEL_TITLE_BASE, C.AFTER_TITLE, SZ_STOP, INK, weight="600",
           block="aft-t")
    y = AFT_B1
    for k, item in enumerate(C.AFTER):
        b.line(AFT_X0, y - 0.8, AFT_X0 + 1.7, y - 0.8, HAIR, W_MED)
        yb = b.block(AFT_X0 + 4.4, y, item, AFT_X1 - AFT_X0 - 4.4, SZ_SMALL, INK,
                     block_id="aft%d" % k)
        y = yb + LH_SMALL + 2.7


# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------
def build_footer(b):
    b.block(M, F_BASE, C.FOOT_L, F_W, SZ_SMALL, MUTED, lh=F_LH, block_id="foot-l")
    lines = wrap(C.FOOT_R, F_W, SZ_SMALL)
    for i, ln in enumerate(lines):
        b.text(CR, F_BASE + i * F_LH, ln, SZ_SMALL, MUTED, anchor="end",
               block="foot-r", li=i)


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------
def build():
    b = Builder()
    build_header(b)
    b.flush_texts()

    b.text(M, A_HEAD_BASE, C.A_HEAD, SZ_HEAD, INK, weight="600", block="a-head")
    build_robot(b)
    b.flush_texts()

    build_equations(b)
    build_physics(b)
    b.flush_texts()

    build_route(b)
    b.flush_texts()

    build_fits(b)
    b.flush_texts()

    build_footer(b)
    b.flush_texts()
    return b


HTML_SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Mobile Manipulator Learning Map</title>
<style>
  @page { size: A3 landscape; margin: 0 }
  html, body { margin: 0; padding: 0; background: #ffffff }
  svg { display: block }
</style>
</head>
<body>
%s
</body>
</html>
"""


def render_outputs():
    html = (ROOT / "mobile-manipulator-map.html").resolve()
    pdf = ROOT / "mobile-manipulator-map.pdf"
    png = ROOT / "mobile-manipulator-map.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--no-pdf-header-footer", "--virtual-time-budget=8000",
                    "--print-to-pdf=" + str(pdf), html.as_uri()],
                   capture_output=True)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--hide-scrollbars", "--force-device-scale-factor=3",
                    "--window-size=1588,1123",
                    "--screenshot=" + str(png), html.as_uri()],
                   capture_output=True)


def main():
    _load_cache()
    prev, b = None, None
    for _ in range(4):
        b = build()
        svg = b.svg()
        if svg == prev:
            break
        prev = svg
        flush_measurements()
    svg = b.svg()
    (ROOT / "mobile-manipulator-map.svg").write_text(svg, encoding="utf-8")
    (ROOT / "mobile-manipulator-map.html").write_text(HTML_SHELL % svg,
                                                     encoding="utf-8")
    if "--render" in sys.argv:
        render_outputs()
    for sid, ln, w in b.stats:
        if w > 0 and ln > 1:
            print("%-12s lines=%d widest=%.2f" % (sid, ln, w))


if __name__ == "__main__":
    main()
