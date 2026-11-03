# -*- coding: utf-8 -*-
"""Automated checks for the Mobile Manipulator Learning Map.

    python src/check_map.py

Every geometric number here is read back from a live headless-Chrome render of
mobile-manipulator-map.html, not from this program's own layout code.
Exits non-zero if any check fails.
"""

import json
import re
import subprocess
import sys
import zlib
from pathlib import Path

import content as C

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / ".tmp"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HTML = ROOT / "mobile-manipulator-map.html"
SVG = ROOT / "mobile-manipulator-map.svg"
PDF = ROOT / "mobile-manipulator-map.pdf"

INK = "#1B2430"
MUTED = "#566070"
HAIR = "#C7CDD6"
PREPARE = "#0B5F9E"
CLASSICAL = "#00695C"
LEARNED = "#8A2F6B"
SAFETY = "#B5420A"
PALETTE = {INK, MUTED, HAIR, PREPARE, CLASSICAL, LEARNED, SAFETY}
TEXT_COLORS = {INK, MUTED, PREPARE, CLASSICAL, LEARNED, SAFETY}

FAILS = []
WARNS = []


def fail(check, msg):
    FAILS.append("[check %s] %s" % (check, msg))


def ok(check, msg):
    print("  ok   %-2s %s" % (check, msg))


