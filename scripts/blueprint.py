#!/usr/bin/env python3
"""Blueprint profile art: the profile drawn as a system-architecture diagram.

  python scripts/blueprint.py hero      -> hero.svg
      Eduardo as the central service (halftone portrait from source-prepped.png),
      wired to company / runtime / messaging / data / platform nodes, with
      packets travelling along the edges and acks coming back.
      Edit the texts in NODES / FOOTER below.

  python scripts/blueprint.py contrib   -> contrib-heatmap.svg
      Weekly contributions curve + daily heatmap, from data/contributions.json
      (written by fetch_contributions.py).
"""

import datetime
import math
import json

import numpy as np
from PIL import Image

DATA_PATH = "data/contributions.json"
PHOTO = "source-prepped.png"
_DATA = None


def data():
    global _DATA
    if _DATA is None:
        _DATA = json.load(open(DATA_PATH))
    return _DATA

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
SERIF = "Georgia,'Times New Roman',Times,serif"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def weeks():
    """Days grouped into Sunday-first columns; last 53 columns."""
    days = data()["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    pad = (first.weekday() + 1) % 7
    cells = [None] * pad + days
    cols = [cells[i:i + 7] for i in range(0, len(cells), 7)]
    return cols[-53:]


def week_totals(cols):
    return [sum(d["count"] for d in c if d) for c in cols]


def month_starts(cols):
    """[(col_index, 'nov'), ...] for the first column containing a month's 1st..7th."""
    out, seen = [], set()
    for i, c in enumerate(cols):
        for d in c:
            if not d:
                continue
            dt = datetime.date.fromisoformat(d["date"])
            key = (dt.year, dt.month)
            if dt.day <= 7 and key not in seen:
                seen.add(key)
                out.append((i, dt.strftime("%b").lower()))
                break
    # drop a label squeezed into the first two columns
    return [m for m in out if m[0] >= 2 or len(out) == 1]


CROP = (95, 0, 615, 520)   # head + phone + upper chest of the 700x700 prepped photo


def darkness_grid(n: int, lo: float = 0.10, hi: float = 0.85, gamma: float = 1.3) -> np.ndarray:
    """n x n array, 0 = background/white, 1 = darkest (contrast-stretched)."""
    im = Image.open(PHOTO).convert("L").crop(CROP).resize((n, n), Image.LANCZOS)
    a = 1.0 - np.asarray(im, dtype=float) / 255.0
    bg = a < 0.04
    a = np.clip((a - lo) / (hi - lo), 0, 1) ** gamma
    a[bg] = 0.0
    return a


def stats():
    D = data()
    s = D["stats"]
    months = s["months"]
    bm = max(months, key=months.get)
    bm_name = datetime.date.fromisoformat(bm + "-01").strftime("%B")
    bd = s["best_day"]
    bd_dt = datetime.date.fromisoformat(bd["date"])
    first = D["days"][0]["date"]
    last = D["days"][-1]["date"]
    return {
        "total": s["total"],
        "longest": s["longest_streak"],
        "best_count": bd["count"],
        "best_date": bd["date"],
        "best_short": bd_dt.strftime("%-d %b"),
        "busiest_month": bm_name,
        "busiest_count": months[bm],
        "range": (first, last),
    }


def smooth_path(pts, ymin=None, ymax=None):
    """Catmull-Rom -> cubic bezier path through pts (control points clamped)."""
    ys = [p[1] for p in pts]
    ymin = min(ys) if ymin is None else ymin
    ymax = max(ys) if ymax is None else ymax
    cl = lambda y: max(ymin, min(ymax, y))
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, cl(p1[1] + (p2[1] - p0[1]) / 6))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, cl(p2[1] - (p3[1] - p1[1]) / 6))
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d



