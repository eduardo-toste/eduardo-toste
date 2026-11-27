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

W = 860
PAD = 28
GAP = 16
CW = (W - 2 * PAD - GAP) / 2          # card width (two columns)
IN = 22                               # inner padding
LX, RX = PAD, PAD + CW + GAP


def card(x, y, w, h, title=None, note=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{T["CARD"]}" stroke="{T["CARD_LINE"]}"/>'
    if title:
        s += (f'<text x="{x+IN}" y="{y+36}" font-family="{SANS}" font-size="16.5" font-weight="800" '
              f'fill="{T["INK"]}">{esc(title)}</text>')
    if note:
        s += (f'<text x="{x+w-IN}" y="{y+36}" font-family="{SANS}" font-size="12.5" fill="{T["MUT"]}" '
              f'text-anchor="end">{esc(note)}</text>')
    return s


def txt(x, y, t, size=15.5, col=None, weight=400, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" font-weight="{weight}" '
            f'fill="{col or T["INK"]}" text-anchor="{anchor}">{t}</text>')


def build():
    s = stats()
    # ---- vertical rhythm
    y_tags = 102
    r1 = 152                      # row 1 top
    desc_h, train_h = 160, 162
    r1_h = desc_h + GAP + train_h  # left stack == evaluation card height
    r2 = r1 + r1_h + GAP
    r2_h = 176
    r3 = r2 + r2_h + GAP
    r3_h = 160
    H = r3 + r3_h + PAD

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" rx="16" fill="{T["BG"]}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{T["OUTER"]}"/>']

    # ---- header
    p.append(f'<text x="{PAD}" y="44" font-family="{SANS}" font-size="12.5" font-weight="800" letter-spacing="2" fill="{T["WARM"]}">MODEL CARD</text>')
    p.append(f'<text x="{PAD}" y="84" font-family="{MONO}" font-size="31" font-weight="700" fill="{T["INK"]}">'
             f'eduardo-toste<tspan fill="{T["MUT"]}">/</tspan><tspan fill="{T["WARM"]}">v2026</tspan></text>')
    p.append(f'<rect x="{W-PAD-136}" y="28" width="136" height="32" rx="16" fill="{T["GREEN_BG"]}"/>'
             f'<circle cx="{W-PAD-116}" cy="44" r="5" fill="{T["GREEN"]}"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle>'
             f'<text x="{W-PAD-102}" y="49.5" font-family="{SANS}" font-size="14.5" font-weight="800" fill="{T["GREEN"]}">Deployed</text>')
    tags = ["Software & AI Engineer", "Backend", "Distributed systems", "AI products", "São Paulo · BR"]
    widths = [len(t) * 7.7 + 26 for t in tags]
    extra = (W - 2 * PAD - sum(widths) - 8 * (len(tags) - 1)) / len(tags)   # stretch tags to full width
    tx = PAD
    for i, (t, w) in enumerate(zip(tags, widths)):
        w += extra
        hl = i == 0
        p.append(f'<rect x="{tx:.1f}" y="{y_tags}" width="{w:.1f}" height="30" rx="8" '
                 f'fill="{T["VSOFT"] if hl else T["TAG"]}" stroke="{T["VSTROKE"] if hl else T["CARD_LINE"]}"/>'
                 f'<text x="{tx+w/2:.1f}" y="{y_tags+20}" font-family="{SANS}" font-size="13.5" font-weight="700" '
                 f'fill="{T["VIOLET"] if hl else T["INK"]}" text-anchor="middle">{esc(t)}</text>')
        tx += w + 8

    # ---- row 1, left: description
    p.append(card(LX, r1, CW, desc_h, "Model description"))
    lines = ["A software engineer trained on Java,", "Spring Boot and distributed systems,",
             "fine-tuned to build AI-powered products", "that work in the real world."]
    for i, l in enumerate(lines):
        p.append(txt(LX + IN, r1 + 66 + i * 23, esc(l)))

    # ---- row 1, left: training data
    ty = r1 + desc_h + GAP
    p.append(card(LX, ty, CW, train_h, "Training data"))
    steps = [("FACENS", "Systems Analysis & Dev."), ("NTT DATA", "previous role"), ("Itaú Unibanco", "current role")]
    for i, (a, b) in enumerate(steps):
        y = ty + 72 + i * 32
        cur = i == len(steps) - 1
        p.append(f'<circle cx="{LX+IN+7}" cy="{y-5}" r="6.5" fill="{T["VIOLET"] if cur else T["VSTROKE"]}"/>')
        if not cur:
            p.append(f'<line x1="{LX+IN+7}" y1="{y+2}" x2="{LX+IN+7}" y2="{y+20}" stroke="{T["VSTROKE"]}" stroke-width="2"/>')
        p.append(txt(LX + IN + 26, y, f'<tspan font-weight="800">{esc(a)}</tspan><tspan fill="{T["MUT"]}">  ·  {esc(b)}</tspan>'))

    # ---- row 1, right: evaluation (same height as the left stack)
    p.append(card(RX, r1, CW, r1_h, "Evaluation results", "GitHub · last 12 months"))
    evals = [("Contributions", f'{s["total"]:,}', min(1, s["total"] / 1500)),
             ("Active days", f'{s["active_days"]} / 365', s["active_days"] / 365),
             ("Longest streak", f'{s["longest"]} days', min(1, s["longest"] / 60)),
             ("Best single day", f'{s["best_count"]} contributions', min(1, s["best_count"] / 50))]
    bw = CW - 2 * IN
    step = (r1_h - 84 - 44) / (len(evals) - 1)
    for i, (k, v, f) in enumerate(evals):
        y = r1 + 84 + i * step
        p.append(txt(RX + IN, y, esc(k), 15.5, None, 600))
        p.append(txt(RX + IN + bw, y, esc(v), 15.5, T["VIOLET"], 800, "end"))
        p.append(f'<rect x="{RX+IN}" y="{y+12}" width="{bw}" height="9" rx="4.5" fill="{T["TRACK"]}"/>')
        p.append(f'<rect x="{RX+IN}" y="{y+12}" width="0" height="9" rx="4.5" fill="{T["VIOLET"]}">'
                 f'<animate attributeName="width" from="0" to="{bw*f:.1f}" dur="1.2s" begin="{0.3+i*0.2:.1f}s" fill="freeze" '
                 'calcMode="spline" keySplines=".2 .8 .2 1" keyTimes="0;1"/></rect>')

    # ---- row 2: capabilities | example outputs
    p.append(card(LX, r2, CW, r2_h, "Capabilities"))
    caps = ["Designs backend systems and APIs", "Builds event-driven microservices",
            "Integrates AI into real products", "Ships with tests and CI/CD"]
    for i, c in enumerate(caps):
        p.append(txt(LX + IN, r2 + 70 + i * 27, f'<tspan fill="{T["GREEN"]}" font-weight="800">✓</tspan>  {esc(c)}'))
    p.append(card(RX, r2, CW, r2_h, "Example outputs"))
    outs = [("Lista.ai", "shopping lists generated by AI"), ("NextMove", "personal finance platform"),
            ("FightHub", "runs Jiu-Jitsu academies"), ("PayTracker", "expense tracking + alerts")]
    for i, (n, d) in enumerate(outs):
        p.append(fade(txt(RX + IN, r2 + 70 + i * 27,
                          f'<tspan font-weight="800" fill="{T["VIOLET"]}">{n}</tspan>  <tspan fill="{T["MUT"]}">{esc(d)}</tspan>'),
                      0.8 + i * 0.12, 0.3))

    # ---- row 3: intended use | how to reach me
    p.append(card(LX, r3, CW, r3_h, "Intended use"))
    for i, l in enumerate(["Teams building reliable backend systems",
                           "and AI-powered products: APIs, event-driven",
                           "services and integrations that scale."]):
        p.append(txt(LX + IN, r3 + 72 + i * 26, esc(l)))

    p.append(card(RX, r3, CW, r3_h, "Model architecture", "core stack"))
    stack = ["Java", "Spring Boot", "Kafka", "RabbitMQ", "PostgreSQL", "MongoDB", "Docker", "Kubernetes",
             "Redis", "AWS", "Azure", "AI integration"]
    cx, cy = RX + IN, r3 + 54
    for i, t in enumerate(stack):
        w = len(t) * 7.0 + 22
        if cx + w > RX + CW - IN:
            cx, cy = RX + IN, cy + 34
        hl = t == "AI integration"
        p.append(fade(f'<rect x="{cx:.1f}" y="{cy}" width="{w:.1f}" height="27" rx="7" '
                      f'fill="{T["VSOFT"] if hl else T["BG"]}" stroke="{T["VSTROKE"] if hl else T["CARD_LINE"]}"/>'
                      f'<text x="{cx+w/2:.1f}" y="{cy+18.5}" font-family="{SANS}" font-size="13.5" font-weight="700" '
                      f'fill="{T["VIOLET"] if hl else T["INK"]}" text-anchor="middle">{esc(t)}</text>', 0.9 + i * 0.05, 0.25))
        cx += w + 7
    p.append("</svg>")
    return p




if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "modelcard.svg"
    T.update(THEMES[sys.argv[2] if len(sys.argv) > 2 else "dark"])
    open(out, "w", encoding="utf-8").write("\n".join(build()))
    print("[modelcard] wrote", out)