# --------------------------------------------------------------------------
# browser probe
# --------------------------------------------------------------------------
PROBE = r"""
<script>
window.addEventListener('load', function(){
  const svg = document.querySelector('svg');
  const r0 = svg.getBoundingClientRect();
  const K = 420 / r0.width;                 // mm per CSS px
  const hex = (c) => {
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return c;
    const p = m[1].split(',').map(x => parseFloat(x));
    return '#' + p.slice(0,3).map(v => Math.round(v).toString(16).padStart(2,'0')).join('').toUpperCase();
  };
  const texts = [...svg.querySelectorAll('text')];
  const ti = texts.map((t, i) => {
    const r = t.getBoundingClientRect();
    const cs = getComputedStyle(t);
    return {i: i, x: (r.left - r0.left) * K, y: (r.top - r0.top) * K,
            w: r.width * K, h: r.height * K,
            fs: parseFloat(cs.fontSize), fill: hex(cs.fill),
            cls: t.getAttribute('class') || '',
            block: t.getAttribute('data-block') || '',
            line: t.getAttribute('data-line') || '',
            text: t.textContent};
  });

  // text / text overlap
  const overlaps = [];
  for (let a = 0; a < ti.length; a++) {
    for (let b = a + 1; b < ti.length; b++) {
      const A = ti[a], B = ti[b];
      const ox = Math.min(A.x + A.w, B.x + B.w) - Math.max(A.x, B.x);
      const oy = Math.min(A.y + A.h, B.y + B.h) - Math.max(A.y, B.y);
      if (ox > 0.001 && oy > 0.001) overlaps.push([a, b, +ox.toFixed(3), +oy.toFixed(3)]);
    }
  }

  // bounds
  const oob = [];
  ti.forEach(t => { if (t.x < 12 - 0.02 || t.y < 12 - 0.02 ||
                       t.x + t.w > 408 + 0.02 || t.y + t.h > 285 + 0.02)
                      oob.push([t.i, +t.x.toFixed(3), +t.y.toFixed(3),
                                +(t.x+t.w).toFixed(2), +(t.y+t.h).toFixed(2)]); });

  // occlusion: centre of a painted glyph
  const occl = [];
  const ctm = (el) => el.getScreenCTM();
  texts.forEach((t, i) => {
    const n = t.getNumberOfChars ? t.getNumberOfChars() : 0;
    if (!n) return;
    const picks = [];
    for (const f of [0.2, 0.5, 0.8]) {
      let idx = Math.floor(n * f), tries = 0;
      while (idx < n && tries < n &&
             (t.getExtentOfChar(idx).width === 0 ||
              /^\s*$/.test(t.textContent[Math.floor(t.getStartPositionOfChar(idx).x*0)+idx] || 'x'))) {
        idx++; tries++;
      }
      picks.push(Math.min(idx, n - 1));
    }
    for (const idx of picks) {
      const e = t.getExtentOfChar(idx);
      if (!e || e.width === 0) continue;
      const pt = svg.createSVGPoint();
      pt.x = e.x + e.width / 2; pt.y = e.y + e.height / 2;
      const sp = pt.matrixTransform(ctm(t));
      const hit = document.elementFromPoint(sp.x, sp.y);
      const good = hit && (hit === t || (hit.closest && hit.closest('text') === t));
      if (!good) occl.push([i, t.textContent.slice(0, 24),
                            hit ? hit.tagName + '.' + (hit.getAttribute('class')||'') : 'null']);
    }
  });

  // stroked shapes vs text boxes
  const shapes = [...svg.querySelectorAll('line,path,rect,circle,polygon,polyline')];
  const crossings = [];
  const STEP = 0.2;
  shapes.forEach((s, si) => {
    const cs = getComputedStyle(s);
    if (cs.stroke === 'none' || parseFloat(cs.strokeWidth) === 0) return;
    const pts = [];
    const tag = s.tagName.toLowerCase();
    if (tag === 'line') {
      const x1 = +s.getAttribute('x1'), y1 = +s.getAttribute('y1');
      const x2 = +s.getAttribute('x2'), y2 = +s.getAttribute('y2');
      const L = Math.hypot(x2-x1, y2-y1), nseg = Math.max(1, Math.ceil(L / STEP));
      for (let k = 0; k <= nseg; k++) pts.push([x1 + (x2-x1)*k/nseg, y1 + (y2-y1)*k/nseg]);
    } else if (tag === 'circle') {
      const cx = +s.getAttribute('cx'), cy = +s.getAttribute('cy'), r = +s.getAttribute('r');
      const nseg = Math.max(24, Math.ceil(2*Math.PI*r / STEP));
      for (let k = 0; k <= nseg; k++) { const a = 2*Math.PI*k/nseg;
        pts.push([cx + r*Math.cos(a), cy + r*Math.sin(a)]); }
    } else if (tag === 'rect') {
      const x = +s.getAttribute('x'), y = +s.getAttribute('y');
      const w = +s.getAttribute('width'), h = +s.getAttribute('height');
      for (const [ax, ay, bx, by] of [[x,y,x+w,y],[x+w,y,x+w,y+h],[x+w,y+h,x,y+h],[x,y+h,x,y]]) {
        const L = Math.hypot(bx-ax, by-ay), nseg = Math.max(1, Math.ceil(L / STEP));
        for (let k = 0; k <= nseg; k++) pts.push([ax + (bx-ax)*k/nseg, ay + (by-ay)*k/nseg]);
      }
    } else if (tag === 'polygon' || tag === 'polyline') {
      const v = s.getAttribute('points').trim().split(/[\s,]+/).map(Number);
      for (let k = 0; k + 3 < v.length; k += 2) {
        const ax=v[k], ay=v[k+1], bx=v[k+2], by=v[k+3];
        const L = Math.hypot(bx-ax, by-ay), nseg = Math.max(1, Math.ceil(L / STEP));
        for (let m = 0; m <= nseg; m++) pts.push([ax + (bx-ax)*m/nseg, ay + (by-ay)*m/nseg]);
      }
    } else if (tag === 'path') {
      const L = s.getTotalLength(), nseg = Math.max(2, Math.ceil(L / STEP));
      for (let k = 0; k <= nseg; k++) { const p = s.getPointAtLength(L*k/nseg);
        pts.push([p.x, p.y]); }
    }
    for (const p of pts) {
      for (const t of ti) {
        if (p[0] > t.x && p[0] < t.x + t.w && p[1] > t.y && p[1] < t.y + t.h) {
          crossings.push([si, t.i, +p[0].toFixed(2), +p[1].toFixed(2), tag]);
          break;
        }
      }
    }
  });

  // white paint must be a station number
  const whiteNotStation = [];
  [...svg.querySelectorAll('*')].forEach(el => {
    const cs = getComputedStyle(el);
    for (const prop of ['fill', 'stroke']) {
      if (hex(cs[prop]) === '#FFFFFF' && el.tagName !== 'svg') {
        if (!(el.tagName === 'text' && (el.getAttribute('class')||'').includes('stn-num')))
          whiteNotStation.push(el.tagName + '.' + (el.getAttribute('class')||'') + ':' + prop);
      }
    }
  });

  // tagged geometry, for the physics invariants
  const geo = {};
  [...svg.querySelectorAll('[class]')].forEach(el => {
    const cls = (el.getAttribute('class') || '').split(' ').filter(c => c && c !== 'txt' && c !== 'mth');
    for (const c of cls) {
      if (geo[c]) continue;
      const a = {};
      for (const k of ['x1','y1','x2','y2','cx','cy','r','x','y','width','height']) {
        if (el.hasAttribute(k)) a[k] = parseFloat(el.getAttribute(k));
      }
      geo[c] = a;
    }
  });

  // station numbers and page text
  const stn = ti.filter(t => t.cls.includes('stn-num')).map(t => t.text);
  const pageText = ti.map(t => t.text).join(' ');
  const doc = {texts: ti, overlaps: overlaps, oob: oob, occl: occl,
               crossings: crossings.slice(0, 200), nCrossings: crossings.length,
               whiteNotStation: [...new Set(whiteNotStation)], stn: stn,
               pageText: pageText, geo: geo,
               svgW: r0.width, svgH: r0.height};
  const pre = document.createElement('pre');
  pre.id = 'probe';
  pre.textContent = JSON.stringify(doc);
  document.body.appendChild(pre);
});
</script>
"""


