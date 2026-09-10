#!/usr/bin/env python3
"""
ONVS TERMINAL - renderiza a capa do perfil como um terminal de mercado.

O que o SVG mostra, tudo a partir de dados reais do GitHub:

  - candles semanais de um indice construido sobre as contribuicoes diarias
  - volume semanal de commits
  - media movel de 4 semanas
  - carteira de linguagens (bytes reais) com variacao da alocacao recente
  - indicadores de atividade
  - fita de cotacoes (ticker tape) com linguagens e repositorios recentes

Animacao: CSS puro dentro do SVG (o GitHub serve o arquivo como imagem,
scripts nao rodam, mas @keyframes sim).
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

W, H = 1000, 470
SPLIT = 700           # divisor entre coluna do grafico e painel lateral

PLOT_X0, PLOT_X1 = 26, 646
PLOT_Y0, PLOT_Y1 = 124, 306
VOL_Y0, VOL_Y1 = 320, 358
AXIS_X = 694          # coluna dos labels de preco
STRIP_Y = 382         # faixa de estatisticas
TAPE_Y = 428          # fita de cotacoes

C = {
    "bg": "#06090E",
    "panel": "#0A0F16",
    "line": "#161E29",
    "grid": "#121A24",
    "text": "#D8E1EC",
    "dim": "#64748B",
    "dim2": "#8494A8",
    "up": "#22D07E",
    "down": "#F05A6A",
    "amber": "#F2B705",
    "ma": "#4FA8F5",
}

MONTHS = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
          "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]

FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
BRT = timezone(timedelta(hours=-3))


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def esc(value):
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def br(value, dec=2):
    """Formata numero no padrao pt-BR: 1.234,56"""
    text = "{:,.{}f}".format(value, dec)
    return text.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def signed(value, dec=2, suffix="%"):
    return ("+" if value >= 0 else "-") + br(abs(value), dec) + suffix


def text(x, y, content, size=11, fill=None, weight=400, anchor="start",
         opacity=None, spacing=None, cls=None, style=None):
    parts = ['<text x="{:.1f}" y="{:.1f}" font-size="{}"'.format(x, y, size)]
    parts.append(' fill="{}"'.format(fill or C["text"]))
    if weight != 400:
        parts.append(' font-weight="{}"'.format(weight))
    if anchor != "start":
        parts.append(' text-anchor="{}"'.format(anchor))
    if opacity is not None:
        parts.append(' opacity="{}"'.format(opacity))
    if spacing is not None:
        parts.append(' letter-spacing="{}"'.format(spacing))
    if cls:
        parts.append(' class="{}"'.format(cls))
    if style:
        parts.append(' style="{}"'.format(style))
    parts.append(">{}</text>".format(esc(content)))
    return "".join(parts)


def rect(x, y, w, h, fill, rx=0, opacity=None, cls=None, style=None, stroke=None):
    parts = ['<rect x="{:.1f}" y="{:.1f}" width="{:.1f}" height="{:.1f}" fill="{}"'
             .format(x, y, max(w, 0), max(h, 0), fill)]
    if rx:
        parts.append(' rx="{}"'.format(rx))
    if stroke:
        parts.append(' stroke="{}"'.format(stroke))
    if opacity is not None:
        parts.append(' opacity="{}"'.format(opacity))
    if cls:
        parts.append(' class="{}"'.format(cls))
    if style:
        parts.append(' style="{}"'.format(style))
    parts.append("/>")
    return "".join(parts)


def line(x1, y1, x2, y2, stroke, width=1, dash=None, opacity=None, cls=None):
    parts = ['<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" stroke="{}" stroke-width="{}"'
             .format(x1, y1, x2, y2, stroke, width)]
    if dash:
        parts.append(' stroke-dasharray="{}"'.format(dash))
    if opacity is not None:
        parts.append(' opacity="{}"'.format(opacity))
    if cls:
        parts.append(' class="{}"'.format(cls))
    parts.append("/>")
    return "".join(parts)


def triangle(x, y, size, up, fill):
    """Seta cheia desenhada em path (evita depender de glifos unicode)."""
    if up:
        d = "M{:.1f} {:.1f} L{:.1f} {:.1f} L{:.1f} {:.1f} Z".format(
            x, y - size, x + size * 0.9, y + size * 0.7, x - size * 0.9, y + size * 0.7)
    else:
        d = "M{:.1f} {:.1f} L{:.1f} {:.1f} L{:.1f} {:.1f} Z".format(
            x, y + size, x + size * 0.9, y - size * 0.7, x - size * 0.9, y - size * 0.7)
    return '<path d="{}" fill="{}"/>'.format(d, fill)


# ---------------------------------------------------------------------------
# blocos do terminal
# ---------------------------------------------------------------------------

def header(data, now):
    profile = data["profile"]
    name = (profile.get("name") or data["user"]).upper()
    out = [rect(0, 0, W, 40, C["panel"]),
           line(0, 40, W, 40, C["line"], 1)]

    out.append('<circle cx="22" cy="20" r="4" fill="{}" class="pulse"/>'.format(C["amber"]))
    out.append(text(34, 24, "ONVS", 15, C["amber"], weight=700, spacing="1.5"))
    out.append(text(84, 24, "|", 13, C["line"]))
    out.append(text(98, 24, name, 13, C["text"], weight=700, spacing="1.2"))
    out.append(text(98 + len(name) * 8.4 + 14, 24,
                    "DESENVOLVEDOR FULL STACK JAVA", 10.5, C["dim2"], spacing="0.8"))

    weekday = now.weekday() < 5
    session = 10 <= now.hour < 17 and weekday
    label = "PREGÃO ABERTO" if session else "AFTER-MARKET"
    stamp = "{:02d}/{:02d}/{} {:02d}:{:02d} BRT".format(
        now.day, now.month, now.year, now.hour, now.minute)

    out.append(text(W - 20, 24, stamp, 10.5, C["dim"], anchor="end"))
    chip_w = len(label) * 6.4 + 26
    chip_x = W - 20 - len(stamp) * 6.3 - 14 - chip_w
    out.append(rect(chip_x, 11, chip_w, 18, C["up"] if session else C["dim"], rx=9, opacity=0.13))
    out.append('<circle cx="{:.1f}" cy="20" r="3" fill="{}" class="blink"/>'
               .format(chip_x + 12, C["up"] if session else C["dim2"]))
    out.append(text(chip_x + 21, 23.5, label, 9.5,
                    C["up"] if session else C["dim2"], weight=700, spacing="0.6"))
    return out


def price_block(data):
    candles = data["candles"]
    last = candles[-1]["close"]
    ref = candles[-5]["close"] if len(candles) > 5 else candles[0]["open"]
    change = (last / ref - 1) * 100 if ref else 0.0
    color = C["up"] if change >= 0 else C["down"]
    out = []

    out.append(text(26, 62, "ÍNDICE DE RITMO · BASE 100 = MÉDIA HISTÓRICA", 9.5,
                    C["dim"], spacing="1.4"))
    out.append(text(26, 95, br(last, 2), 32, color, weight=700))

    px = 26 + len(br(last, 2)) * 19.5 + 16
    out.append(triangle(px + 6, 86, 6, change >= 0, color))
    out.append(text(px + 18, 91, signed(change, 2), 15, color, weight=700))
    out.append(text(px + 18, 106, "{} pts em 4 semanas".format(signed(last - ref, 2, "")),
                    9.5, C["dim"]))

    # legenda do grafico
    lx = SPLIT - 250
    out.append(rect(lx, 76, 9, 13, C["up"], rx=1))
    out.append(text(lx + 15, 86, "SEMANA DE ALTA", 9, C["dim2"]))
    out.append(rect(lx, 94, 9, 13, C["down"], rx=1))
    out.append(text(lx + 15, 104, "SEMANA DE BAIXA", 9, C["dim2"]))
    out.append(line(lx + 132, 82, lx + 152, 82, C["ma"], 2))
    out.append(text(lx + 158, 86, "MÉDIA MÓVEL 4S", 9, C["dim2"]))
    out.append(rect(lx + 132, 96, 20, 8, C["dim"], opacity=0.45))
    out.append(text(lx + 158, 104, "VOLUME / COMMITS", 9, C["dim2"]))
    return out


def chart(data):
    candles = data["candles"]
    n = len(candles)
    out = []

    hi = max(c["high"] for c in candles)
    lo = min(c["low"] for c in candles)
    pad = (hi - lo) * 0.12 or 1
    hi, lo = hi + pad, lo - pad

    def py(value):
        return PLOT_Y1 - (value - lo) / (hi - lo) * (PLOT_Y1 - PLOT_Y0)

    # ---- grade + eixo de precos
    for i in range(5):
        value = lo + (hi - lo) * i / 4
        y = py(value)
        out.append(line(PLOT_X0, y, PLOT_X1, y, C["grid"], 1, dash="2 5"))
        out.append(text(AXIS_X, y + 3.5, br(value, 1), 9, C["dim"], anchor="end"))

    # ---- marca d'agua
    out.append(text((PLOT_X0 + PLOT_X1) / 2, PLOT_Y1 - 6, "ONVS", 74, "#FFFFFF",
                    weight=700, anchor="middle", opacity=0.02, spacing="14"))

    slot = (PLOT_X1 - PLOT_X0) / n
    body = max(3.0, min(9.0, slot * 0.66))

    vmax = max(c["volume"] for c in candles) or 1

    # ---- candles + volume (revelados da esquerda para a direita)
    draw = ['<g clip-path="url(#reveal)">']
    for i, c in enumerate(candles):
        cx = PLOT_X0 + slot * (i + 0.5)
        rising = c["close"] >= c["open"]
        color = C["up"] if rising else C["down"]
        top, bottom = py(max(c["open"], c["close"])), py(min(c["open"], c["close"]))
        draw.append(line(cx, py(c["high"]), cx, py(c["low"]), color, 1, opacity=0.85))
        draw.append(rect(cx - body / 2, top, body, max(bottom - top, 1.6), color, rx=0.8))

        vh = (c["volume"] / vmax) * (VOL_Y1 - VOL_Y0)
        draw.append(rect(cx - body / 2, VOL_Y1 - vh, body, vh, color,
                         rx=0.8, opacity=0.42))

    # ---- media movel de 4 semanas
    pts = []
    for i in range(n):
        window = candles[max(0, i - 3):i + 1]
        avg = sum(c["close"] for c in window) / len(window)
        pts.append("{:.1f},{:.1f}".format(PLOT_X0 + slot * (i + 0.5), py(avg)))
    draw.append('<polyline points="{}" fill="none" stroke="{}" stroke-width="1.6" '
                'stroke-linejoin="round" opacity="0.9" class="ma"/>'
                .format(" ".join(pts), C["ma"]))
    draw.append("</g>")
    out.extend(draw)

    # ---- eixo do tempo
    seen = set()
    for i, c in enumerate(candles):
        key = (c["start"].year, c["start"].month)
        if key in seen:
            continue
        seen.add(key)
        cx = PLOT_X0 + slot * (i + 0.5)
        if cx > PLOT_X1 - 12:
            continue
        out.append(text(cx, VOL_Y1 + 14, MONTHS[c["start"].month - 1], 8.5,
                        C["dim"], anchor="middle", spacing="0.5"))

    # ---- ultimo preco: linha tracejada + etiqueta
    last = candles[-1]
    color = C["up"] if last["close"] >= last["open"] else C["down"]
    y = py(last["close"])
    out.append('<g class="fade-late">')
    out.append(line(PLOT_X0, y, AXIS_X - 46, y, color, 1, dash="4 4", opacity=0.55))
    out.append(rect(AXIS_X - 44, y - 8.5, 46, 17, color, rx=2.5))
    out.append(text(AXIS_X - 21, y + 4, br(last["close"], 1), 10, "#04070B",
                    weight=700, anchor="middle"))
    out.append("</g>")

    out.append(text(PLOT_X0, VOL_Y0 - 6, "VOLUME SEMANAL", 8.5, C["dim"], spacing="1"))
    out.append('<rect x="{}" y="{}" width="{}" height="{}" fill="url(#sweep)" class="scan"/>'
               .format(PLOT_X0, PLOT_Y0, 90, VOL_Y1 - PLOT_Y0))
    return out


def stats_strip(data):
    candles = data["candles"]
    totals = data["totals"]
    rets = []
    for i in range(1, len(candles)):
        prev = candles[i - 1]["close"]
        if prev:
            rets.append((candles[i]["close"] / prev - 1) * 100)
    mean = sum(rets) / len(rets) if rets else 0.0
    vol = math.sqrt(sum((r - mean) ** 2 for r in rets) / len(rets)) if rets else 0.0

    cells = [
        ("ABERTURA", br(candles[0]["open"], 2), C["text"]),
        ("MÁXIMA", br(max(c["high"] for c in candles), 2), C["up"]),
        ("MÍNIMA", br(min(c["low"] for c in candles), 2), C["down"]),
        ("FECHAMENTO", br(candles[-1]["close"], 2), C["text"]),
        ("VOLUME 12M", br(totals["contributions"], 0), C["amber"]),
        ("VOLATILIDADE", br(vol, 1) + "%", C["text"]),
    ]

    out = [line(26, STRIP_Y, SPLIT - 26, STRIP_Y, C["line"], 1)]
    span = (SPLIT - 52) / len(cells)
    for i, (label, value, color) in enumerate(cells):
        x = 26 + span * i
        if i:
            out.append(line(x - 10, STRIP_Y + 8, x - 10, STRIP_Y + 30, C["line"], 1))
        out.append(text(x, STRIP_Y + 17, label, 8.5, C["dim"], spacing="0.9"))
        out.append(text(x, STRIP_Y + 32, value, 13, color, weight=700))
    return out


def side_panel(data):
    out = [rect(SPLIT, 40, W - SPLIT, TAPE_Y - 40, C["panel"], opacity=0.55),
           line(SPLIT, 40, SPLIT, TAPE_Y, C["line"], 1)]

    x0, x1 = SPLIT + 22, W - 22
    out.append(text(x0, 62, "CARTEIRA · LINGUAGENS", 9.5, C["amber"], weight=700, spacing="1.4"))
    out.append(text(x1, 62, "% BYTES", 8.5, C["dim"], anchor="end"))

    book = data["book"][:5]
    row_h = 36
    for i, item in enumerate(book):
        y = 88 + i * row_h
        delta = item["delta"]
        color = C["up"] if delta >= 0 else C["down"]
        out.append(text(x0, y, item["lang"].upper()[:14], 11, C["text"], weight=700))
        out.append(text(x1, y, br(item["share"], 1) + "%", 11, C["text"], weight=700, anchor="end"))

        out.append(rect(x0, y + 6, x1 - x0, 4, C["line"], rx=2))
        out.append(rect(x0, y + 6, (x1 - x0) * item["share"] / 100, 4,
                        C["amber"] if i == 0 else C["ma"], rx=2, cls="bar",
                        style="animation-delay:{:.2f}s".format(0.5 + i * 0.11)))

        out.append(triangle(x0 + 3.4, y + 16.5, 3.2, delta >= 0, color))
        out.append(text(x0 + 11, y + 19.5, signed(delta, 1, "pp"), 8.5, color))
        out.append(text(x0 + 56, y + 19.5, "·  {} repos".format(item["repos"]), 8.5, C["dim"]))

    sep = 88 + len(book) * row_h - 2
    out.append(line(x0, sep, x1, sep, C["line"], 1))
    out.append(text(x0, sep + 22, "INDICADORES", 9.5, C["amber"], weight=700, spacing="1.4"))
    out.append(text(x1, sep + 22, "Δ = ALOCAÇÃO 5 MESES", 8.5, C["dim"], anchor="end"))

    t = data["totals"]
    momentum = t["momentum"]
    kpis = [
        ("CONTRIBUIÇÕES 12M", br(t["contributions"], 0), C["text"]),
        ("DIAS EM PREGÃO", br(t["active_days"], 0), C["text"]),
        ("SEQUÊNCIA ATUAL", "{} d".format(t["current_streak"]), C["text"]),
        ("RECORDE", "{} d".format(t["best_streak"]), C["text"]),
        ("REPOSITÓRIOS", br(t["public_repos"], 0), C["text"]),
        ("PICO DIÁRIO", br(t["best_day"], 0), C["amber"]),
        ("MOMENTUM 30D", signed(momentum, 0), C["up"] if momentum >= 0 else C["down"]),
        ("SEGUIDORES", br(t["followers"], 0), C["text"]),
    ]
    col_w = (x1 - x0) / 2
    for i, (label, value, color) in enumerate(kpis):
        cx = x0 + col_w * (i % 2)
        cy = sep + 44 + (i // 2) * 29
        out.append(text(cx, cy, label, 8, C["dim"], spacing="0.6"))
        out.append(text(cx, cy + 14, value, 12.5, color, weight=700))
    return out


def tape(data, now):
    """Fita de cotacoes: linguagens + repositorios com push recente."""
    out = [rect(0, TAPE_Y, W, H - TAPE_Y, C["panel"]),
           line(0, TAPE_Y, W, TAPE_Y, C["line"], 1)]

    items = []
    for item in data["book"][:8]:
        delta = item["delta"]
        items.append((item["lang"].upper(), br(item["share"], 1) + "%",
                      signed(delta, 1, "pp"), C["up"] if delta >= 0 else C["down"]))

    today = now.date()
    for repo in data["repos"][:8]:
        if repo.get("fork"):
            continue
        pushed = datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00")).date()
        age = (today - pushed).days
        items.append((repo["name"].upper()[:26], (repo.get("language") or "MISC").upper(),
                      "D+{}".format(age), C["up"] if age <= 30 else C["dim2"]))

    adv = 6.6          # avanco medio por caractere em 11px monoespacado
    gap = 26.0
    runs, x = [], 0.0
    for label, mid, delta, color in items:
        runs.append((x, label, C["text"], 700))
        x += len(label) * adv + 9
        runs.append((x, mid, C["dim2"], 400))
        x += len(mid) * adv + 9
        runs.append((x, delta, color, 700))
        x += len(delta) * adv + gap
        runs.append((x - gap / 2 - 3, "|", C["line"], 400))

    total = x
    body = ['<g id="tape-runs">']
    for rx, content, color, weight in runs:
        body.append(text(rx, TAPE_Y + 25, content, 11, color, weight=weight))
    body.append("</g>")

    out.append('<style>@keyframes tape{{from{{transform:translateX(0)}}'
               'to{{transform:translateX(-{:.0f}px)}}}}</style>'.format(total))
    out.append('<g clip-path="url(#tape-clip)">')
    out.append('<g class="tape">')
    out.extend(body)
    out.append('<use href="#tape-runs" x="{:.0f}"/>'.format(total))
    out.append("</g></g>")

    # mascaras laterais para o texto "sumir" nas bordas
    out.append(rect(0, TAPE_Y + 1, 46, H - TAPE_Y, "url(#fade-l)"))
    out.append(rect(W - 46, TAPE_Y + 1, 46, H - TAPE_Y, "url(#fade-r)"))
    return out


# ---------------------------------------------------------------------------
# defs / css
# ---------------------------------------------------------------------------

def defs(total_tape_hint=4000):
    css = """
    /* Todo estado inicial vive dentro do @keyframes (fill-mode backwards):
       se o renderizador ignorar CSS animation, o SVG aparece completo. */
    text { font-family: %FONT%; }
    .pulse { animation: pulse 2.4s ease-in-out infinite; }
    .blink { animation: blink 1.6s steps(1,end) infinite; }
    #reveal-rect { animation: reveal 1.7s cubic-bezier(.22,.61,.36,1) backwards; }
    .ma { stroke-dasharray: 2400;
          animation: draw 2.1s cubic-bezier(.22,.61,.36,1) .25s backwards; }
    .fade-late { animation: fade .6s ease-out 1.5s backwards; }
    .bar { transform-box: fill-box; transform-origin: left center;
           animation: grow .9s cubic-bezier(.22,.61,.36,1) backwards; }
    .scan { opacity: 0; animation: scan 6.5s cubic-bezier(.45,0,.55,1) 1.9s infinite; }
    .tape { animation: tape 46s linear infinite; }

    @keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:.25 } }
    @keyframes blink { 0%,55% { opacity:1 } 56%,100% { opacity:.18 } }
    @keyframes reveal { from { width: 0 } }
    @keyframes draw { from { stroke-dashoffset: 2400 } }
    @keyframes fade { from { opacity: 0 } }
    @keyframes grow { from { transform: scaleX(0) } }
    @keyframes scan { 0% { opacity:0; transform: translateX(0) }
                      12% { opacity:.5 }
                      88% { opacity:.5 }
                      100% { opacity:0; transform: translateX(560px) } }
    /* @keyframes tape e emitido junto da fita, com a largura ja calculada */

    @media (prefers-reduced-motion: reduce) {
      .pulse,.blink,.ma,.fade-late,.bar,.scan,.tape,#reveal-rect { animation: none }
      .scan { display: none }
    }
