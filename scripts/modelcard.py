#!/usr/bin/env python3
"""Model-card profile: Eduardo documented the way AI models are.

  python scripts/modelcard.py [out.svg] [dark|light]     (default: modelcard.svg, dark)

Name + tags, then a two-column grid of cards: model description, training
data (education and jobs), evaluation results (real GitHub activity from
data/contributions.json, written by fetch_contributions.py), capabilities,
example outputs (projects), intended use and how to reach me.
Colours are taken from the profile picture (misty teal, sage, rust cloak).
To change any text, edit it directly in build().
"""
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



MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
THEMES = {
    # matched to the profile picture: misty teal field, sage grass, rust-coloured cloak
    "light": dict(BG="#f6f8f7", CARD="#eef3f1", CARD_LINE="#d8e2de", INK="#15201f", MUT="#5b6b66",
                  LINE="#dbe4e0", VIOLET="#2f6f66", VSOFT="#dcebe6", VSTROKE="#a9c9bf", GREEN="#2f7d5b",
                  GREEN_BG="#dcefe5", TRACK="#d9e3df", WARM="#a4522c", OUTER="#d8e2de", TAG="#eef3f1",
                  ICON_BG="#dcebe6"),
    "dark": dict(BG="#111819", CARD="#172123", CARD_LINE="#253336", INK="#e8efec", MUT="#93a59e",
                 LINE="#253336", VIOLET="#8fc1ae", VSOFT="#1d302d", VSTROKE="#3d5c55", GREEN="#7fd1a8",
                 GREEN_BG="#16302a", TRACK="#26363a", WARM="#d98b5f", OUTER="#2a393c", TAG="#172123",
                 ICON_BG="#1d302d"),
}
T = dict(THEMES["light"])

W = 880
PAD = 24
GAP = 14
COLS = 3
CW = (W - 2 * PAD - (COLS - 1) * GAP) / COLS   # card width (three columns)
IN = 18                                        # inner padding
XS = [PAD + i * (CW + GAP) for i in range(COLS)]


def card(x, y, w, h, title=None, note=None):
    s = f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="12" fill="{T["CARD"]}" stroke="{T["CARD_LINE"]}"/>'
    if title:
        s += (f'<text x="{x+IN:.1f}" y="{y+32}" font-family="{SANS}" font-size="15.5" font-weight="800" '
              f'fill="{T["INK"]}">{esc(title)}</text>')
    if note:
        s += (f'<text x="{x+w-IN:.1f}" y="{y+32}" font-family="{SANS}" font-size="12" fill="{T["MUT"]}" '
              f'text-anchor="end">{esc(note)}</text>')
    return s


def txt(x, y, t, size=14.5, col=None, weight=400, anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{SANS}" font-size="{size}" font-weight="{weight}" '
            f'fill="{col or T["INK"]}" text-anchor="{anchor}">{t}</text>')


