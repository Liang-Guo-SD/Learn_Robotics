# -*- coding: utf-8 -*-
"""Build the Mobile Manipulator Learning Map.

    python src/build_map.py

Always writes every deliverable (SVG, HTML, PDF, PNG). Geometry is computed
from named constants; every millimetre is a margin, a grid line, or derived
from the physics drawn in section A.
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

PW, PH = 420.0, 297.0             # page, mm
M = 12.0                          # margin
CR = PW - M                       # content right edge = 408
GRID = 33.0                       # one column of the 12-column grid


def XG(k):
    """Left edge of grid column k (0..12). The last edge is CR."""
    return M + GRID * k


GUT = 3.0                         # gutter trimmed from a panel's right edge

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

SZ_TITLE, SZ_HEAD, SZ_STOP, SZ_BODY, SZ_SMALL = 11.0, 4.4, 3.6, 2.75, 2.45
LH_BODY, LH_SMALL = 3.85, 3.45

W_HAIR, W_MED, W_BOLD = 0.25, 0.5, 1.6
W_LINK = 0.8
ALLOWED_STROKES = (W_HAIR, W_MED, W_LINK, W_BOLD)

# --------------------------------------------------------------------------
# bands
# --------------------------------------------------------------------------
HEAD_TOP, HEAD_BOT = 12.0, 38.0
A_TOP, A_BOT = 40.0, 110.0
B_TOP, B_BOT = 113.0, 207.0
C_TOP, C_BOT = 211.0, 278.0
FOOT_BASE = 280.6

# --------------------------------------------------------------------------
# header
# --------------------------------------------------------------------------
H_TITLE_BASE = 24.4
H_GOAL_BASE = 32.6
H_KEY_BASE = 15.9
H_HOW_X = 286.0
H_HOW_BASE = 21.2
H_KEY_SW, H_KEY_SWGAP, H_KEY_GAP = 2.6, 1.5, 5.0

# --------------------------------------------------------------------------
# section A — the robot, side view, floor line on FLOOR
# --------------------------------------------------------------------------
A_HEAD_BASE = 45.4
FLOOR = 96.0
FLOOR_X0, FLOOR_X1 = 20.0, 137.5
CH_X0, CH_X1 = 43.0, 80.0
CH_TOP, CH_BOT = 83.5, 89.5
WHEEL_X, WHEEL_R = 64.0, 4.0
WHEEL_Y = FLOOR - WHEEL_R
CASTER_X, CASTER_R = 78.0, 1.8
CASTER_Y = FLOOR - CASTER_R
TRACK = 36.0                      # distance between the two wheel contacts
BATTERY = (43.4, 84.3, 49.4, 87.3)
MAST_X, MAST_TOP = 47.5, 75.2
CAM_C, CAM_W, CAM_H, LENS_L = (49.8, 74.0), 6.2, 3.0, 1.5
TURNTABLE = (74.0, 83.9)
TURNTABLE_RX, TURNTABLE_RY = 3.4, 1.15
SHOULDER = (74.0, 79.0)
L1, L2 = 31.0, 25.0
R_SHOULDER, R_ELBOW, R_WRIST, R_ROLL = 2.8, 2.4, 1.8, 1.0
W_UPPER, W_FORE, W_WRIST = 5.6, 4.2, 2.9
WRIST = (124.4, 72.0)
ROLL_X = 128.0
WALL_X, WALL_TOP = 137.5, 58.0
BUTTON_FACE, BUTTON_Y, BUTTON_H = 134.9, 72.0, 2.6
TIP_X = BUTTON_FACE
OBJECT = (111.0, 85.5, 8.0, 5.5)          # x, y, w, h
TABLE = (105.0, 91.0, 123.0)              # x0, top, x1
SUPPORT_Y = FLOOR + 2.4
SUPPORT_LABEL_BASE = FLOOR + 5.4

# masses (kg) used to compute the centre of mass; every position is derived
MASSES = [
    ("chassis", 0.42, (CH_X0 + CH_X1) / 2, (CH_TOP + CH_BOT) / 2),
    ("battery", 0.78, (BATTERY[0] + BATTERY[2]) / 2, (BATTERY[1] + BATTERY[3]) / 2),
    ("wheel", 0.34, WHEEL_X, WHEEL_Y),
    ("caster", 0.08, CASTER_X, CASTER_Y),
    ("camera", 0.10, CAM_C[0], CAM_C[1] + 4.0),
]

EQ_X, EQ_W = XG(4), 94.0
EQ1_BASE, EQ2_BASE = 53.0, 65.6
INSIGHT_DY, FKEY_DY, REF_DY = 12.4, 22.4, 33.9

# physics small multiples: 2 x 2 in the five columns right of the equations
PHYS_X0 = XG(7)
PHYS_GAP = 9.0
PHYS_W = (CR - PHYS_X0 - PHYS_GAP) / 2
PHYS_ROW = (46.4, 79.9)
PH_TITLE_DY = 3.4
PH_DIA_DY, PH_DIA_H = 4.2, 13.6
PH_FORM_DY, PH_KEY_DY, PH_SENT_DY = 20.4, 23.4, 26.6
SCALE_TOP = 0.75                   # top views, relative to the side view

# --------------------------------------------------------------------------
# section B — the route: nine equal columns, label gutter on the grid
# --------------------------------------------------------------------------
B_HEAD_BASE = 117.0
SAFE_LABEL_BASE = 121.6
SAFE_BR_Y, SAFE_BR_TICK = 124.8, 1.3
LINE_Y = 133.0
STN_R = 4.3
TERM_R = 5.9
TICK_END = 139.6
LABEL_X = XG(1) - 4.0             # right edge of the row labels
COL_X0 = XG(1)                    # first route column edge
COL_N = 9
COL_W = (CR - COL_X0) / COL_N
TXT_INSET = 2.1
TXT_W = COL_W - 2 * TXT_INSET
B_TITLE_BASE = 143.6
B_TIME_BASE = 148.2
LEARN_B1 = 153.4
ROW_GAP = 6.2                     # > 3 mm clear between line boxes
PASS_RULE_DY = 5.2
PASS_B1_DY = 3.4
NOTE_BASE = 199.4

# --------------------------------------------------------------------------
# section C — how it fits
# --------------------------------------------------------------------------
C_HEAD_BASE = 216.8
PANEL_TITLE_BASE = 222.6
LOOP_X0, LOOP_X1 = M, XG(4) - GUT
LOOP_INDENT = 3.4                 # gutter the return line runs in
NODE_GAP = 2.2
LOOP_NAME_Y = 227.4
LOOP_DESC_Y = 231.0
RETURN_Y = 241.4
RATES_BASE = 246.4
SAFETY_TEXT_BASE = 250.8
SAFETY_RULE_Y = 254.2
P2_TITLE_BASE = 260.6
IMPROVE_BASE = 266.2
IMPROVE_RETURN = 270.4
TBL_X0, TBL_X1 = XG(4), XG(9) - GUT
TBL_HEAD_Y = LOOP_NAME_Y
TBL_RULE_Y = 229.8
TBL_B1 = 233.4
TBL_COLS = None                 # computed from the measured copy
AFT_X0, AFT_X1 = XG(9), CR
AFT_B1 = TBL_B1
ROW_PITCH = 7.4

# --------------------------------------------------------------------------
# footer
# --------------------------------------------------------------------------
F_BASE = FOOT_BASE
F_W = 196.0
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
        self.notes = []

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

    def circle(self, cx, cy, r, color=INK, sw=W_MED, fill="none", cls="", data=""):
        c = ' class="%s"' % cls if cls else ""
        if data:
            c += " " + data
        self.parts.append(
            '<circle%s cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="%s"/>'
            % (c, n(cx), n(cy), n(r), fill, color, n(sw)))

    def ellipse(self, cx, cy, rx, ry, color=INK, sw=W_MED, fill="none", cls=""):
        c = ' class="%s"' % cls if cls else ""
        self.parts.append(
            '<ellipse%s cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" stroke="%s" '
            'stroke-width="%s"/>' % (c, n(cx), n(cy), n(rx), n(ry), fill, color, n(sw)))

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

    def head(self, x, y, ux, uy, color=INK, hl=1.5, hw=1.2, cls=""):
        bx, by = x - ux * hl, y - uy * hl
        self.poly([(x, y), (bx - uy * hw / 2, by + ux * hw / 2),
                   (bx + uy * hw / 2, by - ux * hw / 2)], fill=color, sw=0, cls=cls)

    def arrow(self, x1, y1, x2, y2, color=INK, w=W_MED, hl=1.5, hw=1.2, cls="",
              hcls=""):
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1.0
        ux, uy = dx / d, dy / d
        self.line(x1, y1, x2 - ux * hl, y2 - uy * hl, color, w, cls=cls)
        self.head(x2, y2, ux, uy, color, hl, hw, hcls)

    def triad(self, x, y, ang, ax=2.2, color=INK, lw=W_MED, cls="", acls=""):
        a = math.radians(ang)
        d1 = (math.cos(a), math.sin(a))
        d2 = (math.sin(a), -math.cos(a))
        self.arrow(x, y, x + d1[0] * ax, y + d1[1] * ax, color, lw, 1.0, 0.8,
                   cls=acls, hcls=acls)
        self.arrow(x, y, x + d2[0] * ax, y + d2[1] * ax, color, lw, 1.0, 0.8)

    # ---- text
    def text(self, x, y, s, size, fill, weight="400", family=SANS,
             anchor="start", italic=False, block=None, li=None, cls="",
             tspans=None, aria=None):
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
        if aria:
            attrs.append('aria-label="%s"' % escape(aria))
            attrs.append('role="math"')
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

    def math(self, x, y, runs, size=SZ_BODY, fill=INK, block_id=None, cls="",
             aria=None, anchor="start"):
        """Variables in the maths face, words in the sans; real sub/superscripts."""
        out, off = [], 0.0
        for kind, t in runs:
            target = 0.0
            fam = MATH
            italic = False
            fs = size
            if kind == "sup":
                target, fs = -0.34 * size, SZ_SMALL
            elif kind == "sub":
                target, fs = 0.30 * size, SZ_SMALL
            elif kind == "i":
                italic = True
            elif kind == "s":
                fam = SANS
            style = "italic" if italic else "normal"
            attrs = 'font-size="%s" font-style="%s"' % (n(fs), style)
            if kind == "s":
                attrs += ' class="san"' 
            dy = target - off
            if abs(dy) > 1e-6:
                attrs += ' dy="%s"' % n(dy)
            out.append("<tspan %s>%s</tspan>" % (attrs, escape(t)))
            off = target
        attrs = ['x="%s"' % n(x), 'y="%s"' % n(y), 'font-size="%s"' % n(size),
                 'fill="%s"' % fill, 'class="txt mth%s"' % ((" " + cls) if cls else "")]
        if anchor != "start":
            attrs.append('text-anchor="%s"' % anchor)
        if block_id:
            attrs.append('data-block="%s"' % block_id)
        if aria:
            attrs.append('aria-label="%s"' % escape(aria))
            attrs.append('role="math"')
        self.texts.append('<text %s>%s</text>' % (" ".join(attrs), "".join(out)))

    def math_w(self, runs, size=SZ_BODY):
        w = 0.0
        for kind, t in runs:
            fs = SZ_SMALL if kind in ("sub", "sup") else size
            fam = SANS if kind == "s" else MATH
            w += measure(t, fs, "400", fam, ital=(kind == "i"))
        return w

    def flush_texts(self):
        self.parts.extend(self.texts)
        self.texts = []

    def svg(self):
        head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<svg xmlns="http://www.w3.org/2000/svg" width="420mm" '
                'height="297mm" viewBox="0 0 420 297" version="1.1">\n'
                '<title>Mobile Manipulator Learning Map</title>\n'
                '<desc>A learning map from basic Linux and Python to a '
                'two-wheeled mobile robot arm that presses a button and picks up '
                'an object: the robot and its physics, a nine-stop route with a '
                'pass gate at every stop, and how the parts fit.</desc>\n'
                '<style>text{font-family:%s} .mth{font-family:%s} '
                '.san{font-family:%s}</style>\n' % (SANS, MATH, SANS))
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


def interior(a, b, c):
    """Interior angle at b, in degrees."""
    v1 = (a[0] - b[0], a[1] - b[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    d = math.hypot(*v1) * math.hypot(*v2)
    cs = (v1[0] * v2[0] + v1[1] * v2[1]) / d
    return math.degrees(math.acos(max(-1.0, min(1.0, cs))))


def taper(b, p, q, rp, rq, wp, wq, color=INK, cls=""):
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
               color, W_LINK, cls=cls)


def centroid(points, masses):
    tm = sum(m for m, _ in masses)
    return (sum(m * p[0] for m, p in masses) / tm,
            sum(m * p[1] for m, p in masses) / tm)


# --------------------------------------------------------------------------
# robot geometry, computed once
# --------------------------------------------------------------------------
OK = math.hypot(WRIST[0] - SHOULDER[0], WRIST[1] - SHOULDER[1])
ELBOW = ik2(SHOULDER, WRIST, L1, L2, elbow_up=True)
ELBOW_ANGLE = interior(SHOULDER, ELBOW, WRIST)
BUTTON_C = (BUTTON_FACE + (WALL_X - BUTTON_FACE) / 2, BUTTON_Y)
OBJECT_C = (OBJECT[0] + OBJECT[2] / 2, OBJECT[1] + OBJECT[3] / 2)
TARGET_MID = ((BUTTON_C[0] + OBJECT_C[0]) / 2, (BUTTON_C[1] + OBJECT_C[1]) / 2)
CAM_DIR = ((TARGET_MID[0] - CAM_C[0]) / math.hypot(TARGET_MID[0] - CAM_C[0],
                                                   TARGET_MID[1] - CAM_C[1]),
           (TARGET_MID[1] - CAM_C[1]) / math.hypot(TARGET_MID[0] - CAM_C[0],
                                                   TARGET_MID[1] - CAM_C[1]))
CAM_ANG = math.degrees(math.atan2(CAM_DIR[1], CAM_DIR[0]))
LENS = (CAM_C[0] + (CAM_W / 2 + LENS_L) * CAM_DIR[0],
        CAM_C[1] + (CAM_W / 2 + LENS_L) * CAM_DIR[1])
ARM_PTS = [
    (0.30, ((SHOULDER[0] + ELBOW[0]) / 2, (SHOULDER[1] + ELBOW[1]) / 2)),
    (0.22, ((ELBOW[0] + WRIST[0]) / 2, (ELBOW[1] + WRIST[1]) / 2)),
    (0.16, (ROLL_X + 2.0, BUTTON_Y)),
]
COM = centroid(None, [(m, (x, y)) for (_, m, x, y) in MASSES] + ARM_PTS)


def angle_between(a, b):
    d = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return d


def emit_notes(b):
    """Report the computed invariants; the checker re-derives them from the page."""
    ax = math.degrees(math.atan2(CAM_DIR[1], CAM_DIR[0]))
    for name, p in (("button", BUTTON_C), ("object", OBJECT_C)):
        a = angle_between(LENS, p)
        dev = abs(((a - ax + 180) % 360) - 180)
        b.notes.append("camera axis %.2f deg, %s %.2f deg -> off axis %.2f deg"
                       % (ax, name, a, dev))
        assert dev <= 30.0, "camera does not see the %s" % name
    assert 120.0 <= ELBOW_ANGLE <= 150.0, "elbow %.1f" % ELBOW_ANGLE
    assert SHOULDER[1] - ELBOW[1] <= 22.0, "elbow too high"
    assert WHEEL_X < COM[0] < CASTER_X, "COM outside the support"
    assert COM[1] < CH_TOP, "COM not above the chassis"
    assert BATTERY[2] < WHEEL_X, "battery not behind the axle"
    assert CASTER_X > WHEEL_X, "caster not on the reach side"


# --------------------------------------------------------------------------
# header
# --------------------------------------------------------------------------
def build_header(b):
    b.text(M, H_TITLE_BASE, C.TITLE, SZ_TITLE, INK, weight="600", block="title")
    b.text(M, H_GOAL_BASE, C.GOAL, SZ_BODY, MUTED, block="goal")

    lines = wrap(C.HOW_TO, CR - H_HOW_X, SZ_SMALL)
    for i, ln in enumerate(lines):
        b.text(CR, H_HOW_BASE + i * LH_SMALL, ln, SZ_SMALL, INK,
               anchor="end", block="howto", li=i)

    items = [(lab, PHASE_COLOR[c]) for lab, c in C.PHASE_KEY]
    items.append((C.SAFETY_KEY, SAFETY))
    widths = [H_KEY_SW + H_KEY_SWGAP + measure(lab, SZ_SMALL) for lab, _ in items]
    x = CR - (sum(widths) + H_KEY_GAP * (len(items) - 1))
    for (lab, col), w in zip(items, widths):
        b.rect(x, H_KEY_BASE - 2.05, H_KEY_SW, H_KEY_SW, color=col, sw=0, fill=col)
        b.text(x + H_KEY_SW + H_KEY_SWGAP, H_KEY_BASE, lab, SZ_SMALL, MUTED)
        x += w + H_KEY_GAP


# --------------------------------------------------------------------------
# section A — the robot
# --------------------------------------------------------------------------
def build_robot(b):
    b.line(FLOOR_X0, FLOOR, FLOOR_X1, FLOOR, INK, W_MED)
    b.line(WALL_X, FLOOR, WALL_X, WALL_TOP, INK, W_MED)

    # chassis with the wheel arch cut out of its bottom edge
    b.line(CH_X0, CH_TOP, CH_X1, CH_TOP, INK, W_MED, cls="chassis-top")
    b.line(CH_X0, CH_TOP, CH_X0, CH_BOT, INK, W_MED)
    b.line(CH_X1, CH_TOP, CH_X1, CH_BOT, INK, W_MED)
    dxw = math.sqrt(max(WHEEL_R ** 2 - (CH_BOT - WHEEL_Y) ** 2, 0.0))
    b.line(CH_X0, CH_BOT, WHEEL_X - dxw, CH_BOT, INK, W_MED)
    b.line(WHEEL_X + dxw, CH_BOT, CH_X1, CH_BOT, INK, W_MED)

    # battery, low and behind the axle
    b.rect(BATTERY[0], BATTERY[1], BATTERY[2] - BATTERY[0],
           BATTERY[3] - BATTERY[1], INK, W_HAIR, cls="battery")
    b.text(BATTERY[0] + 0.6, CH_BOT - 0.6, "battery", SZ_SMALL, MUTED,
           block="lbl-bat")

    # drive wheel: tyre, axle line, axle mark
    b.circle(WHEEL_X, WHEEL_Y, WHEEL_R, INK, W_LINK, cls="wheel")
    b.line(WHEEL_X - WHEEL_R, WHEEL_Y, WHEEL_X + WHEEL_R, WHEEL_Y, INK, W_HAIR)
    b.circle(WHEEL_X, WHEEL_Y, 0.7, INK, fill=INK, sw=0, cls="axle")

    # caster: plate, fork, small wheel
    b.rect(CASTER_X - 1.7, CH_BOT, 3.4, 1.2, INK, W_MED, cls="caster-plate")
    for s in (-1, 1):
        b.line(CASTER_X + s * 0.9, CH_BOT + 1.2, CASTER_X, CASTER_Y - 0.5,
               INK, W_HAIR)
    b.circle(CASTER_X, CASTER_Y, CASTER_R, INK, W_MED, cls="caster")
    b.text(CASTER_X + 3.2, CASTER_Y - 0.6, "caster", SZ_SMALL, MUTED,
           block="lbl-cast")

    # camera mast and camera body, aimed at the workspace
    b.line(MAST_X, CH_TOP, MAST_X, MAST_TOP, INK, W_LINK, cls="mast")
    b.poly(rot_rect(CAM_C[0], CAM_C[1], CAM_W, CAM_H, CAM_ANG), sw=W_MED,
           cls="cam-body")
    b.poly(rot_rect(CAM_C[0] + (CAM_W / 2 + LENS_L / 2) * CAM_DIR[0],
                    CAM_C[1] + (CAM_W / 2 + LENS_L / 2) * CAM_DIR[1],
                    LENS_L, 2.2, CAM_ANG), sw=W_MED, cls="cam-lens")
    b.poly(rot_rect(MAST_X + 0.9, MAST_TOP + 0.5, 2.4, 0.9, CAM_ANG), sw=W_MED,
           cls="cam-mount")

    # base: turntable drum on the chassis, pedestal up to the shoulder
    b.line(TURNTABLE[0] - TURNTABLE_RX, TURNTABLE[1] - 1.3,
           TURNTABLE[0] - TURNTABLE_RX, TURNTABLE[1], INK, W_MED)
    b.line(TURNTABLE[0] + TURNTABLE_RX, TURNTABLE[1] - 1.3,
           TURNTABLE[0] + TURNTABLE_RX, TURNTABLE[1], INK, W_MED)
    b.ellipse(TURNTABLE[0], TURNTABLE[1], TURNTABLE_RX, TURNTABLE_RY, INK,
              W_MED, cls="joint joint-pan")
    b.line(SHOULDER[0] - 2.7, TURNTABLE[1] - 0.2, SHOULDER[0] - 1.5,
           SHOULDER[1] + 1.4, INK, W_MED)
    b.line(SHOULDER[0] + 2.7, TURNTABLE[1] - 0.2, SHOULDER[0] + 1.5,
           SHOULDER[1] + 1.4, INK, W_MED)

    # arm
    taper(b, SHOULDER, ELBOW, R_SHOULDER, R_ELBOW, W_UPPER, W_FORE)
    taper(b, ELBOW, WRIST, R_ELBOW, R_WRIST, W_FORE, W_WRIST)
    b.circle(SHOULDER[0], SHOULDER[1], R_SHOULDER, INK, W_MED,
             cls="joint joint-shoulder")
    b.circle(ELBOW[0], ELBOW[1], R_ELBOW, INK, W_MED, cls="joint joint-elbow")
    b.circle(WRIST[0], WRIST[1], R_WRIST, INK, W_MED, cls="joint joint-wfix")

    # wrist roll and parallel-jaw gripper
    b.line(WRIST[0] + R_WRIST * 0.75, WRIST[1], ROLL_X - R_ROLL, BUTTON_Y,
           INK, W_MED)
    b.circle(ROLL_X, BUTTON_Y, R_ROLL, INK, W_MED, cls="joint joint-roll")
    b.rect(ROLL_X + R_ROLL, BUTTON_Y - 1.2, 1.5, 2.4, INK, W_MED, cls="grip")
    for s in (-1, 1):
        y = BUTTON_Y + s * 0.9
        b.line(ROLL_X + R_ROLL + 1.5, y, TIP_X, y, INK, W_MED, cls="jaw")

    # wall button
    b.rect(BUTTON_FACE, BUTTON_Y - BUTTON_H / 2, WALL_X - BUTTON_FACE, BUTTON_H,
           INK, fill=INK, sw=0, cls="button")
    b.text(WALL_X, BUTTON_Y + BUTTON_H / 2 + 4.4, "button", SZ_SMALL, MUTED,
           anchor="end", block="lbl-btn")

    # object on a low table
    b.rect(TABLE[0], TABLE[1], TABLE[2] - TABLE[0], 1.2, INK, W_MED,
           cls="table-top")
    for tx in (TABLE[0] + 1.0, TABLE[2] - 2.2):
        b.line(tx, TABLE[1] + 1.2, tx, FLOOR, INK, W_MED, cls="table-leg")
    b.rect(OBJECT[0], OBJECT[1], OBJECT[2], OBJECT[3], INK, W_MED,
           cls="object")
    b.text(OBJECT[0] + OBJECT[2] + 0.9, OBJECT[1] + OBJECT[3] - 1.1, "object",
           SZ_SMALL, MUTED, block="lbl-obj")

    # COM, drop line, support bracket
    b.circle(COM[0], COM[1], 1.0, SAFETY, fill=SAFETY, sw=0, cls="com-dot")
    b.line(COM[0], COM[1] + 1.0, COM[0], SUPPORT_Y, SAFETY, W_HAIR,
           cls="com-drop")
    b.line(WHEEL_X, SUPPORT_Y, CASTER_X, SUPPORT_Y, SAFETY, W_MED, cls="support")
    b.line(WHEEL_X, SUPPORT_Y, WHEEL_X, FLOOR + 0.9, SAFETY, W_MED, cls="support")
    b.line(CASTER_X, SUPPORT_Y, CASTER_X, FLOOR + 0.9, SAFETY, W_MED,
           cls="support")
    b.text(WHEEL_X, SUPPORT_LABEL_BASE, "support", SZ_SMALL, SAFETY,
           block="lbl-sup")
    b.text(COM[0] - 1.6, COM[1] + 0.9, "COM", SZ_SMALL, SAFETY, anchor="end",
           block="lbl-com")

    # frames: W floor, B base, C camera, H hand, O object
    b.triad(26.0, FLOOR, 0.0, 2.4)
    b.text(22.4, FLOOR - 1.6, C.LBL["world"], SZ_SMALL, INK, family=MATH,
           italic=True, block="fW")
    b.triad(44.6, CH_TOP - 1.0, 0.0, 2.2)
    b.text(41.9, CH_TOP - 2.6, C.LBL["base"], SZ_SMALL, INK, family=MATH,
           italic=True, block="fB")
    b.triad(LENS[0], LENS[1], CAM_ANG, 2.2, acls="cam-axis")
    b.text(56.6, 71.4, C.LBL["cam"], SZ_SMALL, INK, family=MATH, italic=True,
           block="fC")
    b.triad(130.6, 69.8, 0.0, 2.2)
    b.text(133.0, 67.2, C.LBL["hand"], SZ_SMALL, INK, family=MATH, italic=True,
           block="fH")
    b.triad(OBJECT_C[0], OBJECT_C[1], 0.0, 2.2)
    b.text(OBJECT_C[0] - 2.0, OBJECT[1] - 1.2, C.LBL["obj"], SZ_SMALL, INK,
           family=MATH, italic=True, block="fO")


# --------------------------------------------------------------------------
# section A — equations and physics small multiples
# --------------------------------------------------------------------------
def build_equations(b):
    b.math(EQ_X, EQ1_BASE, C.EQ1, SZ_STOP, INK, block_id="eq1", aria=C.EQ1_PLAIN)
    y = b.block(EQ_X, EQ1_BASE + 4.6, C.EQ1_CAPTION, EQ_W, SZ_SMALL, MUTED,
                block_id="eq1c")
    b.math(EQ_X, y + 8.4, C.EQ2, SZ_STOP, INK, block_id="eq2", aria=C.EQ2_PLAIN)
    y = b.block(EQ_X, y + 12.8, C.EQ2_CAPTION, EQ_W, SZ_SMALL, MUTED,
                block_id="eq2c")
    y = b.block(EQ_X, y + 9.0, C.KEY_INSIGHT, EQ_W, SZ_BODY, INK,
                weight="600", block_id="insight")
    y = b.block(EQ_X, y + 6.6, C.FRAME_KEY, EQ_W, SZ_SMALL, MUTED,
                block_id="fkey")
    y = b.block(EQ_X, y + 5.4, C.REF_NOTE, EQ_W, SZ_SMALL, MUTED,
                block_id="refnote")
    if y > A_BOT - 1.5:
        b.notes.append("WARNING: equations end at %.1f" % y)


def build_physics(b):
    for i, p in enumerate(C.PHYS):
        col, row = i % 2, i // 2
        px = PHYS_X0 + col * (PHYS_W + PHYS_GAP)
        pt = PHYS_ROW[row]
        b.text(px, pt + PH_TITLE_DY, p["title"], SZ_STOP, INK, weight="600",
               block="ph%d-t" % i)
        (dia_roll, dia_com, dia_constraints, dia_friction)[i](b, px, pt)
        if "formula2" in p:
            b.math(px, pt + PH_FORM_DY, p["formula"], SZ_BODY, INK,
                   block_id="ph%d-f" % i)
            x2 = px + b.math_w(p["formula"], SZ_BODY) + 6.0
            b.math(x2, pt + PH_FORM_DY, p["formula2"], SZ_BODY, INK,
                   block_id="ph%d-f2" % i)
        elif i == 1:
            b.block(px, pt + PH_FORM_DY, p["formula"][0][1], PHYS_W, SZ_BODY,
                    INK, block_id="ph%d-f" % i)
        else:
            b.math(px, pt + PH_FORM_DY, p["formula"], SZ_BODY, INK,
                   block_id="ph%d-f" % i)
        if "key_runs" in p:
            b.math(px, pt + PH_KEY_DY, p["key_runs"], SZ_SMALL, MUTED,
                   block_id="ph%d-k" % i)
        sent_y = pt + PH_SENT_DY
        if i == 1:
            sent_y = pt + PH_FORM_DY + LH_BODY + 3.4
        y = b.block(px, sent_y, p["sentence"], PHYS_W, SZ_SMALL, MUTED,
                    block_id="ph%d-s" % i)
        if y > pt + 33.0:
            b.notes.append("WARNING: panel %d text ends at %.1f" % (i, y))


def dia_roll(b, px, pt):
    """Top view: two wheels on an axle, forward velocity, sideways refused."""
    cx = px + PHYS_W / 2
    top = pt + PH_DIA_DY
    ay = top + 9.4
    spl = TRACK * SCALE_TOP / 2                    # half track in the drawing
    wl = WHEEL_R * 2 * SCALE_TOP                   # wheel length, top view
    ww = 2.4 * SCALE_TOP
    for s in (-1, 1):
        b.rect(cx + s * spl - ww / 2, ay - wl / 2, ww, wl, INK, W_MED,
               cls="ph-wheel")
    b.line(cx - spl, ay, cx + spl, ay, INK, W_HAIR, cls="ph-axle")
    b.arrow(cx, ay - 1.9, cx, top + 1.4, INK, W_MED, 1.4, 1.1, cls="ph-v")
    b.math(cx + 1.1, top + 4.4, [("i", "v")], SZ_BODY, INK, block_id="ph0-v")
    b.arrow(cx - 3.2, ay + 1.9, cx - 10.4, ay + 1.9, SAFETY, W_MED, 1.5, 1.2,
            cls="ph-noside")
    mx, my = cx - 6.8, ay + 1.9
    d = 2.0
    b.line(mx - d, my - d, mx + d, my + d, SAFETY, W_HAIR, cls="ph-slash")


def dia_com(b, px, pt):
    """Top view: the support triangle, the COM inside it, the margin used up."""
    cx = px + PHYS_W / 2
    top = pt + PH_DIA_DY
    ay = top + 9.4
    spl = TRACK * SCALE_TOP / 2
    wl = WHEEL_R * 2 * SCALE_TOP
    ww = 2.4 * SCALE_TOP
    apex = (cx, ay - (CASTER_X - WHEEL_X) * SCALE_TOP)
    left, right = (cx - spl, ay), (cx + spl, ay)
    b.poly([left, right, apex], sw=W_MED, cls="ph-tri")
    for s in (-1, 1):
        b.rect(cx + s * spl - ww / 2, ay - wl / 2, ww, wl, INK, W_MED,
               cls="ph-wheel")
    b.line(apex[0] - 1.3, apex[1], apex[0] + 1.3, apex[1], INK, W_MED,
           cls="ph-cast")
    com = (cx, apex[1] + (CASTER_X - COM[0]) * SCALE_TOP)
    b.arrow(com[0], com[1], apex[0], apex[1] + 0.4, SAFETY, W_MED, 1.4, 1.1,
            cls="ph-comarrow")
    b.circle(com[0], com[1], 1.0, SAFETY, fill=SAFETY, sw=0, cls="ph-comdot")
    b.text(com[0] - 1.5, com[1] + 2.3, "COM", SZ_SMALL, SAFETY, anchor="end",
           block="ph1-com")
    b.text(apex[0] - 5.6, apex[1] + 2.8, "caster", SZ_SMALL, MUTED,
           anchor="end", block="ph1-cast")


def dia_constraints(b, px, pt):
    """One fingertip on a button: contact, approach axis, and free roll."""
    top = pt + PH_DIA_DY
    y = top + 7.0
    wall = px + 50.5
    face = wall - 3.8
    b.line(wall, top + 1.4, wall, top + 12.0, INK, W_MED)
    b.rect(face, y - 1.4, wall - face, 2.8, INK, W_MED, cls="ph-button")
    # finger: a short pad with a tapered tip on the contact
    f0, f1, hh = px + 27.5, px + 40.5, 2.2
    b.poly([(f0, y - hh), (f1, y - hh), (face, y - 1.2),
            (face, y + 1.2), (f1, y + hh), (f0, y + hh)],
           sw=W_MED, cls="ph-finger")
    b.arrow(f0 - 0.4, y, face - 0.5, y, INK, W_HAIR, 1.1, 0.9, cls="ph-axis",
            hcls="ph-axis")
    b.circle(face, y, 1.1, INK, fill=INK, sw=0, cls="ph-contact")
    # free rotation about the approach axis
    ex, rx, ry = px + 31.0, 1.6, 3.6
    a0, a1 = math.radians(-118.0), math.radians(96.0)
    p0 = (ex + rx * math.cos(a0), y + ry * math.sin(a0))
    p1 = (ex + rx * math.cos(a1), y + ry * math.sin(a1))
    b.path("M %s %s A %s %s 0 1 0 %s %s" % (n(p0[0]), n(p0[1]), n(rx), n(ry),
                                            n(p1[0]), n(p1[1])), INK, W_MED,
           cls="ph-free")
    tx, ty = rx * math.sin(a1), -ry * math.cos(a1)
    tl = math.hypot(tx, ty)
    b.head(p1[0] + tx / tl * 1.5, p1[1] + ty / tl * 1.5, tx / tl, ty / tl,
           INK, 1.3, 1.0)
    b.text(ex, top + 1.9, "free", SZ_SMALL, INK, anchor="middle",
           block="ph2-free")


def dia_friction(b, px, pt):
    """Two contacts squeezing the object: 2 mu F_n has to carry mg."""
    cx = px + PHYS_W / 2
    top = pt + PH_DIA_DY
    bw, bt, bb = 3.4, top + 3.6, top + 9.0       # block half-width, top, bottom
    fw, ft = 1.4, top + 3.2                      # finger width and top
    b.rect(cx - bw, bt, 2 * bw, bb - bt, INK, W_MED, cls="ph-block")
    for s in (-1, 1):
        b.rect(cx + s * bw - (fw if s < 0 else 0), ft, fw, top + 9.3 - ft,
               INK, W_MED, cls="ph-finger")
    for s in (-1, 1):
        b.arrow(cx + s * 10.0, top + 6.6, cx + s * (bw + fw + 0.1), top + 6.6,
                INK, W_MED, 1.4, 1.1, cls="ph-fn")
        b.math(cx + s * 9.8, top + 5.2, [("i", "F"), ("sub", "n")], SZ_SMALL,
               INK, block_id="ph3-fn%d" % (s > 0), aria="F_n",
               anchor=("start" if s < 0 else "end"))
    for s in (-1, 1):
        b.arrow(cx + s * (bw - 0.5), bb - 0.3, cx + s * (bw - 0.5), bt + 1.2,
                INK, W_MED, 1.3, 1.0, cls="ph-fric")
    b.math(cx - 2.7, bt - 1.1, [("i", "μ"), ("i", "F"), ("sub", "n")],
           SZ_SMALL, INK, block_id="ph3-mufn", aria="μF_n")
    b.arrow(cx, bb + 0.3, cx, top + 12.4, INK, W_MED, 1.4, 1.1, cls="ph-mg")
    b.math(cx + 1.2, top + 12.2, [("i", "m"), ("n", " "), ("i", "g")], SZ_SMALL,
           INK, block_id="ph3-mg")


# --------------------------------------------------------------------------
# section B — the route
# --------------------------------------------------------------------------
def station_x(i):
    return COL_X0 + COL_W * (i + 0.5)


def column_x(i):
    return COL_X0 + COL_W * i + TXT_INSET


def build_route(b):
    b.text(M, B_HEAD_BASE, C.B_HEAD, SZ_HEAD, INK, weight="600", block="b-head")

    # safety gate: a slim bracket spanning stops 2 to 8
    b.text(station_x(2), SAFE_LABEL_BASE, C.SAFETY_BRACKET, SZ_SMALL, SAFETY,
           block="safe-br")
    b.line(station_x(2), SAFE_BR_Y, station_x(8), SAFE_BR_Y, SAFETY, W_MED,
           cls="safe-br")
    for i in (2, 8):
        b.line(station_x(i), SAFE_BR_Y, station_x(i), SAFE_BR_Y + SAFE_BR_TICK,
               SAFETY, W_MED, cls="safe-br")

    # one continuous segment per link; the colour of a link is its right stop's
    # phase, so every colour change sits on a station's edge
    for i in range(1, COL_N):
        col = PHASE_COLOR[C.STOPS[i]["phase"]]
        b.line(station_x(i - 1) + STN_R, LINE_Y, station_x(i) - STN_R, LINE_Y,
               col, W_BOLD, cls="route")

    for i, s in enumerate(C.STOPS):
        cx = station_x(i)
        col = PHASE_COLOR[s["phase"]]
        b.circle(cx, LINE_Y, STN_R, col, fill=col, sw=0, cls="stn-disc",
                 data='data-station="%d"' % i)
        if i == COL_N - 1:
            b.circle(cx, LINE_Y, TERM_R, MISSION, W_MED, cls="terminus")
        b.line(cx, LINE_Y + (TERM_R if i == COL_N - 1 else STN_R), cx, TICK_END,
               HAIR, W_HAIR, cls="stn-tick")
        b.text(cx, LINE_Y + 1.25, str(s["n"]), SZ_STOP, "#FFFFFF", weight="600",
               anchor="middle", cls="stn-num", block="stn%d" % i,
               aria=None)

    # rows: one baseline per row, shared by the label and every column
    learn = [wrap(s["learn"], TXT_W, SZ_BODY) for s in C.STOPS]
    build = [wrap(s["build"], TXT_W, SZ_BODY) for s in C.STOPS]
    passed = [wrap(s["passed"], TXT_W, SZ_BODY) for s in C.STOPS]
    learn_last = max(LEARN_B1 + (len(l) - 1) * LH_BODY for l in learn)
    build_b1 = learn_last + ROW_GAP
    build_last = max(build_b1 + (len(l) - 1) * LH_BODY for l in build)
    pass_rule = build_last + PASS_RULE_DY
    pass_b1 = pass_rule + PASS_B1_DY
    pass_last = max(pass_b1 + (len(l) - 1) * LH_BODY for l in passed)

    rows = ((C.ROW_LABELS[0][0], B_TIME_BASE, MUTED, "400", "time"),
            (C.ROW_LABELS[1][0], LEARN_B1, MUTED, "400", "learn"),
            (C.ROW_LABELS[2][0], build_b1, MUTED, "400", "build"),
            (C.ROW_LABELS[3][0], pass_b1, INK, "600", "pass"))
    for lab, y, col, wt, key in rows:
        b.text(LABEL_X, y, lab, SZ_SMALL, col, weight=wt, anchor="end",
               block="rl-" + key)
    b.line(LABEL_X + 2.0, pass_rule, CR, pass_rule, HAIR, W_HAIR, cls="pass-rule")

    for i, s in enumerate(C.STOPS):
        x = column_x(i)
        b.text(x, B_TITLE_BASE, s["title"], SZ_STOP, INK, weight="600",
               block="t%d" % i)
        b.text(x, B_TIME_BASE, s["time"], SZ_SMALL, MUTED, block="time%d" % i)
        yl = b.block(x, LEARN_B1, s["learn"], TXT_W, SZ_BODY, INK,
                     block_id="l%d" % i)
        yb = b.block(x, build_b1, s["build"], TXT_W, SZ_BODY, INK,
                     block_id="b%d" % i)
        yp = b.block(x, pass_b1, s["passed"], TXT_W, SZ_BODY, INK, weight="600",
                     block_id="p%d" % i)
        if max(yl, yb, yp) > NOTE_BASE - 4:
            b.notes.append("WARNING: stop %d text reaches the notes" % i)
    b.notes.append("route rows: learn %.2f build %.2f pass %.2f-%.2f"
                   % (LEARN_B1, build_b1, pass_b1, pass_last))

    b.text(M, NOTE_BASE, C.GPU_NOTE, SZ_SMALL, MUTED, block="gpu-note")
    b.text(CR, NOTE_BASE, C.MEASURE_NOTE, SZ_SMALL, MUTED, anchor="end",
           block="meas-note")


# --------------------------------------------------------------------------
# section C — how it fits
# --------------------------------------------------------------------------
def table_columns():
    """Column offsets from the measured copy: longest cell + equal gutters."""
    widths = []
    for c in range(len(C.TABLE_HEAD)):
        w = measure(C.TABLE_HEAD[c], SZ_SMALL, "600")
        for row in C.TABLE:
            w = max(w, measure(row[c], SZ_SMALL))
        widths.append(w)
    slack = (TBL_X1 - TBL_X0) - sum(widths)
    gut = slack / (len(widths) - 1)
    if gut < 4.0:
        print("WARNING: table gutters only %.1f mm" % gut)
    out, x = [], 0.0
    for i, w in enumerate(widths):
        out.append((x, w))
        x += w + gut
    return out


def build_fits(b):
    b.text(M, C_HEAD_BASE, C.C_HEAD, SZ_HEAD, INK, weight="600", block="c-head")

    # --- what runs on the robot: one closed loop
    b.text(LOOP_X0, PANEL_TITLE_BASE, C.LOOP_TITLE, SZ_STOP, INK, weight="600",
           block="loop-t")
    n_nodes = len(C.LOOP_NODES)
    x0 = LOOP_X0 + LOOP_INDENT
    node_w = (LOOP_X1 - x0 - NODE_GAP * (n_nodes - 1)) / n_nodes
    xs = [x0 + k * (node_w + NODE_GAP) for k in range(n_nodes)]
    for k, (name, parts) in enumerate(C.LOOP_NODES):
        b.text(xs[k], LOOP_NAME_Y, name, SZ_BODY, INK, weight="600",
               block="loop-n%d" % k)
        b.block(xs[k], LOOP_DESC_Y, parts, node_w, SZ_SMALL, MUTED,
                block_id="loop-p%d" % k)
        if k < n_nodes - 1:
            b.arrow(xs[k] + node_w + 0.25, LOOP_NAME_Y - 0.85,
                    xs[k + 1] - 0.25, LOOP_NAME_Y - 0.85, INK, W_MED, 1.2, 1.0,
                    cls="loop-fwd")
    # return: down from under Physics, left, and up onto the Sense label
    desc_lines = max(len(wrap(p, node_w, SZ_SMALL)) for _, p in C.LOOP_NODES)
    desc_bottom = LOOP_DESC_Y + (desc_lines - 1) * LH_SMALL
    ret_y = desc_bottom + 1.3
    xr = xs[-1] + node_w / 2
    xl = LOOP_X0 + 0.8
    b.line(xr, desc_bottom + 0.9, xr, ret_y, INK, W_MED, cls="loop-return")
    b.line(xl, ret_y, xr, ret_y, INK, W_MED, cls="loop-return")
    b.line(xl, ret_y, xl, LOOP_NAME_Y - 0.85, INK, W_MED, cls="loop-return")
    b.arrow(xl, LOOP_NAME_Y - 0.85, xs[0] - 0.35, LOOP_NAME_Y - 0.85, INK,
            W_MED, 1.2, 1.0, hcls="loop-return-head")

    rates_y, safe_y = ret_y + 5.2, ret_y + 9.7
    b.text(LOOP_X0, rates_y, C.RATES, SZ_SMALL, MUTED, block="rates")
    b.text(LOOP_X0, safe_y, C.SAFETY_BAND, SZ_BODY, SAFETY, weight="600",
           block="safe-band")
    b.line(LOOP_X0, safe_y + 3.3, LOOP_X1, safe_y + 3.3, SAFETY, W_MED,
           cls="safe-rule")

    # --- how you improve it: a cycle that returns onto its own labels
    imp_title_y = safe_y + 9.2
    b.text(LOOP_X0, imp_title_y, C.IMPROVE_TITLE, SZ_STOP, INK, weight="600",
           block="imp-t")
    step_y = imp_title_y + 5.6
    ret2 = step_y + 4.2
    widths = [measure(t, SZ_SMALL) for t in C.IMPROVE_STEPS]
    gap = (LOOP_X1 - LOOP_X0 - sum(widths)) / (len(widths) - 1)
    x = LOOP_X0
    for k, step in enumerate(C.IMPROVE_STEPS):
        b.text(x, step_y, step, SZ_SMALL, INK, block="imp%d" % k)
        x += widths[k]
        if k < len(widths) - 1:
            b.arrow(x + 1.7, step_y - 0.85, x + gap - 1.7, step_y - 0.85,
                    INK, W_HAIR, 1.0, 0.8, cls="cycle-fwd")
            x += gap
    last_end = LOOP_X1
    xr2 = last_end - 0.4
    b.line(xr2, step_y + 1.0, xr2, ret2, INK, W_HAIR, cls="cycle-return")
    b.line(LOOP_X0 + 0.6, ret2, xr2, ret2, INK, W_HAIR, cls="cycle-return")
    b.arrow(LOOP_X0 + 0.6, ret2, LOOP_X0 + 0.6, step_y + 1.4,
            INK, W_HAIR, 1.0, 0.8, hcls="cycle-return-head")

    # --- five ways to decide
    b.text(TBL_X0, PANEL_TITLE_BASE, C.TABLE_TITLE, SZ_STOP, INK,
           weight="600", block="tbl-t")
    cols = table_columns()
    for (dx, cw), head in zip(cols, C.TABLE_HEAD):
        b.text(TBL_X0 + dx, TBL_HEAD_Y, head, SZ_SMALL, MUTED, weight="600",
               block="tbl-h-" + head)
    b.line(TBL_X0, TBL_RULE_Y, TBL_X1, TBL_RULE_Y, HAIR, W_HAIR, cls="tbl-rule")
    for r, row in enumerate(C.TABLE):
        y = TBL_B1 + r * ROW_PITCH
        for c, ((dx, cw), cell) in enumerate(zip(cols, row)):
            b.text(TBL_X0 + dx, y, cell, SZ_SMALL,
                   MUTED if c in (1, 2) else INK, block="tbl%d-%d" % (r, c))
        if r < len(C.TABLE) - 1:
            b.line(TBL_X0, y + ROW_PITCH - 2.9, TBL_X1, y + ROW_PITCH - 2.9,
                   HAIR, W_HAIR, cls="tbl-rule")

    # --- after the mission: the same pitch, so the two bottoms agree
    b.text(AFT_X0, PANEL_TITLE_BASE, C.AFTER_TITLE, SZ_STOP, INK, weight="600",
           block="aft-t")
    for k, item in enumerate(C.AFTER):
        y = AFT_B1 + k * ROW_PITCH
        b.line(AFT_X0, y - 0.8, AFT_X0 + 1.7, y - 0.8, HAIR, W_HAIR,
               cls="aft-mark")
        b.text(AFT_X0 + 4.4, y, item, SZ_SMALL, INK, block="aft%d" % k)


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
    emit_notes(b)
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


def clean_tmp():
    for name in ("measure.html", "probe.html", "t.html"):
        p = TMP / name
        if p.exists():
            p.unlink()
    views = TMP / "views"
    if views.exists():
        for p in sorted(views.iterdir()):
            p.unlink()
        views.rmdir()


def main():
    _load_cache()
    prev, b = None, None
    for _ in range(5):
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
    render_outputs()
    clean_tmp()
    for sid, ln, w in b.stats:
        if w > 0 and ln > 1:
            print("%-12s lines=%d widest=%.2f" % (sid, ln, w))
    for note in b.notes:
        print("note:", note)
    print("COM %.2f,%.2f  elbow %.1f deg, %.1f above shoulder  axis %.2f deg"
          % (COM[0], COM[1], ELBOW_ANGLE, SHOULDER[1] - ELBOW[1], CAM_ANG))


if __name__ == "__main__":
    main()