""".replace("%FONT%", FONT)

    return """<defs>
  <style>{css}</style>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#080C12"/>
    <stop offset="55%" stop-color="#06090E"/>
    <stop offset="100%" stop-color="#090D14"/>
  </linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{ma}" stop-opacity="0"/>
    <stop offset="70%" stop-color="{ma}" stop-opacity="0.05"/>
    <stop offset="100%" stop-color="{ma}" stop-opacity="0.14"/>
  </linearGradient>
  <linearGradient id="fade-l" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{panel}"/><stop offset="100%" stop-color="{panel}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="fade-r" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{panel}" stop-opacity="0"/><stop offset="100%" stop-color="{panel}"/>
  </linearGradient>
  <clipPath id="reveal"><rect id="reveal-rect" x="{px0}" y="{py0}" width="700" height="{ph}"/></clipPath>
  <clipPath id="tape-clip"><rect x="0" y="{ty}" width="{w}" height="{th}"/></clipPath>
</defs>""".format(css=css, ma=C["ma"], panel=C["panel"], px0=PLOT_X0 - 6, py0=PLOT_Y0 - 10,
                  ph=VOL_Y1 - PLOT_Y0 + 20, ty=TAPE_Y, w=W, th=H - TAPE_Y)


# ---------------------------------------------------------------------------

def render(data, now=None):
    now = now or datetime.now(BRT)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
             'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
             'aria-label="Terminal de mercado com as estatisticas do GitHub de {u}">'
             .format(w=W, h=H, u=esc(data["user"]))]
    parts.append(defs())
    parts.append(rect(0, 0, W, H, "url(#bg)"))
    parts.extend(header(data, now))
    parts.extend(price_block(data))
    parts.extend(chart(data))
    parts.extend(stats_strip(data))
    parts.extend(side_panel(data))
    parts.extend(tape(data, now))
    parts.append(rect(0.5, 0.5, W - 1, H - 1, "none", rx=6, stroke=C["line"]))
    parts.append("</svg>")
    return "\n".join(parts)