def build():
    s = stats()
    y_tags = 96
    r1, r1_h = 144, 150
    r2 = r1 + r1_h + GAP
    r2_h = 176
    r3 = r2 + r2_h + GAP
    r3_h = 106
    H = r3 + r3_h + PAD

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" rx="16" fill="{T["BG"]}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{T["OUTER"]}"/>']

    # ---- header: kicker + name on the left, status on the right, tags across
    p.append(f'<text x="{PAD}" y="40" font-family="{SANS}" font-size="12" font-weight="800" letter-spacing="2" fill="{T["WARM"]}">MODEL CARD</text>')
    p.append(f'<text x="{PAD}" y="77" font-family="{MONO}" font-size="30" font-weight="700" fill="{T["INK"]}">'
             f'eduardo-toste<tspan fill="{T["MUT"]}">/</tspan><tspan fill="{T["WARM"]}">v2026</tspan></text>')
    p.append(f'<rect x="{W-PAD-132}" y="34" width="132" height="32" rx="16" fill="{T["GREEN_BG"]}"/>'
             f'<circle cx="{W-PAD-112}" cy="50" r="5" fill="{T["GREEN"]}"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle>'
             f'<text x="{W-PAD-98}" y="55.5" font-family="{SANS}" font-size="14.5" font-weight="800" fill="{T["GREEN"]}">Deployed</text>')
    tags = ["Software & AI Engineer", "Backend", "Distributed systems", "AI products", "São Paulo · BR"]
    widths = [len(t) * 7.5 + 26 for t in tags]
    extra = (W - 2 * PAD - sum(widths) - 8 * (len(tags) - 1)) / len(tags)
    tx = PAD
    for i, (t, w) in enumerate(zip(tags, widths)):
        w += extra
        hl = i == 0
        p.append(f'<rect x="{tx:.1f}" y="{y_tags}" width="{w:.1f}" height="30" rx="8" '
                 f'fill="{T["VSOFT"] if hl else T["TAG"]}" stroke="{T["VSTROKE"] if hl else T["CARD_LINE"]}"/>'
                 f'<text x="{tx+w/2:.1f}" y="{y_tags+20}" font-family="{SANS}" font-size="13.5" font-weight="700" '
                 f'fill="{T["VIOLET"] if hl else T["INK"]}" text-anchor="middle">{esc(t)}</text>')
        tx += w + 8

    # ---- row 1: description | training data | intended use
    x = XS[0]
    p.append(card(x, r1, CW, r1_h, "Model description"))
    for i, l in enumerate(["Trained on Java, Spring Boot and", "distributed systems. Fine-tuned",
                           "to build AI-powered products that", "work in the real world."]):
        p.append(txt(x + IN, r1 + 60 + i * 22, esc(l)))

    x = XS[1]
    p.append(card(x, r1, CW, r1_h, "Training data"))
    steps = [("FACENS", "education"), ("NTT DATA", "previous role"), ("Itaú Unibanco", "current role")]
    for i, (a, b) in enumerate(steps):
        y = r1 + 66 + i * 28
        cur = i == len(steps) - 1
        p.append(f'<circle cx="{x+IN+6:.1f}" cy="{y-5}" r="6" fill="{T["VIOLET"] if cur else T["VSTROKE"]}"/>')
        if not cur:
            p.append(f'<line x1="{x+IN+6:.1f}" y1="{y+1}" x2="{x+IN+6:.1f}" y2="{y+17}" stroke="{T["VSTROKE"]}" stroke-width="2"/>')
        p.append(txt(x + IN + 22, y, f'<tspan font-weight="800">{esc(a)}</tspan><tspan fill="{T["MUT"]}">  ·  {esc(b)}</tspan>'))

    x = XS[2]
    p.append(card(x, r1, CW, r1_h, "Intended use"))
    for i, l in enumerate(["Teams building reliable backend", "systems and AI-powered products:",
                           "APIs, event-driven services and", "integrations that scale."]):
        p.append(txt(x + IN, r1 + 60 + i * 22, esc(l)))

    # ---- row 2: capabilities | example outputs | model architecture
    x = XS[0]
    p.append(card(x, r2, CW, r2_h, "Capabilities"))
    for i, c in enumerate(["Backend systems and APIs", "Event-driven microservices",
                           "AI inside real products", "Tests and CI/CD built in"]):
        p.append(txt(x + IN, r2 + 64 + i * 27, f'<tspan fill="{T["GREEN"]}" font-weight="800">✓</tspan>  {esc(c)}'))

    x = XS[1]
    p.append(card(x, r2, CW, r2_h, "Example outputs"))
    outs = [("Lista.ai", "AI shopping lists"), ("NextMove", "finance platform"),
            ("FightHub", "Jiu-Jitsu academies"), ("PayTracker", "expense tracker")]
    for i, (n, d) in enumerate(outs):
        p.append(fade(txt(x + IN, r2 + 64 + i * 27,
                          f'<tspan font-weight="800" fill="{T["VIOLET"]}">{n}</tspan>  <tspan fill="{T["MUT"]}">{esc(d)}</tspan>'),
                      0.6 + i * 0.12, 0.3))

    x = XS[2]
    p.append(card(x, r2, CW, r2_h, "Model architecture"))
    stack = ["Java", "Spring Boot", "Kafka", "RabbitMQ", "PostgreSQL", "MongoDB", "Redis",
             "Docker", "Kubernetes", "AWS · Azure", "AI integration"]
    cx, cy = x + IN, r2 + 46
    for i, t in enumerate(stack):
        w = len(t) * 6.6 + 17
        if cx + w > x + CW - IN + 0.5:
            cx, cy = x + IN, cy + 30
        hl = t == "AI integration"
        p.append(fade(f'<rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="25" rx="7" '
                      f'fill="{T["VSOFT"] if hl else T["BG"]}" stroke="{T["VSTROKE"] if hl else T["CARD_LINE"]}"/>'
                      f'<text x="{cx+w/2:.1f}" y="{cy+17}" font-family="{SANS}" font-size="12.5" font-weight="700" '
                      f'fill="{T["VIOLET"] if hl else T["INK"]}" text-anchor="middle">{esc(t)}</text>', 0.8 + i * 0.05, 0.25))
        cx += w + 5

    # ---- row 3: evaluation results, four metric tiles across the full width
    full = W - 2 * PAD
    p.append(card(PAD, r3, full, r3_h, "Evaluation results", "GitHub · last 12 months"))
    evals = [("Contributions", f'{s["total"]:,}', min(1, s["total"] / 1500)),
             ("Active days", f'{s["active_days"]} / 365', s["active_days"] / 365),
             ("Longest streak", f'{s["longest"]} days', min(1, s["longest"] / 60)),
             ("Best single day", f'{s["best_count"]}', min(1, s["best_count"] / 50))]
    tw = (full - 2 * IN - 3 * 28) / 4
    for i, (k, v, f) in enumerate(evals):
        tx = PAD + IN + i * (tw + 28)
        p.append(txt(tx, r3 + 66, esc(k), 13.5, T["MUT"], 600))
        p.append(txt(tx + tw, r3 + 66, esc(v), 17, T["VIOLET"], 800, "end"))
        p.append(f'<rect x="{tx:.1f}" y="{r3+78}" width="{tw:.1f}" height="8" rx="4" fill="{T["TRACK"]}"/>')
        p.append(f'<rect x="{tx:.1f}" y="{r3+78}" width="0" height="8" rx="4" fill="{T["VIOLET"]}">'
                 f'<animate attributeName="width" from="0" to="{tw*f:.1f}" dur="1.2s" begin="{0.3+i*0.2:.1f}s" fill="freeze" '
                 'calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>')
    p.append("</svg>")
    return p


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "modelcard.svg"
    T.update(THEMES[sys.argv[2] if len(sys.argv) > 2 else "dark"])
    open(out, "w", encoding="utf-8").write("\n".join(build()))
    print("[modelcard] wrote", out)
