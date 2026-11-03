# -*- coding: utf-8 -*-
"""Checks for the LeRobot Learning Roadmap.

    python src/check_map.py

Geometry is read from a live headless-Chrome render of lerobot-roadmap.html.
Copy is read from BRIEF.md section 4, never from content.py.  Exits non-zero if
any check fails.

Checks 1-16 are BRIEF section 6; 17-21 implement the extra checks required by
BRIEF section 7 (numbers with units, clean build, trained-policies return,
band C panel bottoms, band A body size).
"""

import hashlib
import json
import math
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_map as B  # grid constants only

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
TMP = ROOT / ".tmp"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BRIEF = ROOT / "BRIEF.md"
HTML = ROOT / "lerobot-roadmap.html"
SVG = ROOT / "lerobot-roadmap.svg"
PDF = ROOT / "lerobot-roadmap.pdf"
PNG = ROOT / "lerobot-roadmap.png"

INK = "#1B2430"
MUTED = "#566070"
HAIR = "#C7CDD6"
SAFETY = "#B5420A"
PHASE_COL = {"prepare": "#0B5F9E", "build": "#00695C", "teach": "#8A2F6B",
             "mission": "#1B2430"}
PALETTE = {INK, MUTED, HAIR, SAFETY} | set(PHASE_COL.values())
TEXT_COLORS = {INK, MUTED, SAFETY} | set(PHASE_COL.values())
WEIGHTS = {0.25, 0.5, 0.8, 1.6}
NUM_END = re.compile(r"(?:^|\s)\d[\d,]*(?:\.\d+)?[.,;:]?$")

FAILS = []


def fail(check, msg):
    FAILS.append("[check %s] %s" % (check, msg))


def ok(check, msg):
    print("  ok   %-2s %s" % (check, msg))


# ---------------------------------------------------------------- copy
def sec4():
    txt = BRIEF.read_text(encoding="utf-8")
    return txt[txt.index("## 4. Final copy"):txt.index("## 5. Science")]


def strip_ticks(s):
    return s.replace("`", "")


def norm(s):
    return re.sub(r"\s+", " ", strip_ticks(s)).strip()


def brief_copy():
    """Every piece of section 4 copy the page must carry."""
    sec = sec4()
    backticked = [m.group(1).strip() for m in re.finditer(r"`([^`]+)`", sec)]
    stages = {}
    for m in re.finditer(r"^Stage (\d+)\n((?:- [A-Za-z]+: .*\n?)+)", sec, re.M):
        n = int(m.group(1))
        fields = [(fm.group(1).lower(), fm.group(2).strip())
                  for fm in re.finditer(r"^- ([A-Za-z]+): `([^`]+)`",
                                        m.group(2), re.M)]
        stages[n] = fields
    stage_table = []
    for m in re.finditer(r"^\| (\d+) \| (\w+) \| ([^|]+?) \| ([^|]+?) \|$",
                         sec, re.M):
        stage_table.append((int(m.group(1)), m.group(2), m.group(3).strip(),
                            m.group(4).strip()))

    def table_after(header):
        i = sec.index(header)
        rows = []
        for line in sec[i:].splitlines()[2:]:
            if not line.startswith("|"):
                break
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
        return rows

    pipeline = table_after("| Step | Sentence | Command (monospace) |")
    parts = table_after("| Part (monospace) | Meaning |")
    steps = table_after("| Feature (monospace) | Bar and note |")
    return dict(backticked=backticked, stages=stages, stage_table=stage_table,
                pipeline=pipeline, parts=parts, steps=steps)


# ---------------------------------------------------------------- probe
PROBE = r"""
<script>
window.addEventListener('load', function(){
  const svg = document.querySelector('svg');
  const r0 = svg.getBoundingClientRect();
  const K = 420 / r0.width;
  const hex = (c) => {
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return (c || '').toUpperCase();
    const p = m[1].split(',').map(x => parseFloat(x));
    return '#' + p.slice(0,3).map(v => Math.round(v).toString(16).padStart(2,'0')).join('').toUpperCase();
  };
  const texts = [...svg.querySelectorAll('text')];
  const ti = texts.map((t,i) => {
    const r = t.getBoundingClientRect(); const cs = getComputedStyle(t);
    return {i:i, x:(r.left-r0.left)*K, y:(r.top-r0.top)*K,
            w:r.width*K, h:r.height*K, fs:parseFloat(cs.fontSize),
            ax:parseFloat(t.getAttribute('x')), ay:parseFloat(t.getAttribute('y')),
            fill:hex(cs.fill), fam:cs.fontFamily,
            weight:cs.fontWeight,
            block:t.getAttribute('data-block')||'',
            stage:t.getAttribute('data-stage'), field:t.getAttribute('data-field')||'',
            line:t.getAttribute('data-line'), measure:t.getAttribute('data-w'),
            tailW:(function(){const txt=t.textContent; let i=txt.length-1;
              while(i>=0 && txt[i]!==' ') i--;
              if(i<0) return 0;
              try{return t.getSubStringLength(i, txt.length-i)*K;}catch(e){return 0;}})(),
            stn:t.getAttribute('data-station'),
            text:t.textContent};
  });
  const overlaps=[];
  for(let a=0;a<ti.length;a++) for(let b=a+1;b<ti.length;b++){
    const A=ti[a],Bb=ti[b];
    const ox=Math.min(A.x+A.w,Bb.x+Bb.w)-Math.max(A.x,Bb.x);
    const oy=Math.min(A.y+A.h,Bb.y+Bb.h)-Math.max(A.y,Bb.y);
    if(ox>0.001&&oy>0.001) overlaps.push([a,b,+ox.toFixed(3),+oy.toFixed(3)]);
  }
  const oob=[];
  ti.forEach(t=>{ if(t.x<12-0.02||t.y<12-0.02||t.x+t.w>408+0.02||t.y+t.h>285+0.02)
     oob.push([t.i,+t.x.toFixed(2),+t.y.toFixed(2),+(t.x+t.w).toFixed(2),+(t.y+t.h).toFixed(2)]); });
  const occl=[];
  texts.forEach((t,i)=>{
    const n=t.getNumberOfChars?t.getNumberOfChars():0; if(!n) return;
    const ctm=t.getScreenCTM();
    for(let k=0;k<n;k++){
      if(/^\s*$/.test(t.textContent[k]||'')) continue;
      let e; try{e=t.getExtentOfChar(k);}catch(err){continue;}
      if(!e||e.width===0) continue;
      const p=svg.createSVGPoint(); p.x=e.x+e.width/2; p.y=e.y+e.height/2;
      const sp=p.matrixTransform(ctm);
      const hit=document.elementFromPoint(sp.x,sp.y);
      const good=hit&&(hit===t||(hit.closest&&hit.closest('text')===t));
      if(!good){ occl.push([i,t.textContent.slice(0,26),hit?hit.tagName:'null']); break; }
    }
  });
  const shapes=[...svg.querySelectorAll('line,path,rect,circle,polygon,polyline')];
  const cross=[]; const STEP=0.25;
  const discBox=[...svg.querySelectorAll('.stn-disc')].map(c=>({
    cx:+c.getAttribute('cx'), cy:+c.getAttribute('cy'), r:+c.getAttribute('r')}));
  const inDisc=(t)=>{ for(const d of discBox){
      if(Math.abs(t.x+t.w/2-d.cx)<d.r-0.2 && Math.abs(t.y+t.h/2-d.cy)<d.r-0.2) return true;
    } return false; };
  shapes.forEach((s,si)=>{
    const cs=getComputedStyle(s); const sw=parseFloat(cs.strokeWidth);
    if(cs.stroke==='none'||!sw) return;
    const tag=s.tagName.toLowerCase(); const pts=[];
    const push=(ax,ay,bx,by)=>{const L=Math.hypot(bx-ax,by-ay),n=Math.max(1,Math.ceil(L/STEP));
      for(let k=0;k<=n;k++) pts.push([ax+(bx-ax)*k/n, ay+(by-ay)*k/n]);};
    if(tag==='line'){push(+s.getAttribute('x1'),+s.getAttribute('y1'),+s.getAttribute('x2'),+s.getAttribute('y2'));}
    else if(tag==='circle'){const cx=+s.getAttribute('cx'),cy=+s.getAttribute('cy'),r=+s.getAttribute('r');
      const n=Math.max(48,Math.ceil(2*Math.PI*r/STEP));
      for(let k=0;k<=n;k++){const a=2*Math.PI*k/n; pts.push([cx+r*Math.cos(a),cy+r*Math.sin(a)]);}}
    else if(tag==='rect'){const x=+s.getAttribute('x'),y=+s.getAttribute('y'),
        w=+s.getAttribute('width'),h=+s.getAttribute('height');
      push(x,y,x+w,y);push(x+w,y,x+w,y+h);push(x+w,y+h,x,y+h);push(x,y+h,x,y);}
    else if(tag==='polygon'||tag==='polyline'){
      const v=(s.getAttribute('points')||'').trim().split(/[\s,]+/).map(Number);
      for(let k=0;k+3<v.length;k+=2) push(v[k],v[k+1],v[k+2],v[k+3]);
      if(tag==='polygon'&&v.length>=6) push(v[v.length-2],v[v.length-1],v[0],v[1]);}
    else if(tag==='path'){const L=s.getTotalLength(),n=Math.max(2,Math.ceil(L/STEP));
      for(let k=0;k<=n;k++){const p=s.getPointAtLength(L*k/n); pts.push([p.x,p.y]);}}
    for(const p of pts){
      for(const t of ti){
        if(inDisc(t)) continue;
        if(p[0]>t.x&&p[0]<t.x+t.w&&p[1]>t.y&&p[1]<t.y+t.h){
          cross.push([si,t.i,+p[0].toFixed(2),+p[1].toFixed(2),tag,(s.getAttribute('class')||'')]);
          break;
        }
      }
    }
  });
  const whiteNot=[];
  [...svg.querySelectorAll('*')].forEach(el=>{
    const cs=getComputedStyle(el);
    for(const prop of ['fill','stroke']){
      if(hex(cs[prop])==='#FFFFFF'&&el.tagName!=='svg'){
        const isNum=el.tagName==='text'&&(el.getAttribute('data-block')||'').startsWith('stn-num');
        if(!isNum) whiteNot.push(el.tagName+'.'+(el.getAttribute('class')||'')+':'+prop);
      }
    }
  });
  const geo={};
  [...svg.querySelectorAll('[class]')].forEach(el=>{
    const cl=(el.getAttribute('class')||'').split(/\s+/).filter(Boolean);
    for(const c of cl){
      if(geo[c]) continue;
      const a={tag:el.tagName.toLowerCase(),cls:c};
      for(const k of ['x1','y1','x2','y2','cx','cy','r','x','y','width','height'])
        if(el.hasAttribute(k)) a[k]=parseFloat(el.getAttribute(k));
      if(el.hasAttribute('points')) a.points=el.getAttribute('points');
      if(el.hasAttribute('d')) a.d=el.getAttribute('d');
      a.joint=el.getAttribute('data-joint'); a.station=el.getAttribute('data-station');
      a.nodeName=el.getAttribute('data-name');
      geo[c]=a;
    }
  });
  const allGeo=[];
  [...svg.querySelectorAll('[class]')].forEach(el=>{
    const cls=(el.getAttribute('class')||'').split(/\s+/).filter(Boolean);
    if(!cls.length) return;
    const a={tag:el.tagName.toLowerCase(),cls:cls};
    for(const k of ['x1','y1','x2','y2','cx','cy','r','x','y','width','height'])
      if(el.hasAttribute(k)) a[k]=parseFloat(el.getAttribute(k));
    if(el.hasAttribute('points')) a.points=el.getAttribute('points');
    if(el.hasAttribute('d')) a.d=el.getAttribute('d');
    a.joint=el.getAttribute('data-joint'); a.station=el.getAttribute('data-station');
    a.nodeName=el.getAttribute('data-name'); a.head=el.getAttribute('data-head');
    a.seg=el.getAttribute('data-seg'); a.fill=hex(getComputedStyle(el).fill);
    a.stroke=hex(getComputedStyle(el).stroke);
    a.sw=parseFloat(getComputedStyle(el).strokeWidth);
    allGeo.push(a);
  });
  const metro=[...svg.querySelectorAll('.metro')].map(p=>{
    const v=(p.getAttribute('d')||'').match(/-?[\d.]+/g).map(Number);
    return {seg:+p.getAttribute('data-seg'), pts:v, stroke:hex(getComputedStyle(p).stroke),
            w:parseFloat(getComputedStyle(p).strokeWidth)};
  }).sort((a,b)=>a.seg-b.seg);
  const discs=[...svg.querySelectorAll('.stn-disc')].map(c=>({
    n:c.getAttribute('data-station'), cx:+c.getAttribute('cx'), cy:+c.getAttribute('cy'),
    r:+c.getAttribute('r'), fill:hex(getComputedStyle(c).fill)}));
  const segs=[...svg.querySelectorAll('.seg')].map(r=>({
    bar:r.getAttribute('data-bar'), group:+r.getAttribute('data-group'),
    x:+r.getAttribute('x'), w:+r.getAttribute('width')}));
  const strokes=new Set();
  [...svg.querySelectorAll('*')].forEach(el=>{
    const cs=getComputedStyle(el);
    if(cs.stroke&&cs.stroke!=='none'&&parseFloat(cs.strokeWidth)>0) strokes.add(parseFloat(cs.strokeWidth));
  });
  const doc={texts:ti, overlaps, oob, occl, cross:cross.slice(0,300),
             ncross:cross.length, whiteNot:[...new Set(whiteNot)], geo, allGeo, metro,
             discs, segs, strokes:[...strokes].sort((a,b)=>a-b),
             pageText:ti.map(t=>t.text).join(' ')};
  const pre=document.createElement('pre'); pre.id='probe';
  pre.textContent=JSON.stringify(doc); document.body.appendChild(pre);
});
</script>
"""


