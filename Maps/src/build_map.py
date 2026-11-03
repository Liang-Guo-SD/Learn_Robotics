# -*- coding: utf-8 -*-
"""Builds the LeRobot Learning Roadmap poster: SVG, HTML, PDF, PNG.

    python src/build_map.py

One run always writes all four outputs.  Every coordinate is computed from the
named constants below.  Text is measured in headless Chrome on every run and is
never cached on disk, so a clean copy of src/ and BRIEF.md reproduces the same
bytes.  Old outputs are deleted before rendering and Chrome's exit status is
checked.
"""

import json
import math
import re
import subprocess
import sys
from pathlib import Path

import content as C

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / ".tmp"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT_SVG = ROOT / "lerobot-roadmap.svg"
OUT_HTML = ROOT / "lerobot-roadmap.html"
OUT_PDF = ROOT / "lerobot-roadmap.pdf"
OUT_PNG = ROOT / "lerobot-roadmap.png"
OUTS = (OUT_SVG, OUT_HTML, OUT_PDF, OUT_PNG)

# ---------------------------------------------------------------- page
PW, PH = 420.0, 297.0
ML, MR, MT, MB = 12.0, 408.0, 12.0, 285.0

# ---------------------------------------------------------------- type
SANS = '"Avenir Next","Helvetica Neue",Helvetica,Arial,sans-serif'
MONO = "Menlo,Consolas,monospace"
SZ_TITLE, SZ_SEC, SZ_STAGE, SZ_BODY, SZ_SMALL = 11.0, 4.4, 3.6, 2.75, 2.45
W_REG, W_DEMI = "400", "600"
LH_S, LH_B = 3.19, 3.80          # line pitch, small / body
PARA = 1.2                       # extra lead between parallel lines of a list

# ---------------------------------------------------------------- ink
INK = "#1B2430"
MUTED = "#566070"
HAIR = "#C7CDD6"
SAFETY = "#B5420A"
WHITE = "#FFFFFF"
PHASE = {"prepare": "#0B5F9E", "build": "#00695C",
         "teach": "#8A2F6B", "mission": "#1B2430"}
SW_HAIR, SW_MED, SW_DRAW, SW_METRO = 0.25, 0.5, 0.8, 1.6
CLEAR = 2.5                      # clear space between body blocks

# ---------------------------------------------------------------- header
HEAD_TITLE_B = 23.2
HEAD_R_X = 250.0

# ---------------------------------------------------------------- the one grid
COL0 = 30.0
COLW = (MR - COL0) / 6.0         # 63.0
G = [COL0 + i * COLW for i in range(6)]
ST_DX = 0.0                      # station centre and field text on the column edge
TXT_W = 58.0                     # field measure; right edge 403.0 at most
PGUT = 6.0                       # gutter between level-2 panels
PANEL_X = [ML, G[2], G[4]]       # 12, 156, 282
PANEL_W = [G[2] - PGUT - ML, G[4] - PGUT - G[2], MR - G[4]]

# ---------------------------------------------------------------- band A
A_GAP_HDR = 0.9
A_GAP_LEAD = 0.55                 # box clearance under a section heading
A_STEP_GAP = 4.6                 # gutter between pipeline steps
A_NAME_COL = 22.5                # parts: monospace name column
A_BAR_X = 38.5                   # time step: notes and bars from the panel edge
SEG_W, SEG_GAP, SEG_GROUP_GAP, BAR_H = 2.05, 0.32, 1.05, 1.55
SEGMENTS = {"state": [7, 2, 16], "action": [7, 2]}

# ---------------------------------------------------------------- band B
DISC_R = 2.55
TITLE_CLEAR = 1.2
SAFETY_ABOVE = 0.5
SAFETY_ARM = 2.2
SAFETY_GAP = 0.7
SAFETY_LABEL_DY = 1.15            # the label's own baseline below the heading
BRK_END = 3.6                    # bracket end arm, clear of the disc edge
CH = 2.4                         # 45 degree chamfer reach
CHANNEL_X = 405.6                # right margin channel centre
RET_CLEAR_MIN = 4.0              # air above and below the return line
GAP_AB = 0.95
RING_GAP, SW_RING = 0.55, 0.5    # station 10 terminus: white gap, ring weight

# ---------------------------------------------------------------- band C
C_BOT = 277.4                    # common last baseline of the band C panels
GAP_BC = 0.35
P1_NODE_DY = 9.8
NODE_R = 1.0
P1_ROLE_COL = 43.5
P2_DRAW_W = 110.0
P3_LADDER_GAP = 4.0
P3_LADDER_TO_RULES = 4.4
P3_RULE_GAP = 2.2

# ---------------------------------------------------------------- footer
FOOT_B = 282.8

# ======================================================================
# text measurement: headless Chrome, in memory, every run
# ======================================================================
_cache = {}
_pending = {}


def _sk(size, weight, family):
    return "%s|%s|%.3f" % (family, weight, size)


def measure(text, size, weight=W_REG, family=SANS):
    key = "%s|%s" % (_sk(size, weight, family), text)
    if key in _cache:
        return _cache[key]
    if key not in _pending:
        _pending[key] = (text, size, weight, family)
    return 0.52 * size * len(text)


def metrics(size, weight=W_REG, family=SANS):
    key = "M|%s" % _sk(100.0, weight, family)
    if key not in _cache:
        if key not in _pending:
            _pending[key] = ("M", 100.0, weight, family)
        return (0.97 * size, 0.326 * size)
    a, d = _cache[key]
    return (a * size, d * size)


def asc(size, weight=W_REG, family=SANS):
    return metrics(size, weight, family)[0]


def dsc(size, weight=W_REG, family=SANS):
    return metrics(size, weight, family)[1]


def _chrome_dump(path):
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--hide-scrollbars", "--virtual-time-budget=8000", "--dump-dom",
           str(path)]
    return subprocess.run(cmd, capture_output=True, text=True)


def flush_measurements():
    if not _pending:
        return
    TMP.mkdir(exist_ok=True)
    items = list(_pending.items())
    payload = []
    for (text, size, weight, family) in _pending.values():
        payload.append(["" if text == "M" else text, size * 10.0, weight,
                        family, text == "M"])
    html = """<!doctype html><meta charset="utf-8"><pre id="o">x</pre><script>
const items=%s, out=[];
const c=document.createElement('canvas').getContext('2d');
for (const [t,s,w,f,isM] of items){ c.font=w+' '+s+'px '+f;
  if (isM){ const m=c.measureText('Hxg');
    out.push([m.fontBoundingBoxAscent/s, m.fontBoundingBoxDescent/s]); }
  else { out.push(c.measureText(t).width/10); } }
document.getElementById('o').textContent=JSON.stringify({w:out});
</script>""" % json.dumps(payload)
    f = TMP / "measure.html"
    f.write_text(html, encoding="utf-8")
    r = _chrome_dump(f)
    if r.returncode:
        print("measurement probe failed (Chrome exit %d)\n%s"
              % (r.returncode, r.stderr[-800:]))
        sys.exit(2)
    m = re.search(r'<pre id="o">(.*?)</pre>', r.stdout, re.S)
    if not m:
        print("measurement probe produced no output")
        sys.exit(2)
    vals = json.loads(m.group(1).replace("&quot;", '"'))["w"]
    for (key, _), v in zip(items, vals):
        _cache[key] = v
    _pending.clear()
    f.unlink()


# ======================================================================
# rich text
# ======================================================================
NUM_RE = re.compile(r"^\d[\d,]*(?:\.\d+)?[.,;:]?$")
GLUE_WORDS = {"of", "\u00d7", "to", "%",
              "m", "cm", "mm", "s", "h"}   # units never end a line (BRIEF 7.7)
GLUE_START = ("\u2192", "\u00b7")


def _chars(s):
    """(char, family) with backticks toggling mono; arrows are always mono."""
    mono = False
    out = []
    for ch in s:
        if ch == "`":
            mono = not mono
            continue
        out.append((ch, MONO if (mono or ch == "\u2192") else SANS))
    return out


