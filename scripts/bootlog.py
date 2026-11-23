#!/usr/bin/env python3
"""Boot-log profile card: the profile starts up like a Spring Boot application.

  python scripts/bootlog.py      -> boot.svg

An EDUARDO block banner, then log lines appear one after another (stack,
brokers, datasources, deploy targets, tests, a coffee WARN), a monthly
contributions chart printed by "GitActivityMonitor", and the classic
"Started EduardoApplication ..." line with a blinking cursor.

Numbers come from data/contributions.json (written by fetch_contributions.py);
the date in the banner/version follows the day it was generated.
To change what the log says, edit the `logs` list in build().
"""
import pyfiglet
import datetime
import json
import os

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

_D = json.load(open(os.environ.get("CONTRIB_JSON", "data/contributions.json")))
DAYS = _D["days"]
_S = _D["stats"]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def months12():
    """[(label 'nov', 'YYYY-MM', count)] for the last 12 calendar months (current one partial)."""
    m = _S["months"]
    keys = sorted(m)[-12:]
    out = []
    for k in keys:
        dt = datetime.date.fromisoformat(k + "-01")
        out.append((dt.strftime("%b").lower(), k, m[k]))
    return out


def stats():
    bd = _S["best_day"]
    m = _S["months"]
    bm = max(m, key=m.get)
    return {
        "total": _S["total"],
        "longest": _S["longest_streak"],
        "current": _S.get("current_streak", 0),
        "best_count": bd["count"],
        "best_date": bd["date"],
        "best_short": datetime.date.fromisoformat(bd["date"]).strftime("%b %-d"),
        "busiest_month": datetime.date.fromisoformat(bm + "-01").strftime("%B"),
        "busiest_count": m[bm],
        "first": DAYS[0]["date"],
        "last": DAYS[-1]["date"],
        "active_days": sum(1 for d in DAYS if d["count"] > 0),
    }


def today():
    return datetime.date.fromisoformat(DAYS[-1]["date"]) + datetime.timedelta(days=1)


def fade(inner, begin, dur=0.35):
    return (f'<g opacity="0">{inner}<animate attributeName="opacity" from="0" to="1" '
            f'dur="{dur}s" begin="{begin:.2f}s" fill="freeze"/></g>')



BG = "#1e1f22"
BAR = "#2b2d30"
LINE = "#393b40"
TXT = "#bcbec4"
DIM = "#6f737a"
GREEN = "#6aab73"
YELLOW = "#e0c46c"
PURPLE = "#c77dbb"
CYAN = "#56a8f5"
ORANGE = "#cf8e6d"
WHITE = "#dfe1e5"

W = 860
FS = 11.5
CW = FS * 0.6          # monospace advance
LH = 19


def log_line(y, ts, level, logger, msg_parts):
    lvl_col = {"INFO": GREEN, "WARN": YELLOW}[level]
    msg = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for t, c in msg_parts)
    return (f'<text x="20" y="{y}" font-family="{MONO}" font-size="{FS}" xml:space="preserve">'
            f'<tspan fill="{DIM}">{ts}</tspan>  <tspan fill="{lvl_col}">{level:>4}</tspan>  '
            f'<tspan fill="{CYAN}">{logger:<22}</tspan><tspan fill="{DIM}">: </tspan>{msg}</text>')


def block_banner(text, x0, y0, cw=8, ch=13, col="#6aab73", shadow="#3b6b42"):
    """Draw figlet ansi_shadow art as crisp rects (full blocks) and lines (box-drawing shadow)."""
    rows = [r for r in pyfiglet.figlet_format(text, font="ansi_shadow").split("\n") if r.strip()]
    out = []
    # segments per box char, as (dx1,dy1,dx2,dy2) in units of half-cells from the cell's centre
    segs = {
        "═": [(-1, -.25, 1, -.25), (-1, .25, 1, .25)],
        "║": [(-.25, -1, -.25, 1), (.25, -1, .25, 1)],
        "╗": [(-1, -.25, .25, -.25), (-1, .25, -.25, .25), (.25, -.25, .25, 1), (-.25, .25, -.25, 1)],
        "╔": [(1, -.25, -.25, -.25), (1, .25, .25, .25), (-.25, -.25, -.25, 1), (.25, .25, .25, 1)],
        "╝": [(-1, .25, .25, .25), (-1, -.25, -.25, -.25), (.25, .25, .25, -1), (-.25, -.25, -.25, -1)],
        "╚": [(1, .25, -.25, .25), (1, -.25, .25, -.25), (-.25, .25, -.25, -1), (.25, -.25, .25, -1)],
    }
    blocks, lines = [], []
    for r, row in enumerate(rows):
        for c, chr_ in enumerate(row):
            x, y = x0 + c * cw, y0 + r * ch
            if chr_ == "█":
                blocks.append(f"M{x} {y}h{cw}v{ch}h-{cw}z")
            elif chr_ in segs:
                cx, cy = x + cw / 2, y + ch / 2
                for a, b, c2, d in segs[chr_]:
                    lines.append(f"M{cx+a*cw/2:.1f} {cy+b*ch/2:.1f}L{cx+c2*cw/2:.1f} {cy+d*ch/2:.1f}")
    out.append(f'<path d="{"".join(lines)}" stroke="{shadow}" stroke-width="1.2" fill="none"/>')
    out.append(f'<path d="{"".join(blocks)}" fill="{col}"/>')
    return "".join(out), len(rows) * ch, max(len(r) for r in rows) * cw