def run_probe():
    html = HTML.read_text(encoding="utf-8")
    TMP.mkdir(exist_ok=True)
    f = TMP / "probe.html"
    f.write_text(html.replace("</body>", PROBE + "\n</body>"), encoding="utf-8")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--hide-scrollbars", "--window-size=1700,1250",
           "--virtual-time-budget=15000", "--dump-dom", f.as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print("probe Chrome failed (%d)" % r.returncode)
        sys.exit(2)
    m = re.search(r'<pre id="probe">(.*?)</pre>', r.stdout, re.S)
    if not m:
        print("probe did not run; Chrome tail:\n", r.stdout[-1500:])
        sys.exit(2)
    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    return json.loads(raw)


# ---------------------------------------------------------------- colour
def lum(h):
    c = [int(h[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- fonts
def ttc_faces(path):
    d = path.read_bytes()
    if d[:4] == b"ttcf":
        n = struct.unpack(">I", d[8:12])[0]
        offs = struct.unpack(">%dI" % n, d[12:12 + 4 * n])
    else:
        offs = (0,)
    out = []
    for off in offs:
        num = struct.unpack(">H", d[off + 4:off + 6])[0]
        tabs = {}
        for i in range(num):
            t, cs, o, l = struct.unpack(">4sIII",
                                        d[off + 12 + 16 * i: off + 28 + 16 * i])
            tabs[t.decode("latin1")] = (o, l)
        out.append((d, tabs))
    return out


def face_name(d, tabs):
    o, l = tabs["name"]
    fmt, count, so = struct.unpack(">HHH", d[o:o + 6])
    for i in range(count):
        pid, eid, lid, nid, ln, off = struct.unpack(">HHHHHH",
                                                   d[o + 6 + 12 * i:o + 18 + 12 * i])
        if nid == 6:
            s = d[o + so + off:o + so + off + ln]
            try:
                return s.decode("utf-16-be") if pid == 3 else s.decode("latin1")
            except Exception:
                return None
    return None


def face_cps(d, tabs):
    o, l = tabs["cmap"]
    ver, n = struct.unpack(">HH", d[o:o + 4])
    cps = set()
    for i in range(n):
        pid, eid, so = struct.unpack(">HHI", d[o + 4 + 8 * i:o + 12 + 8 * i])
        p = o + so
        fmt = struct.unpack(">H", d[p:p + 2])[0]
        if fmt == 4:
            segx2 = struct.unpack(">H", d[p + 6:p + 8])[0]
            seg = segx2 // 2
            ends = struct.unpack(">%dH" % seg, d[p + 14:p + 14 + segx2])
            starts = struct.unpack(">%dH" % seg,
                                   d[p + 16 + segx2:p + 16 + 2 * segx2])
            for a, b in zip(starts, ends):
                if a == 0xFFFF:
                    continue
                cps.update(range(a, min(b, 0xFFFF) + 1))
        elif fmt == 12:
            ng = struct.unpack(">I", d[p + 12:p + 16])[0]
            for g in range(ng):
                a, b, _ = struct.unpack(">III", d[p + 16 + 12 * g:p + 28 + 12 * g])
                cps.update(range(a, min(b, 0x10FFFF) + 1))
    return cps


def load_faces():
    faces = {}
    for path in ("/System/Library/Fonts/Avenir Next.ttc",
                 "/System/Library/Fonts/Menlo.ttc"):
        for d, tabs in ttc_faces(Path(path)):
            nm = face_name(d, tabs)
            if nm:
                faces[nm] = face_cps(d, tabs)
    return faces


def svg_chars_by_family(root):
    out = []
    ns = "{http://www.w3.org/2000/svg}"
    for el in root.iter(ns + "text"):
        kids = list(el)
        if not kids:
            out.append((el.text or "", "sans"))
            continue
        for sp in kids:
            fam = sp.get("font-family") or ""
            out.append((sp.text or "", "mono" if "Menlo" in fam else "sans"))
    return out


# ---------------------------------------------------------------- geometry
def poly_points(el):
    return [float(v) for v in (el.get("points") or "").replace(",", " ").split()]


def inside(el, x, y, slack=0.02):
    """Strictly inside a rect / circle / polygon (drawing coordinates)."""
    tag = el["tag"]
    if tag == "rect":
        return (el["x"] + slack < x < el["x"] + el["width"] - slack
                and el["y"] + slack < y < el["y"] + el["height"] - slack)
    if tag == "circle":
        return math.hypot(x - el["cx"], y - el["cy"]) < el["r"] - slack
    if tag == "polygon":
        v = [float(p) for p in el["points"].replace(",", " ").split()]
        pts = list(zip(v[0::2], v[1::2]))
        inside_flag = False
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            if (y1 > y) != (y2 > y):
                xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                if xi > x:
                    inside_flag = not inside_flag
        return inside_flag
    return False


# ---------------------------------------------------------------- the checks
def main():
    doc = run_probe()
    texts = doc["texts"]
    print("page text elements: %d" % len(texts))

    # 1 minimum size
    small = [(t["text"][:26], round(t["fs"], 3)) for t in texts
             if t["fs"] < 2.45 - 1e-4]
    if small:
        fail(1, "text under 2.45 mm: %s" % small[:5])
    else:
        ok(1, "all %d text elements >= 2.45 mm (min %.2f)"
           % (len(texts), min(t["fs"] for t in texts)))

    # 2 no text on text
    if doc["overlaps"]:
        for a, b, ox, oy in doc["overlaps"][:8]:
            fail(2, "overlap %.2fx%.2f mm between %r and %r"
                 % (ox, oy, texts[a]["text"][:30], texts[b]["text"][:30]))
    else:
        ok(2, "no two text boxes overlap")

    # 3 inside the margins
    if doc["oob"]:
        for i, x0, y0, x1, y1 in doc["oob"][:8]:
            fail(3, "outside the margins: %r at %.2f,%.2f-%.2f,%.2f"
                 % (texts[i]["text"][:30], x0, y0, x1, y1))
    else:
        ok(3, "all text inside x 12-408, y 12-285")

    # 4 occlusion, every glyph centre
    if doc["occl"]:
        for i, s, hit in doc["occl"][:6]:
            fail(4, "text %r is painted under %s" % (s, hit))
    else:
        ok(4, "every glyph centre of every text element is the topmost paint")

    # 5 strokes against text boxes
    if doc["ncross"]:
        for si, ti, x, y, tag, cls in doc["cross"][:10]:
            fail(5, "%s%s at %.2f,%.2f crosses %r"
                 % (tag, ("." + cls) if cls else "", x, y,
                    texts[ti]["text"][:32]))
        print("     (%d crossing samples)" % doc["ncross"])
    else:
        ok(5, "no stroked line, path, circle or polygon edge crosses a text box")

    # 6 colours and station phase colours
    bad = [(t["text"][:20], t["fill"]) for t in texts
           if t["fill"] != "#FFFFFF" and t["fill"] not in TEXT_COLORS]
    badw = [t["text"][:20] for t in texts
            if t["fill"] == "#FFFFFF" and "stn-num" not in (t["block"] or "")]
    if bad or badw:
        fail(6, "text fill outside the palette: %s %s" % (bad[:4], badw[:4]))
    else:
        ok(6, "text fills are ink, muted, a phase colour or safety; "
              "white only on station numbers")
    lows = [(c, round(contrast(c, "#FFFFFF"), 2)) for c in sorted(TEXT_COLORS)
            if contrast(c, "#FFFFFF") < 4.5]
    if lows:
        fail(6, "text colour below 4.5:1 on white: %s" % lows)
    else:
        ok(6, "every text colour clears 4.5:1 on white (min %.2f:1)"
           % min(contrast(c, "#FFFFFF") for c in TEXT_COLORS))
    copy = brief_copy()
    phase_of = {n: ph for (n, ph, _t, _w) in copy["stage_table"]}
    disc = {int(d["n"]): d for d in doc["discs"]}
    errs = []
    for n in range(11):
        want = PHASE_COL[phase_of[n]]
        got = disc.get(n, {}).get("fill")
        if got != want:
            errs.append("station %d is %s, its phase is %s" % (n, got, want))
    if errs:
        for e in errs:
            fail(6, "disc colour: " + e)
    else:
        ok(6, "each station disc carries its stage's phase colour")
    badnum = []
    for t in texts:
        if t["fill"] == "#FFFFFF":
            f = disc.get(int(t["stn"] or -1), {}).get("fill") if t["stn"] else None
            if not f or contrast("#FFFFFF", f) < 4.5:
                badnum.append((t["text"], f))
    if badnum:
        fail(6, "white station number below 4.5:1 on its own disc: %s" % badnum[:5])
    else:
        ok(6, "each white station number clears 4.5:1 on its own disc")

    # 7 palette only
    src = SVG.read_text(encoding="utf-8")
    hexes = set(re.findall(r"#[0-9A-Fa-f]{6}", src))
    extra = {h.upper() for h in hexes} - PALETTE - {"#FFFFFF"}
    if extra:
        fail(7, "non-palette colours in the SVG: %s" % sorted(extra))
    else:
        ok(7, "SVG uses only the palette tokens (%d hex values)" % len(hexes))
    if doc["whiteNot"]:
        fail(7, "white paint outside station numbers: %s" % doc["whiteNot"][:5])
    else:
        ok(7, "white is painted only on station numbers")
    ns_src = re.sub(r'xmlns(:xlink)?="[^"]*"', "", src)
    banned = [w for w in ("<filter", "Gradient", "<pattern", "<image",
                          "http://", "https://", "url(") if w in ns_src]
    if banned:
        fail(7, "forbidden construct in the SVG: %s" % banned)
    else:
        ok(7, "no filter, gradient, pattern, image or external URL")

    # 8 copy from BRIEF, every block
    page = norm(doc["pageText"])
    missing = [s for s in copy["backticked"] if norm(s) not in page]
    if missing:
        for s in missing[:8]:
            fail(8, "copy missing or altered: %r" % s[:70])
        print("     (%d of %d backticked strings missing)"
              % (len(missing), len(copy["backticked"])))
    else:
        ok(8, "all %d backticked strings from BRIEF section 4 are on the page"
           % len(copy["backticked"]))
    by_block, by_stage = {}, {}
    for t in texts:
        if t["block"]:
            by_block.setdefault(t["block"], []).append(t)
        if t["stage"] is not None:
            by_stage.setdefault(int(t["stage"]), []).append(t)

    def joined(block):
        return norm(" ".join(t["text"] for t in
                             sorted(by_block.get(block, []),
                                    key=lambda t: int(t["line"] or 0))))

    bad_tab = []
    for i, row in enumerate(copy["pipeline"]):
        if len(row) != 3:
            bad_tab.append("pipeline row %d has %d cells" % (i, len(row)))
            continue
        step, sent, cmd = row
        if norm(joined("step-name%d" % i)) != norm(step):
            bad_tab.append("pipeline %d name %r" % (i, joined("step-name%d" % i)))
        if joined("step-sent%d" % i) != norm(sent):
            bad_tab.append("pipeline %d sentence %r"
                           % (i, joined("step-sent%d" % i)[:45]))
        if norm(joined("step-cmd%d" % i)) != norm(cmd):
            bad_tab.append("pipeline %d command %r" % (i, joined("step-cmd%d" % i)))
    for row in copy["parts"]:
        if len(row) != 2:
            bad_tab.append("parts row malformed: %s" % row)
            continue
        name, meaning = row
        if norm(joined("part-" + name)) != norm(name):
            bad_tab.append("part name %r" % name)
        if joined("partmean-" + name) != norm(meaning):
            bad_tab.append("part %r meaning %r" % (name,
                                                   joined("partmean-" + name)[:45]))
    for row in copy["steps"]:
        if len(row) != 2:
            bad_tab.append("time-step row malformed: %s" % row)
            continue
        feat, note = row
        if norm(joined("feat-" + feat)) != norm(feat):
            bad_tab.append("feature name %r" % feat)
        if norm(joined("feat-" + feat)) != norm(feat) or norm(
                joined("note-" + feat)) != norm(note):
            bad_tab.append("feature %r note %r" % (feat,
                                                   joined("note-" + feat)[:45]))
    if not copy["pipeline"] or not copy["parts"] or not copy["steps"]:
        bad_tab.append("a BRIEF section 4 table did not parse")
    order = ["learn", "do", "on", "pass", "explain"]
    for (n, phase, title, time) in copy["stage_table"]:
        ts = by_stage.get(n, [])
        titles = [t["text"] for t in ts if t["block"].startswith("stage-title")]
        if title not in titles:
            bad_tab.append("stage %d title %r" % (n, title))
            continue
        tsec = [t["text"] for t in ts if t["block"] == "stage-time-%d" % n]
        if not tsec or tsec[0].strip() != time:
            bad_tab.append("stage %d time %r" % (n, time))
        seen = []
        for t in ts:
            if t["field"] and (not seen or seen[-1] != t["field"]):
                seen.append(t["field"])
        if seen != order:
            bad_tab.append("stage %d field order %s" % (n, seen))
            continue
        field_txt = {}
        for t in ts:
            if t["field"]:
                field_txt.setdefault(t["field"], []).append(t)
        for (lab, want) in copy["stages"].get(n, []):
            lines = sorted(field_txt.get(lab, []), key=lambda t: int(t["line"] or 0))
            got = norm(" ".join(t["text"] for t in lines))
            if got != norm(want):
                bad_tab.append("stage %d %s differs: %r" % (n, lab, got[:45]))
    # 8b each block must sit in its own band and column (BRIEF 8.14)
    windows = [
        ("title", False, (12.0, 260.0, 11.5, 31.0)),
        ("sub", False, (12.0, 280.0, 26.0, 32.0)),
        ("howto", False, (245.0, 408.0, 12.0, 25.0)),
        ("phase-", False, (245.0, 408.0, 23.5, 30.0)),
        ("a-head", False, (12.0, 60.0, 32.0, 40.0)),
        ("a-parts-head", False, (156.0, 200.0, 32.0, 40.0)),
        ("a-time-head", False, (282.0, 330.0, 32.0, 40.0)),
        ("b-head", False, (12.0, 60.0, 70.0, 82.0)),
        ("safety-label", False, (150.0, 360.0, 82.0, 92.0)),
        ("gutter-0-pass", False, (12.0, 30.0, 95.0, 150.0)),
        ("p1-head", False, (12.0, 60.0, 212.0, 222.0)),
        ("p2-head", False, (156.0, 210.0, 212.0, 222.0)),
        ("p3-head", False, (282.0, 340.0, 212.0, 222.0)),
        ("role-0", False, (12.0, 52.0, 225.0, 277.0)),
        ("role-1", False, (55.0, 98.0, 225.0, 277.0)),
        ("role-2", False, (99.0, 152.0, 225.0, 277.0)),
        ("ladder-0", False, (282.0, 320.0, 215.0, 232.0)),
        ("ladder-3", False, (370.0, 408.0, 215.0, 232.0)),
        ("rule-0-lead", False, (282.0, 408.0, 232.0, 277.0)),
        ("rule-4-reason", False, (282.0, 408.0, 240.0, 277.0)),
        ("foot-left", False, (12.0, 280.0, 277.0, 285.0)),
        ("foot-right", False, (170.0, 408.0, 277.0, 285.0)),
        ("p1-setup2", False, (12.0, 152.0, 240.0, 277.0)),
        ("after-head", False, (345.0, 408.0, 155.0, 170.0)),
    ]
    for prefix, exact, (x0, x1, y0, y1) in windows:
        ts = [t for t in texts
              if (t["block"] == prefix if exact else (t["block"] or "").startswith(prefix))]
        if not ts:
            bad_tab.append("block %r is missing for the location test" % prefix)
            continue
        for t in ts:
            cx, cy = t["x"] + t["w"] / 2.0, t["y"] + t["h"] / 2.0
            if not (x0 - 0.5 <= cx <= x1 + 0.5 and y0 - 0.5 <= cy <= y1 + 0.5):
                bad_tab.append("%r sits at %.1f,%.1f outside its band and column "
                               "(%.0f-%.0f, %.0f-%.0f)"
                               % (prefix, cx, cy, x0, x1, y0, y1))
                break
    if len(copy["stage_table"]) != 11:
        bad_tab.append("parsed %d stage rows from BRIEF, expected 11"
                       % len(copy["stage_table"]))
    if bad_tab:
        for s in bad_tab[:10]:
            fail(8, s)
    else:
        ok(8, "all 11 stage blocks, the pipeline, parts and time-step tables "
              "match BRIEF section 4 as written")

    # 9 stations, times, bars
    stn = [d["n"] for d in doc["discs"]]
    if sorted(stn, key=int) != [str(i) for i in range(11)]:
        fail(9, "station discs are %s, expected 0-10" % stn)
    else:
        ok(9, "eleven stations, 0 to 10")
    times = [t["text"].strip() for t in texts
             if t["block"].startswith("stage-time-")]
    wks = []
    for s in times:
        m = re.match(r"^(\d+) weeks?$", s)
        wks.append(int(m.group(1)) if m else None)
    if len(wks) != 11 or None in wks:
        fail(9, "stage times unreadable: %s" % times)
    elif sum(wks) != 19:
        fail(9, "stage times total %d weeks, expected 19" % sum(wks))
    else:
        ok(9, "stage times total 19 weeks: %s" % "+".join(map(str, wks)))
    for bar, want in (("state", [7, 2, 16]), ("action", [7, 2])):
        groups = {}
        for s in doc["segs"]:
            if s["bar"] == bar:
                groups[s["group"]] = groups.get(s["group"], 0) + 1
        got = [groups.get(i, 0) for i in range(len(want))]
        if got != want:
            fail(9, "%s bar segments %s, expected %s" % (bar, got, want))
        elif len({round(s["w"], 3) for s in doc["segs"] if s["bar"] == bar}) != 1:
            fail(9, "%s bar does not use one segment width" % bar)
        else:
            ok(9, "%s bar: %s segments, one width" % (bar, "+".join(map(str, want))))
    widths = {round(s["w"], 3) for s in doc["segs"] if s["bar"] in ("state", "action")}
    if len(widths) > 1:
        fail(9, "state and action bars use different segment widths: %s" % widths)
    # group gaps must be at least twice the gap between segments (BRIEF 8.3)
    for bar in ("state", "action"):
        seg = sorted([x for x in doc["segs"] if x["bar"] == bar],
                     key=lambda x: x["x"])
        gaps, groups = [], []
        for a, b in zip(seg, seg[1:]):
            g = round(b["x"] - (a["x"] + a["w"]), 3)
            (groups if a["group"] != b["group"] else gaps).append(g)
        if not gaps or not groups:
            fail(9, "%s bar has no group boundary" % bar)
        elif min(groups) < 2.0 * max(gaps) - 0.01:
            fail(9, "%s bar group gaps %s are not twice the %s gaps"
                 % (bar, sorted(set(groups)), sorted(set(gaps))))
        else:
            ok(9, "%s bar group gaps are %.2f mm against %.2f mm inside groups "
                  "(%.1fx)" % (bar, min(groups), max(gaps),
                               min(groups) / max(gaps)))

    # 10 one continuous route
    metro_line(doc, texts)

    # 11 the drawn physics
    check_robot(doc, texts)

    # 12 shared baselines and clear space
    rows = {}
    for t in texts:
        if t["field"] and t["stage"] is not None:
            row = 0 if int(t["stage"]) <= 5 else 1
            if t["line"] == "0":
                rows.setdefault((row, t["field"]), set()).add(round(t["y"], 3))
    badrows = {k: sorted(v) for k, v in rows.items() if len(v) > 1}
    if badrows:
        fail(12, "field baselines not shared in a row: %s" % badrows)
    else:
        ok(12, "every field shares one baseline across its row (%d groups)"
           % len(rows))
    tight = []
    for st in range(11):
        ts = [t for t in texts if t["stage"] == str(st)]
        blocks = {}
        for t in ts:
            key = t["field"] or ("title" if t["block"].startswith("stage-title")
                                 else None)
            if key is None:
                continue
            r = blocks.setdefault(key, [1e9, -1e9])
            r[0] = min(r[0], t["y"])
            r[1] = max(r[1], t["y"] + t["h"])
        seq = ["title", "learn", "do", "on", "pass", "explain"]
        for a, b in zip(seq, seq[1:]):
            if a in blocks and b in blocks:
                gap = blocks[b][0] - blocks[a][1]
                if gap < 2.5 - 0.02:
                    tight.append((st, a, b, round(gap, 2)))
    if tight:
        for t in tight[:6]:
            fail(12, "stage %d: %.2f mm between %s and %s"
                 % (t[0], t[3], t[1], t[2]))
    else:
        ok(12, "every field pair has at least 2.5 mm of clear space")
    # 12b the route crosses no text (already covered by 5; checked explicitly)
    cross_metro = [c for c in doc["cross"] if "metro" in (c[5] or "")]
    if cross_metro:
        fail(12, "the metro line crosses %d text boxes" % len(cross_metro))

    # 13 one grid: fields, stations, band headings and panel edges
    grid = [B.G[i] for i in range(6)]
    sx = [B.G[i] + B.ST_DX for i in range(6)]
    near = lambda v, vals: min(abs(v - g) for g in vals) < 0.01
    offgrid = [(t["text"][:22], round(t["ax"], 3)) for t in texts
               if (t["field"] or t["block"].startswith("stage-title"))
               and not near(t["ax"], sx)]
    if offgrid:
        fail(13, "stage text off the column grid: %s" % offgrid[:6])
    else:
        ok(13, "every stage field, title and time sits on the column grid")
    heads = ["a-head", "a-parts-head", "a-time-head", "b-head", "p1-head",
             "p2-head", "p3-head"]
    badh = [(h, round([t for t in texts if t["block"] == h][0]["ax"], 3))
            for h in heads
            if [t for t in texts if t["block"] == h]
            and not near([t for t in texts if t["block"] == h][0]["ax"],
                         [B.ML] + grid)]
    if len([h for h in heads if [t for t in texts if t["block"] == h]]) != len(heads):
        fail(13, "a band heading is missing")
    elif badh:
        fail(13, "band headings off the one grid: %s" % badh)
    else:
        ok(13, "every band heading starts on x = 12 or a G value "
              "(seams at G[2] = %.3f and G[4] = %.3f)" % (B.G[2], B.G[4]))
    if not (near(B.PANEL_X[0], [B.ML]) and near(B.PANEL_X[1], [B.G[2]])
            and near(B.PANEL_X[2], [B.G[4]])):
        fail(13, "band A/C panel left edges are not 12, G[2], G[4]")
    if len({round(B.G[i + 1] - B.G[i], 4) for i in range(5)}) != 1:
        fail(13, "grid pitch is not constant")
    for d in doc["discs"]:
        if not near(d["cx"], sx):
            fail(13, "station %s at x %.2f is off grid" % (d["n"], d["cx"]))
    else:
        ok(13, "one grid: 6 columns of %.3f mm from %.1f to %.1f"
           % (B.COLW, B.G[0], B.G[5] + B.COLW))

    # 17 numbers keep their units; no widow words (BRIEF section 7.7, 7.8)
    num_bad = []
    for t in texts:
        if (t["block"] or "").startswith("stn-num"):
            continue
        if NUM_END.search(t["text"]):
            num_bad.append(t["text"][-28:])
    if num_bad:
        for s in num_bad[:6]:
            fail(17, "a line ends on a bare number: ...%r" % s)
    else:
        ok(17, "no line ends between a number and its unit or noun")
    widows = []
    for block in by_block:
        ts = sorted(by_block[block], key=lambda t: int(t["line"] or 0))
        if len(ts) < 2 or len(ts[-1]["text"].split()) != 1:
            continue
        last, prev = ts[-1], ts[-2]
        measure = float(last["measure"] or 0)
        cand = prev["tailW"] + last["w"]
        if measure and cand <= measure + 0.01:
            widows.append("%r could have taken %r" % (last["text"],
                                                      prev["text"][-18:]))
    if widows:
        for s in widows[:6]:
            fail(17, "a single-word last line was avoidable: %s" % s)
    else:
        ok(17, "no block ends on a single-word line")

    # 19b the three flow links' heads (BRIEF 8.10)
    links = {}
    for el in doc["allGeo"]:
        for c in el["cls"]:
            if c in ("flow-2way", "flow-1way"):
                links.setdefault(c, []).append(el)
    nodes = {g["nodeName"].replace("-", " "): g for g in doc["allGeo"]
             if g["cls"] and "node" in g["cls"] and g["nodeName"]}

    def heads_of(name):
        out = []
        for el in links.get(name, []):
            if el["tag"] == "polygon":
                v = [float(q) for q in el["points"].replace(",", " ").split()]
                out.append((v[0], v[1]))
        return out

    for name, want in (("flow-2way", 2), ("flow-1way", 1)):
        got = heads_of(name)
        if len(got) != want:
            fail(19, "the %s link has %d arrowheads, expected %d"
                 % (name, len(got), want))
            continue
        if name == "flow-1way":
            nd = nodes.get("DGX Spark")
            tip = got[0]
            if nd is None or abs(math.hypot(tip[0] - nd["cx"],
                                            tip[1] - nd["cy"]) - nd["r"]) > 0.05:
                fail(19, "the datasets head does not sit on DGX Spark")
            else:
                ok(19, "the datasets link has one head, at DGX Spark")
        else:
            names = set()
            for tip in got:
                for nm, nd in nodes.items():
                    if abs(math.hypot(tip[0] - nd["cx"], tip[1] - nd["cy"])
                           - nd["r"]) <= 0.05:
                        names.add(nm)
            if names != {"Robot Orin", "Station Orin"}:
                fail(19, "the wired link's heads are on %s" % sorted(names))
            else:
                ok(19, "the wired link has two heads, one on each Orin")

    # 22 text roles (BRIEF 8.11)
    role_bad = []
    for t in texts:
        b = t["block"] or ""
        if b.startswith("gutter-") and b.endswith("-pass"):
            if t["fill"] != INK or t["weight"] != "600":
                role_bad.append("Pass is %s/%s" % (t["fill"], t["weight"]))
        if b.startswith("s-") and b.endswith("-pass"):
            if t["fill"] != INK or t["weight"] != "600":
                role_bad.append("%s is %s/%s" % (b, t["fill"], t["weight"]))
        if (b.startswith("s-") and b.endswith("-explain")) or \
                b.startswith("gutter-") and b.endswith("-explain"):
            if t["fill"] != MUTED or t["weight"] != "400":
                role_bad.append("%s is %s/%s" % (b, t["fill"], t["weight"]))
        if b.startswith("stage-time-"):
            if t["fill"] != MUTED:
                role_bad.append("%s is %s" % (b, t["fill"]))
        if b == "safety-label" and t["fill"] != SAFETY:
            role_bad.append("the safety label is %s" % t["fill"])
        if b.startswith("stn-num-") and (t["fill"] != "#FFFFFF"
                                         or t["weight"] != "600"):
            role_bad.append("%s is %s/%s" % (b, t["fill"], t["weight"]))
    if role_bad:
        for r in role_bad[:6]:
            fail(22, "text role: " + r)
    else:
        ok(22, "Pass is ink demi, Explain muted, times muted, the safety label "
              "is safety colour and station numbers are white demi")

    # 23 row 1 Pass is three lines in stages 2 and 3 (BRIEF 8.9)
    lines = {}
    for t in texts:
        b = t["block"] or ""
        if b.startswith("s-") and b.endswith("-pass"):
            lines[b] = int(t["line"] or 0) + 1
    tall = [n for n in range(6) if lines.get("s-%d-pass" % n, 0) == 3]
    if not tall:
        fail(23, "row 1's Pass field is %s lines, expected three in stages 2 "
                 "and 3" % {n: lines.get("s-%d-pass" % n) for n in range(6)})
    else:
        ok(23, "row 1's Pass field is three lines (stages %s)"
           % ", ".join(map(str, tall)))

    # 24 station 10 is a real double ring (BRIEF 8.2)
    ring = doc["geo"].get("stn-ring")
    d10 = [d for d in doc["discs"] if d["n"] == "10"]
    if ring is None or not d10:
        fail(24, "station 10 has no outer ring")
    else:
        inner = ring["r"] - (ring.get("sw", 0.0) / 2.0) if "sw" in ring else None
        r10 = d10[0]["r"]
        # the ring's stored r is its centre radius; its stroke is not in geo,
        # so read the widths from the rendered attributes instead
        src = SVG.read_text(encoding="utf-8")
        m = re.search(r'class="stn-ring"[^>]*r="([\d.]+)"[^>]*stroke-width="([\d.]+)"',
                      src) or re.search(
            r'<circle[^>]*class="stn-ring"[^>]*/>', src)
        rr, sw = None, None
        for el in ET.parse(SVG).getroot().iter("{http://www.w3.org/2000/svg}circle"):
            if "stn-ring" in (el.get("class") or "").split():
                rr = float(el.get("r"))
                sw = float(el.get("stroke-width"))
        if rr is None:
            fail(24, "cannot read the outer ring's radius")
        else:
            gap = (rr - sw / 2.0) - r10
            if gap < 0.5 - 0.01:
                fail(24, "the white gap inside station 10's ring is %.2f mm, "
                         "below 0.5" % gap)
            elif abs(rr - ring["r"]) > 0.01:
                fail(24, "the ring radius disagrees with the render")
            else:
                ok(24, "station 10 is a double ring with a %.2f mm white gap "
                      "and a %.2f mm outer radius" % (gap, rr))

    # 25 the left turn: one 45 degree descent into station 6, 4 mm of air
    ms = doc["metro"]
    seg6 = ms[5]["pts"] if len(ms) > 5 else []
    d10_ = [d for d in doc["discs"] if d["n"] == "6"]
    if len(seg6) < 12 or not d10_:
        fail(25, "cannot read the return path")
    else:
        pts = list(zip(seg6[0::2], seg6[1::2]))
        last = pts[-1]
        s6 = d10_[0]
        if math.hypot(last[0] - s6["cx"], last[1] - s6["cy"]) > 0.01:
            fail(25, "the return does not end on station 6's centre")
        # the final leg must be exactly 45 degrees, with no other leg after it
        (ax, ay), (bx, by) = pts[-2], pts[-1]
        if abs(abs(bx - ax) - abs(by - ay)) > 0.02:
            fail(25, "the final descent into station 6 is not 45 degrees "
                     "(dx %.2f, dy %.2f)" % (bx - ax, by - ay))
        elif bx > ax:
            fail(25, "the final descent does not come from the right")
        else:
            ok(25, "the return makes one straight 45 degree descent into "
                  "station 6 (dx %.2f, dy %.2f)" % (bx - ax, by - ay))
        # air above and below the lane: find the long horizontal leg
        lane_y, lane_len = None, 0.0
        for a, c in zip(pts, pts[1:]):
            if abs(a[1] - c[1]) < 0.01 and abs(a[0] - c[0]) > lane_len:
                lane_y, lane_len = a[1], abs(a[0] - c[0])
        row1 = [t for t in texts if t["field"] and t["stage"] is not None
                and int(t["stage"]) <= 5]
        bottom = max(t["y"] + t["h"] for t in row1) if row1 else None
        if lane_y is None or lane_len < 300 or bottom is None:
            fail(25, "cannot find the return lane (longest horizontal leg "
                     "%.1f mm)" % lane_len)
        else:
            above = lane_y - 0.8 - bottom
            below = (s6["cy"] - s6["r"]) - (lane_y + 0.8)
            if above < 4.0 - 0.01 or below < 4.0 - 0.01:
                fail(25, "the return has %.2f mm of air above and %.2f mm "
                         "below, less than 4" % (above, below))
            else:
                ok(25, "the return line (%.1f mm long) has %.2f mm of air "
                      "above and %.2f mm below it" % (lane_len, above, below))

    # 26 header: 1 mm between the subtitle's descenders and the rule (8.8)
    sub = [t for t in texts if t["block"] == "sub"]
    rule_y = None
    for el in doc["allGeo"]:
        if "rule" in el["cls"] and el["tag"] == "line" and el.get("y1", 1e9) < 40:
            rule_y = el["y1"]
    if sub and rule_y is not None:
        gap = rule_y - (sub[0]["y"] + sub[0]["h"])
        if gap < 1.0 - 0.01:
            fail(26, "only %.2f mm between the subtitle and the header rule"
                 % gap)
        else:
            ok(26, "%.2f mm between the subtitle's descenders and the header "
                  "rule" % gap)

    # 27 the lidar figure is at least 32 mm tall, arrows mid-gap, phrases glued
    draw_els = [el for el in doc["allGeo"] if el.get("cls")
                and any(c in ("floor", "wall") for c in el["cls"])]
    if len(draw_els) < 2:
        fail(27, "cannot find the lidar figure's floor and wall")
    else:
        ys = [el.get("y1") for el in draw_els if "y1" in el] + \
             [el.get("y2") for el in draw_els if "y2" in el]
        hgt = max(ys) - min(ys)
        if hgt < 32.0 - 0.01:
            fail(27, "the lidar figure is %.2f mm tall, below 32" % hgt)
        else:
            ok(27, "the lidar figure spans %.2f mm vertically" % hgt)
    # ladder arrows: mid-gap, at least 1.5 mm from the step and the next heading
    arrows = [el for el in doc["allGeo"] if "ladder-arrow" in el["cls"]
              and el["tag"] == "line"]
    ladder = {}
    for t in texts:
        if (t["block"] or "").startswith("ladder-") and \
                not (t["block"] or "").startswith("ladder-def"):
            ladder[int(t["block"].split("-")[1])] = t
    bad = []
    for el in arrows:
        mid = (el["x1"] + el["x2"]) / 2.0
        i = None
        for k in sorted(ladder):
            if ladder[k]["ax"] < mid:
                i = k
        if i is None or i + 1 not in ladder:
            bad.append("an arrow sits outside the ladder")
            continue
        left = ladder[i]["ax"] + ladder[i]["w"]
        right = ladder[i + 1]["ax"]
        if mid - left < 1.5 or right - (mid + 1.3) < 1.5:
            bad.append("arrow %d has %.2f/%.2f mm clearance"
                       % (i, mid - left, right - (mid + 1.3)))
    if bad:
        for b_ in bad[:4]:
            fail(27, b_)
    elif arrows:
        ok(27, "%d ladder arrows sit in the middle of their gaps, clear on both "
              "sides" % len(arrows))

    # 28 numbers keep their noun: the protected phrases of BRIEF 7.7 and 8.12
    protected = ["1 m squares", "15 cm", "10 cm", "3 s", "5 cm", "9 of 10",
                 "16 of 20", "14 of 20", "6 of 10", "20 trials", "20 trials "
                 "per task", "1 m square"]
    split = []
    for block, ts in by_block.items():
        ts = sorted(ts, key=lambda t: int(t["line"] or 0))
        words, where = [], []
        for t in ts:
            for w in norm(t["text"]).split(" "):
                if w:
                    words.append(w)
                    where.append(int(t["line"] or 0))
        joined = " ".join(words)
        for ph in protected:
            start = 0
            while True:
                i = joined.find(ph, start)
                if i < 0:
                    break
                start = i + 1
                a = len(joined[:i].split()) - 1 if i else -1
                n = len(ph.split())
                first = a + 1
                if where[first] != where[first + n - 1]:
                    split.append("%r is split across lines in %s"
                                 % (ph, block))
    if split:
        for s_ in sorted(set(split))[:6]:
            fail(28, s_)
    else:
        ok(28, "every protected number-and-noun phrase stays on one line "
              "(%d phrases)" % len(protected))

    # 19 the trained-policies return: exactly two heads, on the right nodes
    heads = [g for g in doc["allGeo"] if g["head"]]
    nodes = {g["nodeName"].replace("-", " "): g for g in doc["allGeo"]
             if g["cls"] and "node" in g["cls"] and g["nodeName"]}
    errs = []
    if len(heads) != 2:
        errs.append("%d arrowheads on the trained-policies return, expected 2"
                    % len(heads))
    for h in heads:
        v = [float(x) for x in h["points"].replace(",", " ").split()]
        tip = (v[0], v[1])
        nd = nodes.get((h["head"] or "").replace("-", " "))
        if nd is None:
            errs.append("head %r names no node" % h["head"])
            continue
        if abs(math.hypot(tip[0] - nd["cx"], tip[1] - nd["cy"]) - nd["r"]) > 0.02:
            errs.append("head %r does not terminate on its node" % h["head"])
        if abs(tip[0] - nd["cx"]) > 0.02 or tip[1] < nd["cy"]:
            errs.append("head %r does not point up into its node" % h["head"])
    if set(h["head"] for h in heads) != {"Robot Orin", "Station Orin"}:
        errs.append("the heads are on %s" % sorted(h["head"] for h in heads))
    ret = doc["geo"].get("ret-line")
    if ret is None:
        errs.append("no return line from DGX Spark")
    else:
        v = [float(x) for x in ret["d"].replace("M", " ").replace("L", " ")
             .split()]
        start = (v[0], v[1])
        if nodes.get("DGX Spark") and math.hypot(start[0] - nodes["DGX Spark"]["cx"],
                                                 start[1] - nodes["DGX Spark"]["cy"]) > 1.02:
            errs.append("the return line does not start at DGX Spark")
    if doc["geo"].get("ret-branch") is None:
        errs.append("the return has no branch")
    if errs:
        for e in errs:
            fail(19, e)
    else:
        ok(19, "one return line from DGX Spark, one branch, exactly two "
              "arrowheads on Station Orin and Robot Orin")

    # 20 band C panel bottoms on one baseline, clear of the footer
    last = {}
    pre = {"p1": ("p1-",), "p2": ("p2-",), "p3": ("rule-", "ladder-")}
    for t in texts:
        for p, keys in pre.items():
            if t["block"].startswith(keys) and not t["block"].endswith("-head"):
                last[p] = max(last.get(p, 0.0), t["y"] + t["h"])
    if len(last) != 3:
        fail(20, "cannot find the three band C panel bottoms")
    else:
        spread = max(last.values()) - min(last.values())
        if spread > 0.5:
            fail(20, "band C panel bottoms differ by %.2f mm: %s"
                 % (spread, {k: round(v, 2) for k, v in last.items()}))
        else:
            ok(20, "the three band C panels end within %.2f mm of each other"
               % spread)
    foot = [t for t in texts if t["block"].startswith("foot-")]
    if foot:
        top = min(t["y"] for t in foot)
        gap = top - max(last.values())
        if gap < 3.0:
            fail(20, "only %.2f mm between band C and the footer" % gap)
        else:
            ok(20, "%.2f mm of clear space between band C and the footer" % gap)

    # 21 band A body size
    bad_size = []
    for t in texts:
        b = t["block"]
        if b in ("a-lead",) or b.startswith("step-sent") or b.startswith("partmean-"):
            if abs(t["fs"] - 2.75) > 1e-3:
                bad_size.append((b, round(t["fs"], 3)))
    if bad_size:
        fail(21, "band A copy is not at body size: %s" % bad_size[:5])
    else:
        ok(21, "the lead, the pipeline sentences and the parts table are 2.75 mm")

    # 16 svg / html / png / strokes
    root = ET.parse(SVG).getroot()
    attrs = {"width": "420mm", "height": "297mm", "viewBox": "0 0 420 297"}
    bad = [k for k, v in attrs.items() if root.get(k) != v]
    ns = "{http://www.w3.org/2000/svg}"
    if root.find(ns + "title") is None or root.find(ns + "desc") is None:
        bad.append("title/desc")
    if bad:
        fail(16, "SVG header problems: %s" % bad)
    else:
        ok(16, "SVG is 420x297 mm with viewBox, title and desc")
    html = HTML.read_text(encoding="utf-8")
    if "@page" not in html or "A3 landscape" not in html or "margin: 0" not in html:
        fail(16, "HTML @page rule is missing or wrong")
    else:
        ok(16, "HTML declares @page { size: A3 landscape; margin: 0 }")
    pw, ph = png_size()
    if abs(pw / ph - 420.0 / 297.0) > 0.002 or abs(pw - 420 / 25.4 * 96 * 3) > 4:
        fail(16, "PNG is %dx%d, not a 3x A3 render" % (pw, ph))
    else:
        ok(16, "PNG is %d x %d px, 3x A3" % (pw, ph))
    bad_w = [w for w in doc["strokes"] if not any(abs(w - x) < 1e-6 for x in WEIGHTS)]
    if bad_w:
        fail(16, "stroke weights outside 0.25/0.5/0.8/1.6: %s" % bad_w)
    else:
        ok(16, "stroke weights used: %s"
           % ", ".join("%.2f" % w for w in doc["strokes"]))

    # 14 fonts and glyphs
    check_fonts()

    # 15 pdf and freshness
    check_pdf()

    # 18 clean build reproduces the deliverables byte for byte
    clean_build()

    print()
    if FAILS:
        print("FAILED %d check(s):" % len(FAILS))
        for f in FAILS:
            print("  -", f)
        sys.exit(1)
    print("all checks passed")


def png_size():
    d = PNG.read_bytes()
    if d[:8] != b"\x89PNG\r\n\x1a\n":
        return (0, 0)
    w, h = struct.unpack(">II", d[16:24])
    return (w, h)


# ---------------------------------------------------------------- check 10
def metro_line(doc, texts):
    ms = doc["metro"]
    if len(ms) < 2:
        fail(10, "metro line has %d segments" % len(ms))
        return
    errs = []
    for k, m in enumerate(ms):
        if m["seg"] != k:
            errs.append("segment order %s at %d" % (m["seg"], k))
        if abs(m["w"] - 1.6) > 1e-6:
            errs.append("segment %d is %.2f mm thick" % (k, m["w"]))
        want = PHASE_COL[[r[1] for r in brief_copy()["stage_table"] if r[0] == k + 1][0]]
        if m["stroke"] != want:
            errs.append("segment %d is %s, should be %s" % (k, m["stroke"], want))
    pts = [((m["pts"][0], m["pts"][1]), (m["pts"][-2], m["pts"][-1])) for m in ms]
    for k in range(1, len(pts)):
        (ax, ay), (bx, by) = pts[k - 1][1], pts[k][0]
        if math.hypot(ax - bx, ay - by) > 0.01:
            errs.append("gap %.2f mm between segments %d and %d"
                        % (math.hypot(ax - bx, ay - by), k - 1, k))
    discs = {int(d["n"]): d for d in doc["discs"]}
    s0, e0 = pts[0][0], pts[-1][1]
    if math.hypot(s0[0] - discs[0]["cx"], s0[1] - discs[0]["cy"]) > 0.01:
        errs.append("line does not start at station 0")
    if math.hypot(e0[0] - discs[10]["cx"], e0[1] - discs[10]["cy"]) > 0.01:
        errs.append("line does not end at station 10")
    # the return: chamfered channel at the right margin, back to station 6
    ret = [p for m in ms for p in [(m["pts"][i], m["pts"][i + 1])
                                   for i in range(0, len(m["pts"]), 2)]]
    seg5 = ms[5]["pts"]
    ys = [seg5[i] for i in range(1, len(seg5), 2)]
    if not (max(ys) > seg5[1] + 4):
        errs.append("the link leaving station 5 never leaves row 1")
    if max(seg5[0::2]) < 400:
        errs.append("the link from station 5 does not reach the right margin "
                    "channel (max x %.1f)" % max(seg5[0::2]))
    if min(seg5[0::2]) > 30:
        errs.append("the return does not run back across the page")
    if errs:
        for e in errs[:6]:
            fail(10, e)
    else:
        ok(10, "one continuous 1.6 mm line from station 0 to 10 on the right "
              "phase colours, with the return through the right margin channel")


# ---------------------------------------------------------------- check 11
def check_robot(doc, texts):
    g = doc["geo"]
    need = ["lidar-ray", "table-leg", "tabletop", "cup", "button", "panel",
            "lidar-puck", "joint", "cam-axis", "forearm", "floor", "wall",
            "wrist-bracket", "hit", "palm", "jaw", "cam-wrist",
            "cam-wrist-axis"]
    miss = [k for k in need if k not in g]
    if miss:
        fail(11, "tagged drawing geometry missing: %s" % miss)
        return
    errs, notes = [], []
    ray = g["lidar-ray"]
    plane_y = ray["y1"]
    leg = g["table-leg"]
    pts = [float(v) for v in g["cup"]["points"].replace(",", " ").split()]
    corners = list(zip(pts[0::2], pts[1::2]))
    ys = pts[1::2]
    cup_bottom = max(ys)
    cup_top = min(ys)
    cup_near = min(pts[0::2])
    top = g["tabletop"]
    if not cup_bottom <= top["y"] + 0.01:
        errs.append("the cup does not stand on the tabletop (%.2f vs %.2f)"
                    % (cup_bottom, top["y"]))
    if not cup_bottom < plane_y:
        errs.append("cup bottom %.2f is not above the plane %.2f"
                    % (cup_bottom, plane_y))
    if not top["y"] + top["height"] < plane_y:
        errs.append("tabletop is not above the plane")
    if not g["button"]["cy"] < plane_y:
        errs.append("button is not above the plane")
    if not (leg["y"] < plane_y < leg["y"] + leg["height"]):
        errs.append("table leg does not cross the plane")
    pan = g["panel"]
    if not (pan["y"] < plane_y < pan["y"] + pan["height"]):
        errs.append("button panel does not cross the plane")
    if abs(ray["x2"] - leg["x"]) > 0.01:
        errs.append("ray stops at %.2f, not at the leg face %.2f"
                    % (ray["x2"], leg["x"]))
    hit = g["hit"]
    if not (abs(hit["cx"] - leg["x"]) < 0.01 and abs(hit["cy"] - plane_y) < 0.01):
        errs.append("the hit mark is not on the leg face at the plane")
    puck = g["lidar-puck"]
    if abs(ray["x1"] - (puck["x"] + puck["width"])) > 0.01:
        errs.append("ray does not start at the puck")
    if not 0.5 < ray["x2"] - ray["x1"] < 40:
        errs.append("ray length %.2f mm is not a plausible scan"
                    % (ray["x2"] - ray["x1"]))
    if not (puck["y"] < plane_y < puck["y"] + puck["height"]):
        errs.append("the plane does not leave the middle of the puck")
    # floor stops at the wall
    fl, wl = g["floor"], g["wall"]
    if abs(fl["x2"] - wl["x1"]) > 0.01 or abs(fl["y1"] - wl["y2"]) > 0.01:
        errs.append("the floor line does not end on the wall")

    # every solid in the figure: filled or stroked rect, circle or polygon
    skip_ray = ("lidar-ray", "hit", "cam-axis", "cam-wrist-axis", "lidar-puck",
                "stn-disc", "stn-ring", "node", "joint", "hub", "button",
                "bullet", "swatch", "seg", "ret-head")
    solids = []
    for el in doc["allGeo"]:
        if el["tag"] not in ("rect", "circle", "polygon"):
            continue
        if any(c in skip_ray for c in el["cls"]):
            continue
        if el["tag"] == "circle":
            bx, by = el["cx"], el["cy"]
        elif el["tag"] == "rect":
            bx, by = el["x"], el["y"]
        else:
            v = [float(q) for q in el["points"].replace(",", " ").split()]
            bx, by = min(v[0::2]), min(v[1::2])
        ink = el["fill"] not in ("none", "#FFFFFF") or el["sw"] > 0
        if ink and bx > 160 and by > 225:      # inside the lidar figure
            solids.append(el)
    n = max(4, int((ray["x2"] - ray["x1"]) / 0.2))
    for k in range(1, n):
        x = ray["x1"] + (ray["x2"] - ray["x1"]) * k / n
        for el in solids:
            if inside(el, x, plane_y):
                errs.append("the ray passes through %s at x %.1f"
                            % ("/".join(el["cls"]), x))
                break

    # the wrist camera sits on a short vertical stem under the wrist housing
    br, cam, palm = g["wrist-bracket"], g["cam-wrist"], g["palm"]
    if abs(br["x1"] - br["x2"]) > 0.01:
        errs.append("the wrist camera bracket is not vertical")
    if abs(max(br["y1"], br["y2"]) - cam["y"]) > 0.01:
        errs.append("the wrist camera bracket does not touch the camera")
    bar = g["carriage"]
    if abs(min(br["y1"], br["y2"]) - (bar["y"] + bar["height"])) > 0.01:
        errs.append("the wrist camera bracket does not reach the finger "
                    "carriage")

    ns = "{http://www.w3.org/2000/svg}"
    joints = {}
    for el in ET.parse(SVG).getroot().iter(ns + "circle"):
        if "joint" in (el.get("class") or "").split():
            joints[el.get("data-joint")] = (float(el.get("cx")),
                                            float(el.get("cy")))
    if len(joints) != 6:
        errs.append("%d joint marks, expected 6" % len(joints))
        ang = 0.0
    else:
        S, E, W = joints["shoulder"], joints["elbow"], joints["wrist1"]
        a = (S[0] - E[0], S[1] - E[1])
        b = (W[0] - E[0], W[1] - E[1])
        c = (a[0] * b[0] + a[1] * b[1]) / (math.hypot(*a) * math.hypot(*b))
        ang = math.degrees(math.acos(max(-1.0, min(1.0, c))))
        if not 120 <= ang <= 150:
            errs.append("elbow angle %.1f deg is outside 120-150" % ang)
        if not E[1] < S[1]:
            errs.append("the elbow is not above the shoulder")
        reach = (math.hypot(S[0] - E[0], S[1] - E[1])
                 + math.hypot(W[0] - E[0], W[1] - E[1]))
        cup_d = min(math.hypot(x - S[0], y - S[1]) for (x, y) in corners)
        if cup_d > reach + 0.01:
            errs.append("the cup is %.2f mm from the shoulder, beyond the "
                        "arm's %.2f mm reach" % (cup_d, reach))
        else:
            notes.append("cup %.2f mm inside reach %.2f (%.0f%%)"
                         % (cup_d, reach, 100.0 * (1 - cup_d / reach)))
    # head camera: above the cup's top, axis on the cup, clear line of sight
    cam = g["cam-axis"]
    lens = (cam["x1"], cam["y1"])
    ca = math.atan2(cam["y2"] - cam["y1"], cam["x2"] - cam["x1"])
    if not lens[1] < cup_top:
        errs.append("the head camera lens is not above the cup's top")
    for (x, y) in corners + [((cup_near + max(pts[0::2])) / 2.0,
                              (cup_top + cup_bottom) / 2.0)]:
        ta = math.atan2(y - lens[1], x - lens[0])
        dd = math.degrees(abs((ta - ca + math.pi) % (2 * math.pi) - math.pi))
        if dd > 30:
            errs.append("head camera axis is %.1f deg from the cup" % dd)
            break
    # sightlines.  The wrist camera looks into the gripper's opening, so its
    # line to the cup is short and must be clear.  The head camera stands on a
    # mast behind the arm: its drawn axis is tested clear, and the cup must lie
    # inside the axis's 30 degree cone (tested above).
    targets = [(cup_near, cup_top + f * (cup_bottom - cup_top))
               for f in (0.3, 0.45, 0.6)]
    wl_ = g["cam-wrist-axis"]

    def clear_line(lx, ly, tx, ty):
        steps = max(6, int(math.hypot(tx - lx, ty - ly) / 0.2))
        for k in range(1, steps):
            px = lx + (tx - lx) * k / steps
            py = ly + (ty - ly) * k / steps
            for el in solids:
                if "cup" in el["cls"] or "lens" in el["cls"]:
                    continue
                if inside(el, px, py):
                    return False
        return True

    clear = sum(1 for (tx, ty) in targets
                if clear_line(wl_["x1"], wl_["y1"], tx, ty))
    if clear < 3:
        errs.append("the wrist camera has no clear view of the cup (%d of 3 "
                    "sightlines)" % clear)
    else:
        notes.append("wrist camera sees the cup on %d of 3 sightlines" % clear)
    if not clear_line(cam["x1"], cam["y1"], cam["x2"], cam["y2"]):
        errs.append("the head camera's axis is drawn through a solid")
    else:
        notes.append("head camera axis clear over its drawn length")
    if errs:
        for e in errs[:8]:
            fail(11, e)
    else:
        ok(11, "six joints, elbow %.1f deg, cup %.2f mm inside the reach, "
              "cup/table/button above the plane, leg and panel cross it, hit "
              "mark on the leg, ray crosses no solid, wrist camera on its stem, "
              "floor trimmed at the wall, both cameras and the axis on the cup"
           % (ang, cup_d))
        for s in notes:
            print("       %s" % s)


# ---------------------------------------------------------------- check 14
def check_fonts():
    faces = load_faces()
    root = ET.parse(SVG).getroot()
    uses = svg_chars_by_family(root)
    missing = []
    for (s, fam) in uses:
        f = "Menlo-Regular" if fam == "mono" else "AvenirNext-Regular"
        cps = faces.get(f)
        if cps is None:
            missing.append("%s font not found" % f)
            continue
        for ch in s:
            if ord(ch) > 127 and ord(ch) not in cps:
                missing.append("%s missing U+%04X" % (f, ord(ch)))
    if missing:
        fail(14, "glyph coverage: %s" % sorted(set(missing))[:6])
    else:
        ok(14, "every non-ASCII glyph exists in the font it is set in")
    if not PDF.exists():
        fail(14, "no PDF to inspect")
        return
    out = subprocess.run(["pdffonts", str(PDF)], capture_output=True,
                         text=True).stdout
    fams = set()
    for line in out.splitlines()[2:]:
        if line.strip():
            fams.add(line.split()[0].split("+")[-1])
    allowed = {"AvenirNext-Regular", "AvenirNext-DemiBold", "Menlo-Regular"}
    if not fams:
        fail(14, "pdffonts reported no fonts")
    elif fams - allowed:
        fail(14, "unexpected font families in the PDF: %s" % sorted(fams - allowed))
    else:
        ok(14, "pdffonts shows only %s" % ", ".join(sorted(fams)))


# ---------------------------------------------------------------- check 15
def check_pdf():
    if not PDF.exists():
        fail(15, "lerobot-roadmap.pdf is missing")
        return
    raw = PDF.read_bytes()
    boxes = re.findall(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]",
                       raw)
    pages = len(re.findall(rb"/Type\s*/Page[^s]", raw))
    a3w, a3h = 420 * 72 / 25.4, 297 * 72 / 25.4
    if not boxes:
        fail(15, "no /MediaBox in the PDF")
        return
    w = float(boxes[0][2]) - float(boxes[0][0])
    h = float(boxes[0][3]) - float(boxes[0][1])
    if pages != 1:
        fail(15, "PDF has %d pages, expected 1" % pages)
    elif not (abs(w - a3w) < 2 and abs(h - a3h) < 2):
        fail(15, "PDF page is %.1f x %.1f pt, not A3 landscape" % (w, h))
    else:
        ok(15, "PDF is one page, %.1f x %.1f pt (A3 landscape)" % (w, h))
    ops = 0
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        chunk = m.group(1)
        try:
            data = zlib.decompress(chunk)
        except Exception:
            data = chunk
        ops += len(re.findall(rb"\bT[Jj]\b", data))
    if b"/Font" not in raw or ops < 200:
        fail(15, "PDF text is not selectable (%d text ops)" % ops)
    else:
        ok(15, "PDF text is selectable (%d text operations)" % ops)
    newest = max((SRC / n).stat().st_mtime for n in
                 ("content.py", "build_map.py"))
    stale = [p.name for p in (SVG, HTML, PDF, PNG)
             if not p.exists() or p.stat().st_mtime < newest - 0.001]
    if stale:
        fail(15, "outputs older than the sources: %s" % stale)
    else:
        ok(15, "SVG, HTML, PDF and PNG are all newer than the source files")


# ---------------------------------------------------------------- check 18
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def clean_build():
    d = Path(tempfile.mkdtemp(prefix="lerobot-clean-"))
    try:
        (d / "src").mkdir()
        for f in ("content.py", "build_map.py"):
            shutil.copy2(SRC / f, d / "src" / f)
        shutil.copy2(BRIEF, d / "BRIEF.md")
        r = subprocess.run([sys.executable, str(d / "src" / "build_map.py")],
                           cwd=str(d), capture_output=True, text=True)
        if r.returncode:
            fail(18, "the clean build failed: %s" % r.stderr[-300:])
            return
        bad = []
        for name in ("lerobot-roadmap.svg", "lerobot-roadmap.html",
                     "lerobot-roadmap.png"):
            a, b = sha(ROOT / name), sha(d / name)
            if a != b:
                bad.append("%s %s != %s" % (name, a[:12], b[:12]))
        if bad:
            for s in bad:
                fail(18, "a clean copy does not reproduce %s" % s)
        else:
            ok(18, "a clean copy of src/ and BRIEF.md reproduces the SVG, HTML "
                  "and PNG byte for byte")
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()