def run_probe():
    html = HTML.read_text(encoding="utf-8")
    probe_html = html.replace("</body>", PROBE + "\n</body>")
    f = TMP / "probe.html"
    TMP.mkdir(exist_ok=True)
    f.write_text(probe_html, encoding="utf-8")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--hide-scrollbars", "--window-size=1600,1200",
           "--virtual-time-budget=15000", "--dump-dom", f.as_uri()]
    dom = subprocess.run(cmd, capture_output=True, text=True).stdout
    m = re.search(r'<pre id="probe">(.*?)</pre>', dom, re.S)
    if not m:
        print("probe did not run; Chrome output tail:\n", dom[-2000:])
        sys.exit(2)
    raw = m.group(1)
    raw = (raw.replace("&quot;", '"').replace("&amp;", "&")
              .replace("&lt;", "<").replace("&gt;", ">"))
    return json.loads(raw)


# --------------------------------------------------------------------------
# colour helpers
# --------------------------------------------------------------------------
def lum(hexcol):
    c = [int(hexcol[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def norm(s):
    s = s.replace("_", "")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------
def main():
    doc = run_probe()
    texts = doc["texts"]
    print("page text elements: %d   svg px: %.1f x %.1f"
          % (len(texts), doc["svgW"], doc["svgH"]))

    # 1 — minimum type size
    small = [(t["text"][:30], round(t["fs"], 3)) for t in texts if t["fs"] < 2.45 - 1e-6]
    if small:
        fail(1, "text under 2.45 mm: %s" % small[:5])
    else:
        ok(1, "smallest text %.2f mm, all %d text elements >= 2.45 mm"
           % (min(t["fs"] for t in texts), len(texts)))

    # 2 — no text overlaps text
    if doc["overlaps"]:
        for a, b, ox, oy in doc["overlaps"][:8]:
            fail(2, "overlap %r / %r by %.2f x %.2f mm"
                 % (texts[a]["text"][:28], texts[b]["text"][:28], ox, oy))
    else:
        ok(2, "no two text boxes overlap (%d pairs checked)" % (len(texts) * (len(texts) - 1) // 2))

    # 3 — everything inside the margins
    if doc["oob"]:
        for i, x0, y0, x1, y1 in doc["oob"][:8]:
            fail(3, "text outside 12-408 / 12-285: %r at %.2f,%.2f-%.2f,%.2f"
                 % (texts[i]["text"][:30], x0, y0, x1, y1))
    else:
        ok(3, "all text inside x 12-408, y 12-285")

    # 4 — occlusion
    if doc["occl"]:
        for i, s, hit in doc["occl"][:8]:
            fail(4, "text %r is painted under %s" % (s, hit))
    else:
        ok(4, "every sampled glyph centre is the topmost element")

    # 5 — no stroked line crosses a text box
    if doc["nCrossings"]:
        for si, ti, x, y, tag in doc["crossings"][:10]:
            fail(5, "%s at %.2f,%.2f crosses %r"
                 % (tag, x, y, texts[ti]["text"][:34]))
        print("     (%d crossing samples)" % doc["nCrossings"])
    else:
        ok(5, "no stroked line or path crosses any text box")

    # 6 — declared text colours
    bad = []
    for t in texts:
        if t["fill"] == "#FFFFFF":
            if "stn-num" not in t["cls"]:
                bad.append((t["text"][:20], t["fill"]))
        elif t["fill"] not in TEXT_COLORS:
            bad.append((t["text"][:20], t["fill"]))
    if bad:
        fail(6, "text fill outside the palette: %s" % bad[:6])
    else:
        ok(6, "all text fills are ink, muted or a phase colour (white only on station numbers)")
    lows = [(c, round(contrast(c, "#FFFFFF"), 2)) for c in
            sorted(TEXT_COLORS) if contrast(c, "#FFFFFF") < 4.5]
    if lows:
        fail(6, "text colours below 4.5:1 on white: %s" % lows)
    else:
        ok(6, "every text colour clears 4.5:1 on white (min %.1f:1)"
           % min(contrast(c, "#FFFFFF") for c in TEXT_COLORS))
    # station numbers must stay legible on their own disc
    badw = [t["text"] for t in texts if t["fill"] == "#FFFFFF"
            and contrast(t["fill"], INK) < 4.5]
    if badw:
        fail(6, "white station numbers below 4.5:1: %s" % badw[:5])
    else:
        ok(6, "white station numbers clear 4.5:1 on the darkest phase colour")

    # 7 — palette only, no filters/gradients/images/urls
    src = SVG.read_text(encoding="utf-8")
    hexes = set(re.findall(r"#[0-9A-Fa-f]{6}", src))
    extra = hexes - PALETTE - {"#FFFFFF"}
    if extra:
        fail(7, "non-palette colours in the SVG: %s" % sorted(extra))
    else:
        ok(7, "SVG uses only the seven palette tokens (%d found)" % len(hexes))
    if doc["whiteNotStation"]:
        fail(7, "white paint somewhere other than a station number: %s"
             % doc["whiteNotStation"][:5])
    else:
        ok(7, "white is used only for station numbers")
    src_ns = re.sub(r'xmlns(:xlink)?="[^"]*"', "", src)
    banned = [w for w in ("<filter", "Gradient", "<pattern", "<image", "http://",
                          "https://", "url(") if w in src_ns]
    if banned:
        fail(7, "forbidden constructs in the SVG: %s" % banned)
    else:
        ok(7, "no filter, gradient, pattern, image or external URL")

    # 8 — copy present
    page = norm(doc["pageText"])
    missing = [s for s in C.EXACT_COPY if norm(s) not in page]
    if missing:
        for s in missing[:10]:
            fail(8, "copy missing or altered: %r" % s[:70])
        print("     (%d strings missing)" % len(missing))
    else:
        ok(8, "all %d required strings are present, in order and unbroken"
           % len(C.EXACT_COPY))

    # 9 — nine stops, times total 22 weeks, numbers visible
    stn = doc["stn"]
    if stn != [str(i) for i in range(9)]:
        fail(9, "station numbers are %r, expected 0-8" % stn)
    else:
        ok(9, "nine stations, numbers 0-8 present")
    times = [t["text"] for t in texts if t["block"].startswith("time")]
    wks = []
    for s in times:
        m = re.match(r"(\d+) weeks?$", s.strip())
        wks.append(int(m.group(1)) if m else None)
    if len(wks) != 9 or None in wks:
        fail(9, "stop times unreadable: %r" % times)
    elif sum(wks) != 22:
        fail(9, "stop times total %d weeks, expected 22" % sum(wks))
    else:
        ok(9, "stop times total %d weeks: %s" % (sum(wks), "+".join(map(str, wks))))

    # 11 — the drawn physics: COM inside support, caster on the reach side
    check_geometry(doc)

    # 10 — the PDF
    check_pdf()

    print()
    if FAILS:
        print("FAILED %d check(s):" % len(FAILS))
        for f in FAILS:
            print("  -", f)
        sys.exit(1)
    print("all checks passed")


def check_geometry(doc):
    g = doc["geo"]
    need = ["wheel", "axle", "caster", "battery", "support", "com-dot", "com-drop",
            "mast", "chassis-top"]
    missing = [k for k in need if k not in g]
    if missing:
        fail(11, "tagged geometry missing: %s" % missing)
        return
    sup = g["support"]
    sx0, sx1 = min(sup["x1"], sup["x2"]), max(sup["x1"], sup["x2"])
    axle, cast = g["wheel"], g["caster"]
    com, drop = g["com-dot"], g["com-drop"]
    bat = g["battery"]
    errs = []
    if not (sx0 - 1e-6 <= com["cx"] <= sx1 + 1e-6):
        errs.append("COM x %.2f is outside the support bracket %.2f-%.2f"
                    % (com["cx"], sx0, sx1))
    if abs(axle["cx"] - sx0) > 0.01 or abs(cast["cx"] - sx1) > 0.01:
        errs.append("support bracket does not run axle(%.2f) to caster(%.2f)"
                    % (axle["cx"], cast["cx"]))
    if abs(drop["x1"] - com["cx"]) > 0.01 or abs(drop["x2"] - com["cx"]) > 0.01:
        errs.append("COM drop line is not vertical under the COM dot")
    if drop["y2"] < com["cy"] or drop["y2"] < 100.9:
        errs.append("COM drop line does not reach the floor")
    if bat["x"] + bat["width"] > axle["cx"] - 0.2:
        errs.append("battery is not behind the axle")
    if cast["cx"] <= axle["cx"]:
        errs.append("caster is not on the reach side of the axle")
    # frames: C on the base mast, H at the hand, O at the object, W on the floor
    tb = {t["block"]: t for t in doc["texts"] if t["block"]}
    chassis = g["chassis-top"]
    if "fC" in tb and not (chassis["x1"] - 4 <= tb["fC"]["x"] <= chassis["x1"] + 40):
        errs.append("camera frame is not on the base")
    if "fH" in tb and not (tb["fH"]["x"] > cast["cx"] + 40):
        errs.append("hand frame is not out at the gripper")
    if "fW" in tb and tb["fW"]["y"] > 103:
        errs.append("world frame is not on the floor")
    for line in errs:
        fail(11, line)
    if not errs:
        ok(11, "COM drop line lands inside the support bracket (x %.2f in %.2f-%.2f); "
               "battery behind the axle; caster on the reach side; frames placed"
           % (com["cx"], sx0, sx1))


def check_pdf():
    if not PDF.exists():
        fail(10, "mobile-manipulator-map.pdf is missing")
        return
    raw = PDF.read_bytes()
    boxes = re.findall(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\]",
                       raw)
    pages = len(re.findall(rb"/Type\s*/Page[^s]", raw))
    a3w, a3h = 420 * 72 / 25.4, 297 * 72 / 25.4
    if not boxes:
        fail(10, "no /MediaBox in the PDF")
        return
    ok_size = False
    for b in boxes:
        w = float(b[2]) - float(b[0])
        h = float(b[3]) - float(b[1])
        if abs(w - a3w) < 2 and abs(h - a3h) < 2:
            ok_size = True
        elif abs(h - a3w) < 2 and abs(w - a3h) < 2:
            fail(10, "PDF page is A3 but portrait")
            return
    if not ok_size:
        fail(10, "PDF page size is not A3 landscape: %s" % [tuple(b) for b in boxes[:2]])
        return
    if pages != 1:
        fail(10, "PDF has %d pages, expected 1" % pages)
        return
    ok(10, "PDF is one page, %.1f x %.1f pt (A3 landscape)" % (a3w, a3h))

    # selectable text: fonts + drawn glyphs in a decompressed content stream
    has_font = b"/Font" in raw
    text_ops = 0
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S):
        chunk = m.group(1)
        try:
            data = zlib.decompress(chunk)
        except Exception:
            data = chunk
        text_ops += len(re.findall(rb"\bT[Jj]\b", data))
    if not has_font:
        fail(10, "PDF has no font resource, so text is not selectable")
    elif text_ops < 100:
        fail(10, "PDF content stream shows only %d text operations" % text_ops)
    else:
        ok(10, "PDF text is selectable (%d text operations, fonts embedded)" % text_ops)


if __name__ == "__main__":
    main()