BG = "#0a1424"
MINOR = "#10213b"
MAJOR = "#163056"
LINE = "#2a5b96"
NODE = "#0d1b31"
INK = "#7fd3ff"
TXT = "#e6f1ff"
MUT = "#6f8fb8"
ACK = "#5af78e"
ACCENTS = ["#7fd3ff", "#5af78e", "#ffb86b", "#c3a6ff", "#ff7a90"]
# --- texts (edit here) ---------------------------------------------------
NODES = [
    # (label, value, tag)
    ("COMPANY", "Itaú Unibanco · São Paulo, BR", "fintech"),
    ("RUNTIME", "Java · Spring Boot · Node.js · TypeScript", "jvm"),
    ("MESSAGING", "Kafka · RabbitMQ · event-driven", "async"),
    ("DATA", "PostgreSQL · MongoDB · Redis · MySQL", "sql/nosql"),
    ("PLATFORM", "Docker · Kubernetes · AWS · Azure", "ci/cd"),
]
FOOTER = ("Software Engineer · Itaú Unibanco", "FACENS — Systems Analysis & Dev.")
# -------------------------------------------------------------------------

RAMP = ["#11223b", "#0f3d66", "#1767a3", "#2f9ad8", "#7fd3ff"]


def grid_defs():
    return (
        '<pattern id="g20" width="20" height="20" patternUnits="userSpaceOnUse">'
        f'<path d="M20 0H0V20" fill="none" stroke="{MINOR}" stroke-width="1"/></pattern>'
        '<pattern id="g100" width="100" height="100" patternUnits="userSpaceOnUse">'
        f'<path d="M100 0H0V100" fill="none" stroke="{MAJOR}" stroke-width="1"/></pattern>'
        '<filter id="glow" x="-200%" y="-200%" width="500%" height="500%">'
        '<feGaussianBlur stdDeviation="2.2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
    )


def frame(W, H, title_l, title_r):
    return [
        f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
        f'<rect width="{W}" height="{H}" rx="10" fill="url(#g20)"/>',
        f'<rect width="{W}" height="{H}" rx="10" fill="url(#g100)"/>',
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{MAJOR}"/>',
        f'<text x="24" y="30" font-family="{MONO}" font-size="12" fill="{MUT}">'
        f'<tspan fill="{INK}">◆</tspan> {title_l}</text>',
        f'<text x="{W-24}" y="30" font-family="{MONO}" font-size="12" fill="{MUT}" text-anchor="end">{title_r}</text>',
    ]