def _tokens(chars, size, weight):
    raw, cur = [], []
    for ch, fam in chars:
        if ch == " ":
            if cur:
                raw.append(cur)
                cur = []
        else:
            cur.append((ch, fam))
    if cur:
        raw.append(cur)
    toks = []
    for tkc in raw:
        code = all(fam == MONO for (_, fam) in tkc)
        runs = []
        for ch, fam in tkc:
            if runs and runs[-1][1] == fam:
                runs[-1] = (runs[-1][0] + ch, fam)
            else:
                runs.append((ch, fam))
        text = "".join(r[0] for r in runs)
        w = sum(measure(t, size, weight, fam) for (t, fam) in runs)
        glue = text.startswith(GLUE_START)
        if toks:
            prev = toks[-1]["text"]
            if NUM_RE.match(prev) or prev in GLUE_WORDS:
                glue = True
            if len(toks) > 1 and NUM_RE.match(toks[-2]["text"]) \
                    and prev in GLUE_WORDS:
                glue = True
            if code and toks[-1].get("code"):
                glue = True
        toks.append({"runs": [(t, f, None, None) for (t, f) in runs],
                     "text": text, "glue": glue, "w": w, "code": code})
    return toks


def tokenize(s, size, weight=W_REG):
    return _tokens(_chars(s), size, weight)


def tokenize_runs(runs, size, weight):
    """Tokenise an explicit run list of (text, family, weight, fill)."""
    chars = []
    for (t, fam, wt, fl) in runs:
        for ch in t:
            chars.append((ch, fam, wt or weight, fl))
    raw, cur = [], []
    for ch, fam, wt, fl in chars:
        if ch == " ":
            if cur:
                raw.append(cur)
                cur = []
        else:
            cur.append((ch, fam, wt, fl))
    if cur:
        raw.append(cur)
    toks = []
    for tkc in raw:
        trs = []
        for ch, fam, wt, fl in tkc:
            if trs and trs[-1][1] == fam and trs[-1][2] == wt and trs[-1][3] == fl:
                trs[-1] = (trs[-1][0] + ch, fam, wt, fl)
            else:
                trs.append((ch, fam, wt, fl))
        text = "".join(r[0] for r in trs)
        w = sum(measure(r[0], size, r[2], r[1]) for r in trs)
        glue = text.startswith(GLUE_START)
        if toks:
            prev = toks[-1]["text"]
            if NUM_RE.match(prev) or prev in GLUE_WORDS:
                glue = True
        toks.append({"runs": trs, "text": text, "glue": glue, "w": w})
    return toks


def space_w(size, weight):
    key = "S|%s" % _sk(size, weight, SANS)
    if key not in _cache:
        if key not in _pending:
            _pending[key] = (" ", size, weight, SANS)
        return 0.28 * size
    return _cache[key]


def _line_w(toks, i, j, sw):
    return sum(toks[k]["w"] for k in range(i, j)) + (j - i - 1) * sw


def wrap_tokens(toks, width, size, weight=W_REG):
    """Break into lines: never strand a number, never a one-word last line."""
    n = len(toks)
    if n < 2:
        return [toks]
    sw = space_w(size, weight)
    widow = 1.6 * width * width

    def exact(k):
        memo = {}

        def rec(i, left):
            if left == 1:
                w = _line_w(toks, i, n, sw)
                if w > width + 1e-9:
                    return (None, None)
                c = (width - w) ** 2
                if (n - i) == 1:
                    c += widow
                return (c, [n])
            if (i, left) in memo:
                return memo[(i, left)]
            res = (None, None)
            for j in range(i + 1, n - left + 2):
                if j < n and toks[j]["glue"]:
                    continue
                w = _line_w(toks, i, j, sw)
                if w > width + 1e-9:
                    break
                c, br = rec(j, left - 1)
                if c is None:
                    continue
                c += (width - w) ** 2
                if res[0] is None or c < res[0]:
                    res = (c, [j] + br)
            memo[(i, left)] = res
            return res

        return rec(0, k)

    best = None
    for k in range(1, n + 1):
        c, br = exact(k)
        if c is None:
            continue
        total = c + 0.35 * width * width * (k - 1)
        if best is None or total < best[0] - 1e-9:
            best = (total, br)
    if best is None:
        return [toks]
    out, s = [], 0
    for e in best[1]:
        out.append(toks[s:e])
        s = e
    return out


def line_width(line, size, weight=W_REG):
    return sum(t["w"] for t in line) + (len(line) - 1) * space_w(size, weight)


# ======================================================================
# SVG builder
# ======================================================================
def n(v):
    s = ("%.3f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


class Builder:
    def __init__(self):
        self.parts = []
        self.texts = []
        self.notes = []
        self.dry = False
        self.n_text = 0

    def line(self, x1, y1, x2, y2, color=INK, w=SW_MED, cap="butt", cls="",
             data=""):
        if self.dry:
            return
        c = (' class="%s"' % cls) if cls else ""
        if data:
            c += " " + data
        self.parts.append(
            '<line%s x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" '
            'stroke-width="%s" stroke-linecap="%s"/>'
            % (c, n(x1), n(y1), n(x2), n(y2), color, n(w), cap))

    def rect(self, x, y, w, h, color=INK, sw=SW_MED, fill="none", cls="",
             data=""):
        if self.dry:
            return
        c = (' class="%s"' % cls) if cls else ""
        if data:
            c += " " + data
        self.parts.append(
            '<rect%s x="%s" y="%s" width="%s" height="%s" fill="%s" '
            'stroke="%s" stroke-width="%s"/>'
            % (c, n(x), n(y), n(w), n(h), fill, color, n(sw)))

    def bar(self, x, y, w, h, cls="", data=""):
        if self.dry:
            return
        c = (' class="%s"' % cls) if cls else ""
        if data:
            c += " " + data
        self.parts.append('<rect%s x="%s" y="%s" width="%s" height="%s" '
                          'fill="%s" stroke="none"/>'
                          % (c, n(x), n(y), n(w), n(h), INK))

    def circle(self, cx, cy, r, color=INK, sw=SW_MED, fill="none", cls="",
               data=""):
        if self.dry:
            return
        c = (' class="%s"' % cls) if cls else ""
        if data:
            c += " " + data
        self.parts.append(
            '<circle%s cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" '
            'stroke-width="%s"/>' % (c, n(cx), n(cy), n(r), fill, color, n(sw)))

    def ellipse(self, cx, cy, rx, ry, color=INK, sw=SW_MED, fill="none",
                cls=""):
        if self.dry:
            return
        c = (' class="%s"' % cls) if cls else ""
        self.parts.append(
            '<ellipse%s cx="%s" cy="%s" rx="%s" ry="%s" fill="%s" stroke="%s" '
            'stroke-width="%s"/>' % (c, n(cx), n(cy), n(rx), n(ry), fill,
                                     color, n(sw)))

    def path(self, d, color=INK, sw=SW_MED, fill="none", cap="butt", cls="",
             data=""):
        if self.dry:
            return
        c = (' class="%s"' % cls) if cls else ""
        if data:
            c += " " + data
        self.parts.append(
            '<path%s d="%s" fill="%s" stroke="%s" stroke-width="%s" '
            'stroke-linecap="%s" stroke-linejoin="miter"/>'
            % (c, d, fill, color, n(sw), cap))

    def poly(self, pts, fill="none", stroke=INK, sw=SW_MED, cls="", data=""):
        if self.dry:
            return
        c = (' class="%s"' % cls) if cls else ""
        if data:
            c += " " + data
        p = " ".join("%s,%s" % (n(x), n(y)) for x, y in pts)
        self.parts.append('<polygon%s points="%s" fill="%s" stroke="%s" '
                          'stroke-width="%s" stroke-linejoin="miter"/>'
                          % (c, p, fill, stroke, n(sw)))

    def head(self, x, y, ux, uy, color=INK, hl=1.4, hw=1.0, cls="", data=""):
        bx, by = x - ux * hl, y - uy * hl
        self.poly([(x, y), (bx - uy * hw / 2.0, by + ux * hw / 2.0),
                   (bx + uy * hw / 2.0, by - ux * hw / 2.0)],
                  fill=color, stroke="none", sw=0, cls=cls, data=data)

    def arrow(self, x1, y1, x2, y2, color=INK, w=SW_MED, hl=1.4, hw=1.0,
              cls="", head_cls="", data=""):
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1.0
        ux, uy = dx / d, dy / d
        self.line(x1, y1, x2 - ux * hl, y2 - uy * hl, color, w, cls=cls)
        self.head(x2, y2, ux, uy, color, hl, hw, cls=head_cls, data=data)

    def darrow(self, x1, y1, x2, y2, color=INK, w=SW_MED, hl=1.4, hw=1.0,
               cls="", data=""):
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1.0
        ux, uy = dx / d, dy / d
        self.line(x1 + ux * hl, y1 + uy * hl, x2 - ux * hl, y2 - uy * hl,
                  color, w, cls=cls, data=data)
        self.head(x2, y2, ux, uy, color, hl, hw, cls=cls, data=data)
        self.head(x1, y1, -ux, -uy, color, hl, hw, cls=cls, data=data)

    def text(self, x, y, s, size, fill=INK, weight=W_REG, anchor="start",
             block=None, stage=None, field=None, li=None, runs=None, w=None,
             mono=False, data=""):
        if runs is None:
            runs = [(s, MONO if mono else SANS, weight, None)]
        else:
            runs = [(t, f, wt or weight, fl) for (t, f, wt, fl) in runs]
        if self.dry:
            return
        attrs = ['x="%s"' % n(x), 'y="%s"' % n(y),
                 'font-size="%s"' % n(size), 'fill="%s"' % fill,
                 'font-weight="%s"' % weight]
        if anchor != "start":
            attrs.append('text-anchor="%s"' % anchor)
        if block:
            attrs.append('data-block="%s"' % block)
        if stage is not None:
            attrs.append('data-stage="%d"' % stage)
        if field:
            attrs.append('data-field="%s"' % field)
        if li is not None:
            attrs.append('data-line="%d"' % li)
        if w is not None:
            attrs.append('data-w="%s"' % n(w))
        if data:
            attrs.append(data)
        attrs.append('class="txt"')
        single = (len(runs) == 1 and runs[0][1] == SANS
                  and runs[0][2] == weight and runs[0][3] is None)
        if single:
            body = esc(runs[0][0])
        else:
            body = ""
            for (t, fam, wt, fl) in runs:
                a = ""
                if fam != SANS:
                    a += ' font-family="%s"' % fam
                if wt != weight:
                    a += ' font-weight="%s"' % wt
                if fl:
                    a += ' fill="%s"' % fl
                body += "<tspan%s>%s</tspan>" % (a, esc(t))
        self.texts.append("<text %s>%s</text>" % (" ".join(attrs), body))
        self.n_text += 1

    def block(self, x, y, s, width, size, fill=INK, weight=W_REG, lh=None,
              block_id=None, stage=None, field=None, align="start", runs=None):
        lh = lh or (LH_S if size <= SZ_SMALL + 1e-6 else LH_B)
        toks = tokenize(s, size, weight) if runs is None else runs
        lines = wrap_tokens(toks, width, size, weight)
        sw = space_w(size, weight)
        for i, line in enumerate(lines):
            w = line_width(line, size, weight)
            if align == "end":
                lx = x + width - w
            elif align == "middle":
                lx = x + (width - w) / 2.0
            else:
                lx = x
            pieces = []
            for k, t in enumerate(line):
                if k:
                    pieces.append((" ", SANS, weight, None))
                for r in t["runs"]:
                    pieces.append((r[0], r[1], r[2] or weight, r[3]))
            rl = []
            for piece in pieces:
                if rl and rl[-1][1:] == piece[1:]:
                    rl[-1] = (rl[-1][0] + piece[0],) + piece[1:]
                else:
                    rl.append(piece)
            self.text(lx, y + i * lh, "", size, fill, weight=weight,
                      block=block_id, stage=stage, field=field, li=i,
                      runs=rl, w=width)
        return (y + (len(lines) - 1) * lh, len(lines))

    def flush_texts(self):
        self.parts.extend(self.texts)
        self.texts = []

    def svg(self):
        head = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="420mm" '
            'height="297mm" viewBox="0 0 420 297" version="1.1">\n'
            '<title>The LeRobot Learning Roadmap</title>\n'
            '<desc>One-page learning roadmap for students who know ROS 2 and '
            'OpenCV: how LeRobot works, eleven stages on one metro line from '
            'setting up three computers to pressing a button and picking up a '
            'cup, what each of three computers does, what one horizontal lidar '
            'plane can and cannot see, and a four-step ladder for mastering '
            'it.</desc>\n'
            '<style>text{font-family:%s; white-space:pre}</style>\n'
            % SANS)
        return head + "\n".join(self.parts) + "\n</svg>\n"