def build():
    s = stats()
    d = today()
    date = d.isoformat()
    banner_svg, banner_h, banner_w = block_banner("eduardo", 20, 0)

    lines = []   # (kind, payload)
    t = [0.0]

    def ts():
        t[0] += 0.137
        sec = 1 + t[0]
        return f"08:17:{int(sec):02d}.{int((sec % 1) * 1000):03d}"

    W_ = lambda txt: (txt, TXT)
    H_ = lambda txt: (txt, WHITE)
    logs = [
        ("INFO", "e.t.EduardoApplication", [W_("Starting EduardoApplication v"), H_(f"{d:%Y.%m}"),
                                            W_(" · São Paulo, BR · PID 1337")]),
        ("INFO", "e.t.EduardoApplication", [W_('No active profile set, falling back to: "'),
                                            ("software-engineer", ORANGE), W_('"')]),
        ("INFO", "o.s.b.w.Employment", [W_("Current employer: "), H_("Itaú Unibanco"),
                                        W_("  (previously: NTT DATA)")]),
        ("INFO", "o.s.b.a.Runtime", [W_("Loaded runtimes: "), H_("Java · Spring Boot · Node.js · TypeScript")]),
        ("INFO", "o.a.k.c.EventBus", [W_("Connected to brokers "), H_("[kafka, rabbitmq]"),
                                      W_(" — event-driven mode "), ("ON", GREEN)]),
        ("INFO", "com.zaxxer.HikariPool", [W_("Start completed. datasources="),
                                           H_("[postgresql, mysql, mongodb, redis]")]),
        ("INFO", "o.s.c.k.Deploy", [W_("Targets ready: "), H_("docker · kubernetes · aws · azure"), W_(" via CI/CD")]),
        ("INFO", "o.j.p.TestEngine", [W_("JUnit 5 · Mockito · Testcontainers → "), ("0 failures", GREEN)]),
        ("WARN", "c.b.CoffeeMonitor", [("Caffeine below recommended threshold. Proceeding anyway.", YELLOW)]),
        ("INFO", "g.h.GitActivityMonitor", [W_("Contributions (12 mo): "), H_(f"{s['total']:,}"),
                                            W_(" · longest streak "), H_(f"{s['longest']}d"),
                                            W_(" · best day "), H_(f"{s['best_count']}")]),
    ]

    p = []
    # --- layout
    y = 30 + 20           # after title bar
    banner_top = y
    y += banner_h + 8
    tagline_y = y + 4
    y += 30
    log_top = y
    y += len(logs) * LH
    chart_top = y + 6
    chart_h = 72
    y = chart_top + chart_h + 34
    started_y = y
    H = started_y + 34

    p.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    p.append(f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>')
    p.append(f'<path d="M0 10a10 10 0 0 1 10-10h{W-20}a10 10 0 0 1 10 10v20H0z" fill="{BAR}"/>')
    p.append(f'<line x1="0" y1="30" x2="{W}" y2="30" stroke="{LINE}"/>')
    p.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="none" stroke="{LINE}"/>')
    # run toolbar: green play, title, stop square
    p.append(f'<path d="M18 9l9 6-9 6z" fill="{GREEN}"/>')
    p.append(f'<text x="36" y="19.5" font-family="{MONO}" font-size="11.5" fill="{TXT}">Run: '
             f'<tspan fill="{WHITE}">EduardoApplication</tspan></text>')
    p.append(f'<rect x="{W-28}" y="10" width="10" height="10" rx="1.5" fill="#db5c5c" opacity=".85"/>')
    p.append(f'<text x="{W-40}" y="19.5" font-family="{MONO}" font-size="11" fill="{DIM}" text-anchor="end">'
             'java -jar eduardo-toste.jar</text>')

    # banner: wipes in left to right
    p.append(f'<defs><clipPath id="wipe"><rect x="0" y="-2" width="0" height="{banner_h+4}">'
             f'<animate attributeName="width" from="0" to="{W}" dur=".9s" fill="freeze"/></rect></clipPath></defs>')
    p.append(f'<g clip-path="url(#wipe)" transform="translate(0 {banner_top})">{banner_svg}</g>')
    p.append(f'<text x="{20+banner_w+18}" y="{banner_top+banner_h-6}" font-family="{MONO}" font-size="11" fill="{DIM}">'
             f'.toste</text>')
    p.append(fade(f'<text x="20" y="{tagline_y}" font-family="{MONO}" font-size="{FS}" xml:space="preserve">'
                  f'<tspan fill="{GREEN}"> :: Eduardo Toste ::</tspan><tspan fill="{DIM}">   software engineer · '
                  f'distributed systems · event-driven · clean architecture</tspan>'
                  f'<tspan fill="{DIM}">   (v{d:%Y.%m})</tspan></text>', 0.45))

    begin = 0.8
    for i, (lvl, logger, parts) in enumerate(logs):
        p.append(fade(log_line(log_top + i * LH, ts(), lvl, logger, parts), begin + i * 0.22, 0.15))

    # monthly activity chart, printed as part of the log
    cb = begin + len(logs) * 0.22 + 0.1
    m = months12()
    mx = max(c for _, _, c in m) or 1
    cx0 = 20 + 52 * CW / 1.0
    bw, gap = 26, 10
    base = chart_top + chart_h - 14
    chart = [""]
    for i, (lab, key, c) in enumerate(m):
        h = max(2, (chart_h - 30) * c / mx)
        x = 20 + 54 * CW + i * (bw + gap)
        col = WHITE if c == mx else CYAN
        chart.append(f'<rect x="{x:.1f}" y="{base-h:.1f}" width="{bw}" height="{h:.1f}" rx="2" fill="{col}" opacity=".9">'
                     f'<animate attributeName="height" from="0" to="{h:.1f}" dur=".5s" begin="{cb+i*0.04:.2f}s" fill="freeze"/>'
                     f'<animate attributeName="y" from="{base}" to="{base-h:.1f}" dur=".5s" begin="{cb+i*0.04:.2f}s" fill="freeze"/></rect>')
        chart.append(f'<text x="{x+bw/2:.1f}" y="{base+13}" font-family="{MONO}" font-size="10" fill="{DIM}" text-anchor="middle">{lab}</text>')
        chart.append(f'<text x="{x+bw/2:.1f}" y="{base-h-4:.1f}" font-family="{MONO}" font-size="9.5" '
                     f'fill="{WHITE if c == mx else DIM}" text-anchor="middle">{c}</text>')
    chart_label = (f'<text x="20" y="{chart_top+26}" font-family="{MONO}" font-size="{FS}" fill="{DIM}">'
                   f'monthly contributions ↗</text>'
                   f'<text x="20" y="{chart_top+44}" font-family="{MONO}" font-size="{FS}" fill="{DIM}">'
                   f'peak: <tspan fill="{WHITE}">{s["busiest_month"].lower()} ({s["busiest_count"]})</tspan></text>')
    p.append(fade(chart_label + "".join(chart[1:]), cb, 0.3))

    sb = cb + 0.9
    p.append(fade(log_line(started_y - 22, ts(), "INFO", "e.t.EduardoApplication",
                           [W_("Tomcat started on port 8080 · "), ("open to new ideas & good conversations", ORANGE)]), sb, 0.15))
    p.append(fade(log_line(started_y - 3, ts(), "INFO", "e.t.EduardoApplication",
                           [("Started EduardoApplication in 2.026 seconds", GREEN), W_(" (JVM running since FACENS)")]), sb + 0.25, 0.15))
    cursor_x = 20
    p.append(fade(f'<text x="{cursor_x}" y="{started_y+18}" font-family="{MONO}" font-size="{FS}" fill="{GREEN}">❯</text>'
                  f'<rect x="{cursor_x+14}" y="{started_y+8}" width="7" height="13" fill="{WHITE}">'
                  '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.51;1" dur="1s" repeatCount="indefinite"/></rect>',
                  sb + 0.5, 0.1))
    p.append("</svg>")
    return p




if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "boot.svg"
    open(out, "w", encoding="utf-8").write("\n".join(build()))
    print("[bootlog] wrote", out)