def hero():
    W, H = 860, 440
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f"<defs>{grid_defs()}</defs>"]
    p += frame(W, H, f'topology <tspan fill="{TXT}">eduardo-toste</tspan>', "region: sa-east-1 · São Paulo")

    # --- central service node with halftone portrait
    nx, ny, nw, nh = 24, 48, 300, 372
    p.append(f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="10" fill="{NODE}" stroke="{LINE}"/>')
    p.append(f'<text x="{nx+16}" y="{ny+20}" font-family="{MONO}" font-size="12" fill="{TXT}">svc/eduardo-toste</text>')
    p.append(f'<circle cx="{nx+nw-38}" cy="{ny+16}" r="4" fill="{ACK}">'
             '<animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>')
    p.append(f'<text x="{nx+nw-16}" y="{ny+20}" font-family="{MONO}" font-size="11" fill="{ACK}" text-anchor="end">UP</text>')
    p.append(f'<line x1="{nx}" y1="{ny+30}" x2="{nx+nw}" y2="{ny+30}" stroke="{LINE}" stroke-opacity=".7"/>')

    n, cell = 50, 6
    g = darkness_grid(n)
    ox, oy = nx, ny + 30
    for r in range(n):
        dots = []
        for c in range(n):
            v = g[r, c]
            if v <= 0:
                continue
            rad = cell / 2 * math.sqrt(v) * 1.08
            if rad < 0.45:
                continue
            dots.append(f'<circle cx="{ox+(c+.5)*cell:.1f}" cy="{oy+(r+.5)*cell:.1f}" r="{rad:.2f}"/>')
        if dots:
            p.append(f'<g fill="{INK}" opacity="0">{"".join(dots)}'
                     f'<animate attributeName="opacity" from="0" to="1" dur=".35s" begin="{r*0.022:.3f}s" fill="freeze"/></g>')

    fy = ny + 30 + n * cell
    p.append(f'<line x1="{nx}" y1="{fy}" x2="{nx+nw}" y2="{fy}" stroke="{LINE}" stroke-opacity=".7"/>')
    p.append(f'<text x="{nx+16}" y="{fy+19}" font-family="{SANS}" font-size="13" font-weight="600" fill="{TXT}">'
             f'{esc(FOOTER[0])}</text>')
    p.append(f'<text x="{nx+16}" y="{fy+35}" font-family="{MONO}" font-size="10.5" fill="{MUT}">'
             f'{esc(FOOTER[1])}</text>')

    # --- dependency nodes
    nodes = NODES
    rx, rw, rh = 474, 362, 58
    gap = (nh - len(nodes) * rh) / (len(nodes) - 1)
    for i, (lab, val, tag) in enumerate(nodes):
        y = ny + i * (rh + gap)
        yc = y + rh / 2
        col = ACCENTS[i]
        sy = ny + 92 + i * 52
        path = f"M{nx+nw} {sy} C{nx+nw+80} {sy} {rx-80} {yc} {rx} {yc}"
        p.append(f'<path d="{path}" fill="none" stroke="{LINE}" stroke-width="1.3" stroke-dasharray="4 4"/>')
        p.append(f'<circle cx="{nx+nw}" cy="{sy}" r="3.2" fill="{BG}" stroke="{LINE}" stroke-width="1.3"/>')
        p.append(f'<circle cx="{rx}" cy="{yc:.1f}" r="3.2" fill="{BG}" stroke="{col}" stroke-width="1.3"/>')
        # request packet
        p.append(f'<circle r="2.8" fill="{col}" filter="url(#glow)" opacity="0">'
                 f'<set attributeName="opacity" to="1" begin="{1.2+i*0.35:.2f}s"/>'
                 f'<animateMotion dur="2.6s" begin="{1.2+i*0.35:.2f}s" repeatCount="indefinite" path="{path}"/></circle>')
        # ack coming back
        p.append(f'<circle r="1.8" fill="#ffffff" opacity="0">'
                 f'<set attributeName="opacity" to=".75" begin="{2.5+i*0.35:.2f}s"/>'
                 f'<animateMotion dur="2.6s" begin="{2.5+i*0.35:.2f}s" repeatCount="indefinite" '
                 f'keyPoints="1;0" keyTimes="0;1" calcMode="linear" path="{path}"/></circle>')
        # node box
        p.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur=".4s" '
                 f'begin="{0.5+i*0.12:.2f}s" fill="freeze"/>'
                 f'<rect x="{rx}" y="{y:.1f}" width="{rw}" height="{rh}" rx="8" fill="{NODE}" stroke="{LINE}"/>'
                 f'<rect x="{rx}" y="{y+10:.1f}" width="3" height="{rh-20}" rx="1.5" fill="{col}"/>'
                 f'<text x="{rx+18}" y="{y+22:.1f}" font-family="{MONO}" font-size="10" letter-spacing="1.6" fill="{MUT}">{lab}</text>'
                 f'<text x="{rx+rw-14}" y="{y+22:.1f}" font-family="{MONO}" font-size="10" fill="{col}" text-anchor="end">{tag}</text>'
                 f'<text x="{rx+18}" y="{y+43:.1f}" font-family="{SANS}" font-size="14" fill="{TXT}">{esc(val)}</text></g>')
    p.append("</svg>")
    return p