# ======================================================================
# layout helpers
# ======================================================================
def nb(prev_y, prev_size, prev_w, next_size, next_w, clear, pad=0.0,
       prev_fam=SANS, next_fam=SANS):
    return (prev_y + dsc(prev_size, prev_w, prev_fam) + clear + pad
            + asc(next_size, next_w, next_fam))


def heading(b, x, top, text, block):
    y = top + asc(SZ_SEC, W_DEMI)
    b.text(x, y, text, SZ_SEC, INK, W_DEMI, block=block)
    return y


def first_body(y_head):
    return nb(y_head, SZ_SEC, W_DEMI, SZ_BODY, W_REG, A_GAP_LEAD)


# ======================================================================
# header
# ======================================================================
def header_plan():
    tb = max(HEAD_TITLE_B, MT + asc(SZ_TITLE, W_DEMI))
    sb = nb(tb, SZ_TITLE, W_DEMI, SZ_BODY, W_REG, 0.4)
    rule = sb + dsc(SZ_BODY, W_REG) + 1.2   # BRIEF 8.8: clear of the descenders
    return tb, sb, rule


def build_header(b):
    tb, sb, rule = header_plan()
    b.text(ML, tb, C.TITLE, SZ_TITLE, INK, W_DEMI, block="title")
    b.block(ML, sb, C.SUBTITLE, 262.0, SZ_BODY, MUTED, block_id="sub")
    b.block(HEAD_R_X, 20.4, C.HOWTO, MR - HEAD_R_X, SZ_SMALL, INK,
            block_id="howto")
    y = 26.6
    x = HEAD_R_X
    for (key, name) in C.PHASES:
        b.rect(x, y - 2.35, 2.35, 2.35, color=PHASE[key], sw=0, fill=PHASE[key],
               cls="swatch")
        b.text(x + 2.9, y, name, SZ_SMALL, INK, block="phase-" + name)
        x += 2.9 + measure(name, SZ_SMALL) + 3.6
    b.rect(x, y - 2.35, 2.35, 2.35, color=SAFETY, sw=0, fill=SAFETY,
           cls="swatch")
    b.text(x + 2.9, y, C.SAFETY_KEY, SZ_SMALL, SAFETY, block="phase-safety")
    b.line(ML, rule, MR, rule, HAIR, SW_HAIR, cls="rule")
    return rule


# ======================================================================
# band A
# ======================================================================
def draw_bar(b, x, y, groups, name):
    xx, first = 0.0, True
    for gi, cnt in enumerate(groups):
        for k in range(cnt):
            if not first:
                xx += SEG_GAP + (SEG_GROUP_GAP if k == 0 else 0.0)
            b.bar(x + xx, y, SEG_W, BAR_H, cls="seg",
                  data='data-bar="%s" data-group="%d"' % (name, gi))
            xx += SEG_W
            first = False
    return xx


def a_left(b, y0, pad):
    x, w = PANEL_X[0], PANEL_W[0]
    cnt = [0]

    def gap(prev_y, prev_sz, prev_w, next_sz, next_w, clear):
        cnt[0] += 1
        return nb(prev_y, prev_sz, prev_w, next_sz, next_w, clear, pad)

    lead_last, _ = b.block(x, y0, C.A_LEAD, w, SZ_BODY, INK, block_id="a-lead")
    steps = len(C.PIPELINE)
    step_w = (w - (steps - 1) * A_STEP_GAP) / steps
    sx = [x + i * (step_w + A_STEP_GAP) for i in range(steps)]
    name_b = gap(lead_last, SZ_BODY, W_REG, SZ_BODY, W_DEMI, 0.6)
    sent_b = nb(name_b, SZ_BODY, W_DEMI, SZ_BODY, W_REG, 0.26)
    lines = 1
    for i, (nm, sent, cmd) in enumerate(C.PIPELINE):
        b.text(sx[i], name_b, nm, SZ_BODY, INK, W_DEMI, block="step-name%d" % i)
        _, k = b.block(sx[i], sent_b, sent, step_w, SZ_BODY, INK,
                       block_id="step-sent%d" % i)
        lines = max(lines, k)
    sent_last = sent_b + (lines - 1) * LH_B
    cmd_b = gap(sent_last, SZ_BODY, W_REG, SZ_SMALL, W_REG, 0.5)
    for i, (nm, sent, cmd) in enumerate(C.PIPELINE):
        b.text(sx[i], cmd_b, cmd, SZ_SMALL, INK, mono=True,
               block="step-cmd%d" % i)
        if i:
            ax0 = sx[i - 1] + measure(C.PIPELINE[i - 1][0], SZ_BODY, W_DEMI) + 1.4
            b.arrow(ax0, name_b - 0.85, sx[i] - 1.4, name_b - 0.85, INK,
                    SW_MED, 1.3, 0.95, cls="step-arrow")
    nx = [s + step_w / 2.0 for s in sx]
    lane = gap(cmd_b, SZ_SMALL, W_REG, SZ_SMALL, W_REG, 0.75)
    tip = cmd_b + dsc(SZ_SMALL, W_REG, MONO) + 0.35
    b.path("M %s %s L %s %s L %s %s L %s %s"
           % (n(nx[3]), n(cmd_b + dsc(SZ_SMALL, W_REG, MONO) + 0.3),
              n(nx[3]), n(lane), n(nx[1]), n(lane), n(nx[1]), n(tip + 1.3)),
           INK, SW_MED, cls="improve-loop")
    b.head(nx[1], tip, 0, -1, INK, 1.3, 0.95, cls="improve-head")
    lab_b = lane + 2.65
    b.text(x, lab_b, C.LOOP_LABEL, SZ_SMALL, INK, block="loop-label")
    lw = measure(C.LOOP_LABEL, SZ_SMALL)
    b.text(x + lw + 1.8, lab_b, C.LOOP_CMD, SZ_SMALL, INK, mono=True,
           block="loop-cmd")
    return (lab_b, cnt[0])


def a_middle(b, y0, pad):
    x, w = PANEL_X[1], PANEL_W[1]
    mx, mw = x + A_NAME_COL, w - A_NAME_COL
    y, n = y0, 0
    for i, (name, meaning) in enumerate(C.PARTS):
        if i:
            n += 1
            y = nb(y, SZ_BODY, W_REG, SZ_SMALL, W_REG, CLEAR, pad)
        b.text(x, y, name, SZ_SMALL, INK, mono=True, block="part-" + name)
        y, _ = b.block(mx, y, meaning, mw, SZ_BODY, INK,
                       block_id="partmean-" + name)
    return (y, n)


def a_right(b, y0, pad):
    x, w = PANEL_X[2], PANEL_W[2]
    bx, bw = x + A_BAR_X, PANEL_W[2] - A_BAR_X
    y, n = y0, 0
    for i, (feat, bar, note) in enumerate(C.TIME_ROWS):
        if i:
            n += 1
            y = nb(y, SZ_SMALL, W_REG, SZ_SMALL, W_REG, CLEAR, pad)
        b.text(x, y, feat, SZ_SMALL, INK, mono=True, block="feat-" + feat)
        b.text(bx, y, note, SZ_SMALL, INK, block="note-" + feat)
        if bar:
            draw_bar(b, bx, y + 2.2, SEGMENTS[bar], bar)
            y = y + 2.2 + BAR_H
    n += 1
    ty = nb(y, SZ_SMALL, W_REG, SZ_SMALL, W_REG, CLEAR, pad)
    last, _ = b.block(x, ty, C.TIME_NOTE, w, SZ_SMALL, MUTED,
                      block_id="time-note")
    return (last, n)


def build_band_a(b, top):
    heads = [heading(b, PANEL_X[i], top, t, blk) for i, (t, blk) in enumerate([
        (C.A_HEAD, "a-head"), (C.PARTS_HEAD, "a-parts-head"),
        (C.TIME_HEAD, "a-time-head")])]
    y0 = first_body(heads[0])
    nat = []
    for f in (a_left, a_middle, a_right):
        b.dry = True
        last, gaps = f(b, y0, 0.0)
        b.dry = False
        nat.append((last, gaps))
    target = max(l for (l, _) in nat)
    bottoms = []
    for i, f in enumerate((a_left, a_middle, a_right)):
        last, gaps = nat[i]
        pad = (target - last) / gaps if gaps else 0.0
        bot, _ = f(b, y0, pad)
        bottoms.append(bot)
    b.notes.append("band A: panel bottoms %s (heading %.2f, first body %.2f)"
                   % (", ".join("%.2f" % v for v in bottoms), heads[0], y0))
    return max(v + dsc(SZ_SMALL) for v in bottoms)


# ======================================================================
# band B: the roadmap
# ======================================================================
B_FIELDS = [("learn", W_REG, INK), ("do", W_REG, INK), ("on", W_REG, INK),
            ("pass", W_DEMI, INK), ("explain", W_REG, MUTED)]
FIELD_LABEL = {"learn": "Learn", "do": "Do", "on": "On", "pass": "Pass",
               "explain": "Explain"}
FIELD_KEY = {"learn": "learn", "do": "do", "on": "on", "pass": "passed",
             "explain": "explain"}


def stage_x(i):
    return G[i % 6] + ST_DX


def field_wrap(txt, weight):
    return wrap_tokens(tokenize(txt, SZ_SMALL, weight), TXT_W, SZ_SMALL, weight)


def row_counts(stages):
    return [max(len(field_wrap(st[FIELD_KEY[key]], wt)) for st in stages)
            for (key, wt, _) in B_FIELDS]


def row_offsets(title_b, counts):
    """Baselines of the five fields, measured from the title baseline."""
    out, y = [], title_b
    prev_sz, prev_w = SZ_STAGE, W_DEMI
    for k, cnt in enumerate(counts):
        y = nb(y, prev_sz, prev_w, SZ_SMALL, B_FIELDS[k][1], CLEAR)
        out.append(y)
        prev_sz, prev_w = SZ_SMALL, B_FIELDS[k][1]
        y += (cnt - 1) * LH_S
    return out


def title_baseline(first_field_b):
    return first_field_b - (dsc(SZ_STAGE, W_DEMI) + CLEAR + asc(SZ_SMALL, W_REG))


def band_b_head(b, top):
    """Band heading; the safety label shares its baseline; then bracket 1.

    A bracket is a slim bar just above the discs with short arms rising to the
    label, so the bar and the return lane never read as two parallel lines.
    """
    y = heading(b, ML, top, C.B_HEAD, "b-head")
    brk1 = y + SAFETY_LABEL_DY + dsc(SZ_SMALL) + SAFETY_GAP
    L1 = brk1 + SAFETY_ABOVE + DISC_R
    return y, brk1, L1


def row_h(counts):
    """Disc centre to the bottom of a row's last field."""
    offs = row_offsets(0.0, counts)
    return (DISC_R + TITLE_CLEAR + asc(SZ_STAGE, W_DEMI) + offs[-1]
            + (counts[-1] - 1) * LH_S + dsc(SZ_SMALL))


def band_b_metrics(top):
    b = Builder()
    b.dry = True
    _, _, L1 = band_b_head(b, top)
    c1 = row_counts(C.STAGES[0:6])
    c2 = row_counts(C.STAGES[6:11])
    return dict(head=L1 - top, row1=row_h(c1), row2=row_h(c2), counts=(c1, c2))