def contrib():
    W, H = 860, 304
    cols = weeks()
    tot = week_totals(cols)
    s = stats()
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<defs>{grid_defs()}<linearGradient id="area" x1="0" y1="0" x2="0" y2="1">'
         f'<stop offset="0" stop-color="{INK}" stop-opacity=".35"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/>'
         '</linearGradient></defs>']
    p += frame(W, H, f'metrics <tspan fill="{TXT}">contributions_total</tspan>{{user="eduardo"}}',
               f'<tspan fill="{INK}">{s["total"]:,}</tspan> events · 12 mo')

    step = 14
    x0 = (W - 53 * step) / 2
    cx = [x0 + i * step + 5.5 for i in range(len(cols))]
    top, ch = 52, 84
    mx = max(tot) or 1
    pts = [(cx[i], top + ch - ch * t / mx) for i, t in enumerate(tot)]
    line = smooth_path(pts)
    for k in (0, .5, 1):
        y = top + ch - ch * k
        p.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+53*step-3}" y2="{y:.1f}" stroke="{LINE}" stroke-opacity=".35" stroke-dasharray="2 4"/>')
        p.append(f'<text x="{x0+53*step+4}" y="{y+3.5:.1f}" font-family="{MONO}" font-size="9.5" fill="{MUT}">{round(mx*k)}</text>')
    p.append(f'<path d="{line} L{pts[-1][0]:.1f} {top+ch} L{pts[0][0]:.1f} {top+ch}Z" fill="url(#area)" opacity="0">'
             '<animate attributeName="opacity" from="0" to="1" dur=".8s" begin="1.2s" fill="freeze"/></path>')
    p.append(f'<path d="{line}" fill="none" stroke="{INK}" stroke-width="1.8" filter="url(#glow)" '
             'pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
             '<animate attributeName="stroke-dashoffset" from="1" to="0" dur="1.8s" fill="freeze"/></path>')
    p.append(f'<circle r="3" fill="#fff" filter="url(#glow)" opacity="0"><set attributeName="opacity" to="1" begin="1.8s"/>'
             f'<animateMotion dur="7s" begin="1.8s" repeatCount="indefinite" path="{line}"/></circle>')

    hy = 156
    for i, c in enumerate(cols):
        cells = []
        for r, d in enumerate(c):
            if not d:
                continue
            cells.append(f'<rect x="{x0+i*step:.1f}" y="{hy+r*step}" width="11" height="11" rx="2" fill="{RAMP[d["level"]]}"/>')
        p.append(f'<g opacity="0">{"".join(cells)}<animate attributeName="opacity" from="0" to="1" dur=".3s" '
                 f'begin="{0.2+i*0.02:.2f}s" fill="freeze"/></g>')
    for i, m in month_starts(cols):
        p.append(f'<text x="{x0+i*step:.1f}" y="{hy+7*step+14}" font-family="{MONO}" font-size="10" fill="{MUT}">{m}</text>')
    fy = H - 16
    p.append(f'<text x="{x0}" y="{fy}" font-family="{MONO}" font-size="11" fill="{MUT}" xml:space="preserve">'
             f'longest streak <tspan fill="{TXT}">{s["longest"]}d</tspan>   ·   best day <tspan fill="{TXT}">{s["best_count"]}</tspan> '
             f'({s["best_date"]})   ·   busiest month <tspan fill="{TXT}">{s["busiest_month"].lower()} ({s["busiest_count"]})</tspan></text>')
    lx = x0 + 53 * step - 3
    leg = "".join(f'<rect x="{lx-5*14+k*14+3:.1f}" y="{fy-10}" width="11" height="11" rx="2" fill="{RAMP[k]}"/>' for k in range(5))
    p.append(leg)
    p.append("</svg>")
    return p




def _write(path, parts):
    open(path, "w", encoding="utf-8").write("\n".join(parts))
    print("[blueprint] wrote", path)


if __name__ == "__main__":
    import sys
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("hero", "all"):
        _write("hero.svg", hero())
    if what in ("contrib", "all"):
        _write("contrib-heatmap.svg", contrib())