def draw_band_b(b, top, lane, L2):
    _, brk1, L1 = band_b_head(b, top)
    x = [stage_x(i) for i in range(11)]
    r1, r2 = C.STAGES[0:6], C.STAGES[6:11]
    c1, c2 = row_counts(r1), row_counts(r2)
    T1 = L1 + DISC_R + TITLE_CLEAR + asc(SZ_STAGE, W_DEMI)
    T2 = L2 + DISC_R + TITLE_CLEAR + asc(SZ_STAGE, W_DEMI)
    # ---- the route: one polyline from station 0 to station 10
    pts = [(x[i], L1) for i in range(6)]
    stops = [0, 1, 2, 3, 4, 5]
    # after station 5: right to the margin channel, down, back left through the
    # corridor, then ONE straight 45 degree descent straight into station 6's
    # disc centre.  No hook, no vertical leg, no lead-in: a Beck interchange.
    diag = L2 - lane                       # 45 degrees, so dx = dy
    pts += [(CHANNEL_X - CH, L1), (CHANNEL_X, L1 + CH),
            (CHANNEL_X, lane - CH), (CHANNEL_X - CH, lane),
            (x[6] + diag, lane), (x[6], L2)]
    for i in range(7, 11):
        stops.append(len(pts) - 1)
        pts.append((x[i], L2))
    stops.append(len(pts) - 1)
    for k in range(10):
        seg = pts[stops[k]:stops[k + 1] + 1]
        d = ["M %s %s" % (n(seg[0][0]), n(seg[0][1]))]
        d += ["L %s %s" % (n(p[0]), n(p[1])) for p in seg[1:]]
        b.path(" ".join(d), PHASE[C.STAGES[k + 1]["phase"]], SW_METRO,
               cls="metro", data='data-seg="%d"' % k)
    # ---- stations
    for i, st in enumerate(C.STAGES):
        cy = L1 if i <= 5 else L2
        col = PHASE[st["phase"]]
        if i == 10:
            b.circle(x[i], cy, DISC_R + RING_GAP + SW_RING / 2.0, col, SW_RING,
                     cls="stn-ring", data='data-station="10"')
        b.circle(x[i], cy, DISC_R, col, 0, col, cls="stn-disc",
                 data='data-station="%d"' % i)
        b.text(x[i], cy + 1.0, str(i), SZ_BODY, WHITE, W_DEMI, anchor="middle",
               block="stn-num-%d" % i, data='data-station="%d"' % i)
    # ---- safety bracket: one slim bracket above stations 2-5 only
    b.path("M %s %s L %s %s L %s %s L %s %s"
           % (n(G[2] - BRK_END), n(brk1 + SAFETY_ARM), n(G[2] - BRK_END), n(brk1),
              n(x[5] + BRK_END), n(brk1), n(x[5] + BRK_END),
              n(brk1 + SAFETY_ARM)),
           SAFETY, SW_MED, cls="safety-bracket")
    b.text(G[2], brk1 - dsc(SZ_SMALL) - SAFETY_GAP, C.SAFETY_LABEL,
           SZ_SMALL, SAFETY, block="safety-label")
    # ---- gutter labels, titles, fields
    for (row, stages, tb, counts) in ((0, r1, T1, c1), (1, r2, T2, c2)):
        offs = row_offsets(tb, counts)
        for k, (key, wt, col) in enumerate(B_FIELDS):
            b.text(ML, offs[k], FIELD_LABEL[key], SZ_SMALL,
                   INK if key == "pass" else MUTED,
                   W_DEMI if key == "pass" else W_REG,
                   block="gutter-%d-%s" % (row, key))
        for st in stages:
            cx = stage_x(st["n"])
            b.text(cx, tb, st["title"], SZ_STAGE, INK, W_DEMI,
                   block="stage-title-%d" % st["n"], stage=st["n"])
            tw = measure(st["title"], SZ_STAGE, W_DEMI)
            b.text(cx + tw + 2.2, tb, st["time"], SZ_SMALL, MUTED,
                   block="stage-time-%d" % st["n"], stage=st["n"])
            for k, (key, wt, col) in enumerate(B_FIELDS):
                b.block(cx, offs[k], st[FIELD_KEY[key]], TXT_W, SZ_SMALL, col,
                        weight=wt, block_id="s-%d-%s" % (st["n"], key),
                        stage=st["n"], field=key)
    # ---- after the mission: no station, heading on the row-2 title baseline
    b.text(stage_x(5), T2, C.AFTER_HEAD, SZ_STAGE, INK, W_DEMI,
           block="after-head")
    ay = row_offsets(T2, c2)[0]
    for i, item in enumerate(C.AFTER):
        last, _ = b.block(stage_x(5), ay, item, TXT_W, SZ_SMALL, INK,
                          block_id="after-%d" % i)
        ay = nb(last, SZ_SMALL, W_REG, SZ_SMALL, W_REG, CLEAR)
    return T2 + row_h(c2) - (DISC_R + TITLE_CLEAR + asc(SZ_STAGE, W_DEMI))


# ======================================================================
# band C
# ======================================================================
def p1(b, top, pad):
    x, w = PANEL_X[0], PANEL_W[0]
    y = heading(b, x, top, C.P1_HEAD, "p1-head")
    cnt = [1]
    ny = top + P1_NODE_DY
    nx = [x + i * P1_ROLE_COL for i in range(3)]
    for i, nm in enumerate(C.P1_NODES):
        b.circle(nx[i], ny, NODE_R, INK, SW_DRAW, cls="node",
                 data='data-node="%d" data-name="%s"'
                      % (i, C.P1_NODES[i].replace(" ", "-")))
        b.text(nx[i] + 1.9, ny + 4.0, nm, SZ_SMALL, INK, block="p1-node-%d" % i)
    # Robot Orin <-> Station Orin: a two-way link; Station Orin -> DGX Spark:
    # datasets travel one way only, so exactly one head, at the Spark
    b.darrow(nx[0] + NODE_R, ny, nx[1] - NODE_R, ny, INK, SW_MED, 1.3, 0.95,
             cls="flow-2way", data='data-link="wired"')
    b.arrow(nx[1] + NODE_R, ny, nx[2] - NODE_R, ny, INK, SW_MED, 1.3, 0.95,
            cls="flow-1way", head_cls="flow-1way", data='data-link="datasets"')
    for i in (0, 1):
        b.text((nx[i] + nx[i + 1]) / 2.0, ny - 1.1, C.P1_FLOW_LABELS[i],
               SZ_SMALL, MUTED, anchor="middle", block="p1-flow%d" % i)
    lane = ny + 10.0
    b.path("M %s %s L %s %s L %s %s L %s %s"
           % (n(nx[2]), n(ny + 1.0), n(nx[2]), n(lane), n(nx[0]), n(lane),
              n(nx[0]), n(ny + 1.0 + 1.35)),
           INK, SW_MED, cls="ret-line")
    b.head(nx[0], ny + 1.0, 0, -1, INK, 1.35, 0.95, cls="ret-head",
           data='data-head="Robot Orin"')
    b.line(nx[1], lane, nx[1], ny + 1.0 + 1.35, INK, SW_MED, cls="ret-branch")
    b.head(nx[1], ny + 1.0, 0, -1, INK, 1.35, 0.95, cls="ret-head",
           data='data-head="Station Orin"')
    b.text((nx[1] + nx[2]) / 2.0, lane - 2.0, C.P1_FLOW_LABELS[2], SZ_SMALL,
           MUTED, anchor="middle", block="p1-flow2")
    # roles under the nodes
    y = lane + dsc(SZ_SMALL) + 2.5 + pad
    cnt[0] += 1
    roww = P1_ROLE_COL - 2.5
    last = y
    for i, (name, qual, text) in enumerate(C.P1_ROLES):
        runs = [(name + ", ", SANS, W_DEMI, INK),
                (qual + ": ", SANS, W_REG, MUTED),
                (text, SANS, W_REG, None)]
        toks = tokenize_runs(runs, SZ_SMALL, W_REG)
        last, _ = b.block(x + i * P1_ROLE_COL, y, "", roww, SZ_SMALL, INK,
                          block_id="role-%d" % i, runs=toks)
    y = last
    y = nb(y, SZ_SMALL, W_REG, SZ_SMALL, W_REG, 1.2, pad)
    cnt[0] += 1
    y, _ = b.block(x, y, C.P1_WORK, w, SZ_SMALL, INK, block_id="p1-work")
    y = nb(y, SZ_SMALL, W_REG, SZ_SMALL, W_REG, 1.2, pad)
    cnt[0] += 1
    y, _ = b.block(x, y, C.P1_TIMING, w, SZ_SMALL, INK, block_id="p1-timing")
    for i, s in enumerate(C.P1_SETUP):
        y = nb(y, SZ_SMALL, W_REG, SZ_SMALL, W_REG, 0.9, pad)
        cnt[0] += 1
        y, _ = b.block(x, y, s, w, SZ_SMALL, INK, block_id="p1-setup%d" % i)
    return (y, y, cnt[0])


# ---------------------------------------------------------------- the drawing
# A side view, 110 x 32 mm, every position computed from these variables.
# v grows downward and one unit is one millimetre, so the assertions below are
# real lengths.  The robot is parked for the cup: the gripper is open 3.9 mm
# from the cup, at the cup's upper body, and touches nothing.
DRAW_V0, DRAW_V1 = 0.8, 33.0
DRAW_W = 110.0
FLOOR_V = 33.0
WALL_U, WALL_TOP = 104.0, 0.8
PANEL_U0, PANEL_U1 = 99.0, WALL_U
PANEL_V0, PANEL_V1 = 13.6, 22.4
BUTTON_U, BUTTON_V, BUTTON_R = 101.4, 16.4, 1.0
TBL_U0, TBL_U1 = 57.0, 97.0
TBL_TOP, TBL_BOT = 15.0, 16.6
LEG1_U0, LEG1_U1 = 61.9, 64.2
LEG2_U0, LEG2_U1 = 86.0, 88.4
CUP_U0, CUP_U1, CUP_TOP, CUP_BOT = 64.4, 70.4, 8.5, 15.0
CH_U0, CH_U1, CH_TOP, CH_BOT = 8.0, 44.0, 20.0, 25.5
WHEEL_U, WHEEL_R = 18.0, 5.0
CASTER_U, CASTER_R = 41.4, 1.3
PUCK_U0, PUCK_U1, PUCK_V0, PUCK_V1 = 40.6, 43.6, 18.2, CH_TOP
LIDAR_V = 19.1
SH = (34.0, 13.0)                  # shoulder joint on a 7 mm column
ARM_ELBOW_DEG = 135.0              # solved, not guessed
WRIST = (64.8, 5.6)                # J4, above the cup's near rim
ARM_L = (math.hypot(WRIST[0] - SH[0], WRIST[1] - SH[1])
         / (2.0 * math.sin(math.radians(ARM_ELBOW_DEG / 2.0))))
ARM_REACH = 2.0 * ARM_L
HOUSING_V0, HOUSING_V1 = 4.2, 6.0  # the wrist body
BAR_V0, BAR_V1 = 6.0, 7.0          # the finger carriage
JAW_GAP, JAW_W, JAW_TIP_V = 3.9, 0.7, 11.6
JAW_L_U0 = CUP_U0 - JAW_GAP - JAW_W
JAW_R_U1 = CUP_U1 + JAW_GAP + JAW_W
BAR_U0, BAR_U1 = JAW_L_U0 - 0.4, JAW_R_U1 + 0.4
CAM_BODY = (8.2, 5.8, 4.0, 1.7)     # head camera box: u0, v0, w, h
CAM_M = ((CAM_BODY[0] + CAM_BODY[0] + CAM_BODY[2]) / 2.0, CH_TOP)
CAM_LENS = (CAM_BODY[0] + CAM_BODY[2], 6.65)
HEAD_TARGET = ((CUP_U0 + CUP_U1) / 2.0, (CUP_TOP + CUP_BOT) / 2.0)
WRIST_CAM = (JAW_L_U0 + JAW_W + 0.7, BAR_V1 + 0.3, 1.5, 1.1)
WRIST_LENS = (WRIST_CAM[0] + WRIST_CAM[2], WRIST_CAM[1] + 0.6)
WRIST_SIGHT = (CUP_U0, 10.0)


def ik_elbow(S, T, l1, l2):
    dx, dy = T[0] - S[0], T[1] - S[1]
    D = math.hypot(dx, dy)
    h = math.sqrt(max(l1 * l1 - (D / 2.0) ** 2, 1e-9))
    mx, my = (S[0] + T[0]) / 2.0, (S[1] + T[1]) / 2.0
    ux, uy = dx / D, dy / D
    return (mx + uy * h, my - ux * h), D


def elbow_angle(S, E, W):
    a = (S[0] - E[0], S[1] - E[1])
    b = (W[0] - E[0], W[1] - E[1])
    c = (a[0] * b[0] + a[1] * b[1]) / (math.hypot(*a) * math.hypot(*b))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


ELBOW, ARM_D = ik_elbow(SH, WRIST, ARM_L, ARM_L)


def sight_v(a, b, u):
    return a[1] + (u - a[0]) / (b[0] - a[0]) * (b[1] - a[1])


def draw_robot(b, x0, y0, S=1.0):
    def X(u):
        return x0 + u * S

    def Y(v):
        return y0 + v * S

    def L(u1, v1, u2, v2, color=INK, w=SW_DRAW, cls=""):
        b.line(X(u1), Y(v1), X(u2), Y(v2), color, w, cls=cls)

    def R(u0, v0, u1, v1, color=INK, w=SW_DRAW, cls="", fill="none"):
        b.rect(X(u0), Y(v0), (u1 - u0) * S, (v1 - v0) * S, color, w, fill=fill,
               cls=cls)

    def Ci(u, v, r, color=INK, w=SW_DRAW, fill="none", cls="", data=""):
        b.circle(X(u), Y(v), r * S, color, w, fill, cls=cls, data=data)

    def T(u, v, key, anchor="start"):
        s = C.D_LABELS[key]
        x = u - measure(s, SZ_SMALL) if anchor == "end" else u
        b.text(X(x), Y(v), s, SZ_SMALL, INK, block="lbl-" + key)

    # ---- floor, wall, button panel, table
    L(4.0, FLOOR_V, WALL_U, FLOOR_V, cls="floor")
    L(WALL_U, WALL_TOP, WALL_U, FLOOR_V, cls="wall")
    R(PANEL_U0, PANEL_V0, PANEL_U1, PANEL_V1, cls="panel")
    Ci(BUTTON_U, BUTTON_V, BUTTON_R, INK, SW_MED, INK, cls="button")
    R(TBL_U0, TBL_TOP, TBL_U1, TBL_BOT, cls="tabletop")
    R(LEG1_U0, TBL_BOT, LEG1_U1, FLOOR_V, cls="table-leg")
    R(LEG2_U0, TBL_BOT, LEG2_U1, FLOOR_V, cls="table-leg2")
    # ---- cup: tapered body, rim ellipse, standing on the tabletop
    taper = 0.45
    b.poly([(X(CUP_U0), Y(CUP_TOP)), (X(CUP_U1), Y(CUP_TOP)),
            (X(CUP_U1 - taper), Y(CUP_BOT)), (X(CUP_U0 + taper), Y(CUP_BOT))],
           fill="none", stroke=INK, sw=SW_DRAW, cls="cup")
    b.ellipse(X((CUP_U0 + CUP_U1) / 2.0), Y(CUP_TOP),
              ((CUP_U1 - CUP_U0) / 2.0) * S, 0.62 * S, INK, SW_MED,
              cls="cup-rim")
    # ---- base: low chassis, one large rear wheel, small front caster
    R(CH_U0, CH_TOP, CH_U1, CH_BOT, cls="chassis")
    Ci(WHEEL_U, FLOOR_V - WHEEL_R, WHEEL_R, cls="wheel")
    Ci(WHEEL_U, FLOOR_V - WHEEL_R, 0.55, INK, 0, INK, cls="hub")
    L(CASTER_U, CH_BOT, CASTER_U, FLOOR_V - CASTER_R, cls="caster-strut")
    Ci(CASTER_U, FLOOR_V - CASTER_R, CASTER_R, cls="caster")
    # ---- lidar: a puck on the chassis's front top edge; the plane leaves it
    R(PUCK_U0, PUCK_V0, PUCK_U1, PUCK_V1, cls="lidar-puck")
    b.line(X(PUCK_U1), Y(LIDAR_V), X(LEG1_U0), Y(LIDAR_V), INK, SW_MED,
           cls="lidar-ray")
    Ci(LEG1_U0, LIDAR_V, 0.58, INK, 0, INK, cls="hit")
    # ---- arm: column with a shoulder housing, six joints, open gripper
    R(SH[0] - 2.4, CH_TOP - 0.9, SH[0] + 2.4, CH_TOP, INK, SW_DRAW,
      cls="arm-base")
    b.poly([(X(SH[0] - 1.9), Y(CH_TOP - 0.9)), (X(SH[0] + 1.9), Y(CH_TOP - 0.9)),
            (X(SH[0] + 0.9), Y(SH[1] + 0.3)), (X(SH[0] - 0.9), Y(SH[1] + 0.3))],
           fill="none", stroke=INK, sw=SW_DRAW, cls="arm-column")

    L(SH[0], SH[1], ELBOW[0], ELBOW[1], cls="upper-arm")
    L(ELBOW[0], ELBOW[1], WRIST[0], WRIST[1], cls="forearm")
    cu = (CUP_U0 + CUP_U1) / 2.0
    R(cu - 2.6, HOUSING_V0, cu + 2.6, HOUSING_V1, INK, SW_DRAW, cls="palm")
    R(BAR_U0, BAR_V1 - 0.7, cu - 2.6, BAR_V1, INK, SW_DRAW, cls="carriage")
    R(cu + 2.6, BAR_V1 - 0.7, BAR_U1, BAR_V1, INK, SW_DRAW, cls="carriage")
    for ju in (JAW_L_U0, JAW_R_U1 - JAW_W):
        R(ju, BAR_V1, ju + JAW_W, JAW_TIP_V, INK, SW_DRAW, cls="jaw")
    for (nm, (u, v)) in [("base", (SH[0], CH_TOP - 0.4)),
                         ("shoulder", SH), ("elbow", ELBOW),
                         ("wrist1", WRIST),
                         ("wrist2", (WRIST[0] + 2.6, WRIST[1] - 0.1)),
                         ("wrist3", (WRIST[0] + 5.2, WRIST[1] - 0.2))]:
        Ci(u, v, 0.45, INK, SW_MED, cls="joint", data='data-joint="%s"' % nm)
    # ---- head camera on its mast, axis on the cup
    L(CAM_M[0], CH_TOP, CAM_M[0], CAM_BODY[1] + CAM_BODY[3], cls="mast")
    R(CAM_BODY[0], CAM_BODY[1], CAM_BODY[0] + CAM_BODY[2],
      CAM_BODY[1] + CAM_BODY[3], cls="cam-head")
    Ci(CAM_LENS[0] - 0.3, CAM_LENS[1], 0.42, INK, SW_HAIR, INK, cls="lens")
    dx, dy = HEAD_TARGET[0] - CAM_LENS[0], HEAD_TARGET[1] - CAM_LENS[1]
    dd = math.hypot(dx, dy)
    b.arrow(X(CAM_LENS[0] + 0.15), Y(CAM_LENS[1] + 0.02),
            X(CAM_LENS[0] + dx / dd * 7.0), Y(CAM_LENS[1] + dy / dd * 7.0),
            INK, SW_MED, hl=1.0, hw=0.8, cls="cam-axis")
    # ---- wrist camera inside the gripper opening, on a short stem
    R(WRIST_CAM[0], WRIST_CAM[1], WRIST_CAM[0] + WRIST_CAM[2],
      WRIST_CAM[1] + WRIST_CAM[3], cls="cam-wrist")
    L(WRIST_CAM[0] + 0.5, BAR_V1, WRIST_CAM[0] + 0.5, WRIST_CAM[1],
      cls="wrist-bracket")
    ex, ey = WRIST_SIGHT[0] - WRIST_LENS[0], WRIST_SIGHT[1] - WRIST_LENS[1]
    ee = math.hypot(ex, ey)
    b.arrow(X(WRIST_LENS[0]), Y(WRIST_LENS[1]),
            X(WRIST_LENS[0] + ex / ee * 2.4), Y(WRIST_LENS[1] + ey / ee * 2.4),
            INK, SW_MED, hl=0.9, hw=0.7, cls="cam-wrist-axis")
    # ---- hand-placed labels
    T(CAM_BODY[0], CAM_BODY[1] - 1.2, "head")
    T(PUCK_U0 - 3.0, 16.2, "lidar")
    T(PUCK_U1 + 0.6, 16.9, "plane")
    T(CH_U1 + 1.2, 23.2, "hit")
    T(LEG1_U1 + 1.1, 22.6, "leg")
    T(JAW_R_U1 + 1.2, 10.4, "cup")
    T(PANEL_U0 - 2.6, 12.4, "button", "end")
    T(CH_U1 + 0.6, 31.6, "caster")
    T(JAW_L_U0 - 0.8, 9.4, "wrist", "end")

    # ---- the drawing is a claim about physics: refuse to render if it is false
    assert CUP_BOT <= TBL_TOP + 1e-9, "the cup does not stand on the tabletop"
    assert CUP_TOP < LIDAR_V, "the cup is not above the lidar plane"
    assert TBL_BOT < LIDAR_V, "the tabletop is not above the lidar plane"
    assert BUTTON_V + BUTTON_R < LIDAR_V, "the button is not above the plane"
    assert PANEL_V0 < LIDAR_V < PANEL_V1, "the panel does not cross the plane"
    assert LEG1_U0 < LEG1_U1 < LEG2_U0 < TBL_U1, "the legs are out of order"
    assert TBL_BOT < LIDAR_V < FLOOR_V, "the near leg does not cross the plane"
    assert PUCK_V0 < LIDAR_V < PUCK_V1, "the plane does not leave the puck"
    assert PUCK_U1 < LEG1_U0, "the ray has nothing to hit"
    assert LIDAR_V - TBL_BOT > 0.5, "the ray would hit the tabletop"
    assert LEG1_U0 - PUCK_U1 > 8.0, "the ray is too short to read"
    assert CUP_U0 > LEG1_U1 + 0.1, "the cup stands on the near leg"
    assert BAR_U0 > TBL_U0, "the gripper is not over the table's near edge"
    assert 3.0 <= JAW_GAP <= 4.6, "the gripper gap is not about 4 mm"
    assert BAR_V1 < CUP_TOP, "the carriage does not clear the cup's rim"
    assert JAW_TIP_V > CUP_TOP + 2.5, "the jaws cannot hold the cup"
    assert JAW_TIP_V < TBL_TOP - 1.0, "the jaws touch the table"
    assert 120.0 <= elbow_angle(SH, ELBOW, WRIST) <= 150.0, "elbow angle"
    assert ELBOW[1] < SH[1] < CH_TOP, "the elbow is not above the shoulder"
    assert ARM_D <= ARM_REACH + 1e-9, "the wrist is beyond the arm's reach"
    cup_near = (CUP_U0, CUP_TOP)
    cup_d = math.hypot(cup_near[0] - SH[0], cup_near[1] - SH[1])
    assert cup_d <= ARM_REACH - 1.0, \
        "the cup is not inside the arm's reach (%.2f > %.2f)" % (cup_d, ARM_REACH)
    assert CAM_LENS[1] < CUP_TOP - 0.5, "the head camera is not above the cup"
    axis = math.atan2(HEAD_TARGET[1] - CAM_LENS[1], HEAD_TARGET[0] - CAM_LENS[0])
    for corner in ((CUP_U0, CUP_TOP), (CUP_U1, CUP_TOP),
                   (CUP_U1, CUP_BOT), (CUP_U0, CUP_BOT)):
        a = math.atan2(corner[1] - CAM_LENS[1], corner[0] - CAM_LENS[0])
        assert abs(math.degrees(a - axis)) <= 30.0, \
            "the head camera misses the cup corner %s" % (corner,)
    assert WRIST_LENS[0] < CUP_U0 and WRIST_LENS[1] < WRIST_SIGHT[1]
    assert CUP_TOP < WRIST_SIGHT[1] < TBL_TOP, "the wrist camera looks off the cup"
    assert WRIST_LENS[0] > JAW_L_U0 + JAW_W, "the wrist camera sits in the jaw"
    assert WRIST_CAM[1] >= BAR_V1, "the wrist camera is inside the carriage"
    b.notes.append("drawing: elbow %.1f deg, reach %.2f mm, cup %.2f mm, "
                   "gap %.1f, ray %.2f mm, axis %.1f deg"
                   % (elbow_angle(SH, ELBOW, WRIST), ARM_REACH, cup_d, JAW_GAP,
                      LEG1_U0 - PUCK_U1, math.degrees(axis)))


def p2(b, top, pad):
    x, w = PANEL_X[1], PANEL_W[1]
    y = heading(b, x, top, C.P2_HEAD, "p2-head")
    cnt = [0]
    dy = nb(y, SZ_SEC, W_DEMI, SZ_SMALL, W_REG, 0.35)
    draw_robot(b, x + (w - DRAW_W) / 2.0, dy - DRAW_V0)
    last = dy + (DRAW_V1 - DRAW_V0)
    for i, s in enumerate(C.P2_COPY):
        last = nb(last, SZ_SMALL, W_REG, SZ_SMALL, W_REG, 0.2, pad)
        cnt[0] += 1
        last, _ = b.block(x, last, s, w, SZ_SMALL, INK,
                          block_id="p2-%d" % i)
    return (last, last, cnt[0])


def p3(b, top, pad):
    x, w = PANEL_X[2], PANEL_W[2]
    y = heading(b, x, top, C.P3_HEAD, "p3-head")
    cnt = [0]
    ny = nb(y, SZ_SEC, W_DEMI, SZ_BODY, W_DEMI, 1.2)
    cols = len(C.P3_LADDER)
    cw = (w - (cols - 1) * P3_LADDER_GAP) / cols
    ends = []
    for i, step in enumerate(C.P3_LADDER):
        cx = x + i * (cw + P3_LADDER_GAP)
        b.text(cx, ny, step, SZ_BODY, INK, W_DEMI, block="ladder-%d" % i)
        last, _ = b.block(cx, ny + 3.45, C.P3_LADDER_DEF[i], cw, SZ_SMALL,
                          MUTED, block_id="ladder-def-%d" % i)
        ends.append((cx + measure(step, SZ_BODY, W_DEMI), cx, last))
    # each arrow sits in the middle of the gap, clear of the step and the next
    for i in range(1, len(ends)):
        mid = (ends[i - 1][0] + ends[i][1]) / 2.0
        b.arrow(mid - 1.3, ny - 0.9, mid + 1.3, ny - 0.9, INK, SW_MED, 1.2, 0.9,
                cls="ladder-arrow")
    last = y = max(e[2] for e in ends) + P3_LADDER_TO_RULES + pad
    cnt[0] += 1
    for i, (lead, reason) in enumerate(C.P3_RULES):
        if i:
            y = nb(y, SZ_SMALL, W_REG, SZ_SMALL, W_REG, P3_RULE_GAP)
        b.circle(x + 0.8, y - 0.85, 0.4, INK, 0, INK, cls="bullet")
        b.text(x + 3.2, y, lead, SZ_SMALL, INK, block="rule-%d-lead" % i)
        ry = nb(y, SZ_SMALL, W_REG, SZ_SMALL, W_REG, 0.2)
        last, _ = b.block(x + 3.6, ry, reason, w - 3.6, SZ_SMALL, MUTED,
                          block_id="rule-%d-reason" % i)
        y = last
    return (last, last, cnt[0])


C_PANELS = [(p1, PANEL_X[0]), (p2, PANEL_X[1]), (p3, PANEL_X[2])]


def band_c_height():
    b = Builder()
    b.dry = True
    last = 0.0
    for f, x in C_PANELS:
        _, bot, _ = f(b, 200.0, 0.0)
        last = max(last, bot - 200.0)
    return last + dsc(SZ_SMALL)


def build_band_c(b, top):
    nat = []
    for f, x in C_PANELS:
        b.dry = True
        _, bot, gaps = f(b, top, 0.0)
        b.dry = False
        nat.append((bot, gaps))
    target = C_BOT - dsc(SZ_SMALL)
    for i, (f, x) in enumerate(C_PANELS):
        bot, gaps = nat[i]
        pad = (target - bot) / gaps if gaps else 0.0
        if pad < -1e-9:
            raise SystemExit("band C panel %d overflows by %.2f mm"
                             % (i, bot - target))
        f(b, top, max(0.0, pad))
    b.notes.append("band C natural bottoms %s, target %.2f"
                   % (", ".join("%.2f" % v for (v, _) in nat), target))
    return target


# ======================================================================
# footer
# ======================================================================
def build_footer(b):
    b.block(ML, FOOT_B, C.FOOT_LEFT, 244.0, SZ_SMALL, MUTED,
            block_id="foot-left")
    b.block(MR - 236.0, FOOT_B, C.FOOT_RIGHT, 236.0, SZ_SMALL, MUTED,
            block_id="foot-right", align="end")


# ======================================================================
# assembly
# ======================================================================
def assemble(b, strict=True):
    tb, sb, rule = header_plan()
    a_top = rule + A_GAP_HDR
    build_header(b)
    a_bot = build_band_a(b, a_top)
    b_top = a_bot + GAP_AB
    m = band_b_metrics(b_top)
    c_h = band_c_height()
    c_top = C_BOT - c_h
    b_bot = c_top - asc(SZ_SEC, W_DEMI) - GAP_BC
    corridor = b_bot - b_top - m["head"] - m["row1"] - m["row2"]
    cmin = 2 * RET_CLEAR_MIN + SW_METRO
    import os
    if os.environ.get("MAP_DEBUG"):
        print("DBG A %.2f-%.2f hdr %.2f B %.2f head %.2f row1 %.2f row2 %.2f %s %s "
              "Ch %.2f corridor %.2f (min %.2f)"
              % (a_top, a_bot, rule, b_top, m["head"], m["row1"], m["row2"],
                 m["counts"][0], m["counts"][1], c_h, corridor, cmin),
              file=sys.stderr)
    if strict and corridor < cmin - 1e-9:
        raise SystemExit("corridor %.2f mm is below the minimum %.2f mm: "
                         "tighten band A or band C" % (corridor, cmin))
    air = (corridor - SW_METRO) / 2.0
    lane = b_top + m["head"] + m["row1"] + air + SW_METRO / 2.0
    L2 = lane + SW_METRO / 2.0 + air + DISC_R
    draw_band_b(b, b_top, lane, L2)
    build_band_c(b, c_top)
    build_footer(b)
    b.notes.append("page: header %.2f-%.2f, A %.2f-%.2f, B %.2f-%.2f, "
                   "C %.2f-%.2f" % (MT, rule, a_top, a_bot, b_top, b_bot,
                                    c_top, C_BOT))
    b.notes.append("band B: head %.2f, rows %.2f/%.2f %s %s, corridor %.2f "
                   "(min %.2f), air %.2f/%.2f, lane %.2f, L1 %.2f, L2 %.2f"
                   % (m["head"], m["row1"], m["row2"], m["counts"][0],
                      m["counts"][1], corridor, cmin, air, air, lane,
                      b_top + m["head"], L2))
    b.notes.append("band C height %.2f" % c_h)
    b.flush_texts()


HTML_SHELL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>The LeRobot Learning Roadmap</title>
<style>
  @page { size: A3 landscape; margin: 0 }
  html, body { margin: 0; padding: 0; background: #FFFFFF }
  svg { display: block }
</style></head>
<body>
%s
</body></html>
"""


def clear_outputs():
    """No run may leave an old deliverable behind (BRIEF 8.13)."""
    for p in OUTS:
        if p.exists():
            p.unlink()


def render_outputs():
    html = OUT_HTML.resolve()
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                        "--no-sandbox", "--hide-scrollbars",
                        "--no-pdf-header-footer", "--virtual-time-budget=10000",
                        "--print-to-pdf=" + str(OUT_PDF), html.as_uri()],
                       capture_output=True, text=True)
    if r.returncode or not OUT_PDF.exists():
        raise SystemExit("PDF print failed (Chrome exit %d): %s"
                         % (r.returncode, r.stderr[-600:]))
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                        "--no-sandbox", "--hide-scrollbars",
                        "--force-device-scale-factor=3",
                        "--window-size=1587,1123",
                        "--screenshot=" + str(OUT_PNG), html.as_uri()],
                       capture_output=True, text=True)
    if r.returncode or not OUT_PNG.exists():
        raise SystemExit("PNG screenshot failed (Chrome exit %d): %s"
                         % (r.returncode, r.stderr[-600:]))
    raw = OUT_PDF.read_bytes()
    raw = re.sub(rb"D:\d{14}\+00'00'", b"D:20260101000000+00'00'", raw)
    OUT_PDF.write_bytes(raw)


def main():
    # a dry pass collects every measurement the layout needs, then Chrome is
    # asked once for all of them; from here the layout is exact.
    b = Builder()
    b.dry = True
    assemble(b, strict=False)
    flush_measurements()
    prev = None
    for _ in range(6):
        b = Builder()
        assemble(b)
        svg = b.svg()
        if not _pending and svg == prev:
            break
        prev = svg
        flush_measurements()
    b = Builder()
    assemble(b)
    svg = b.svg()
    clear_outputs()
    OUT_SVG.write_text(svg, encoding="utf-8")
    # the standalone SVG keeps its XML declaration; the inline copy must not
    inline = re.sub(r"^<\?xml[^>]*\?>\s*", "", svg)
    OUT_HTML.write_text(HTML_SHELL % inline, encoding="utf-8")
    render_outputs()
    for note in b.notes:
        print("note:", note)
    print("svg %.1f kB, %d text elements" % (len(svg) / 1024.0, b.n_text))


if __name__ == "__main__":
    main()
