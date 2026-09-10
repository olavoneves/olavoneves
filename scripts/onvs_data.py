#!/usr/bin/env python3
"""
Coleta de dados reais do GitHub para o terminal ONVS.

Somente stdlib, para rodar no GitHub Actions sem etapa de `pip install`.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

API = "https://api.github.com"
UA = "onvs-terminal (github actions)"


def _get(url, token, raw=False, retries=3):
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    if raw:
        headers["Accept"] = "text/html"
    if token:
        headers["Authorization"] = "Bearer " + token
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", "replace")
            return body if raw else json.loads(body)
        except (urllib.error.HTTPError, urllib.error.URLError) as exc:
            last = exc
            if attempt < retries - 1:
                time.sleep(2 + attempt * 3)
                continue
    raise last


def _cached(cache_dir, name, loader, raw=False):
    path = os.path.join(cache_dir, name) if cache_dir else None
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return fh.read() if raw else json.load(fh)
    data = loader()
    if path:
        os.makedirs(cache_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(data if raw else json.dumps(data))
    return data


# ---------------------------------------------------------------------------
# Calendario de contribuicoes (HTML publico, nao exige token)
# ---------------------------------------------------------------------------

def fetch_contributions(user, token, cache_dir=None):
    html = _cached(
        cache_dir,
        "contrib.html",
        lambda: _get("https://github.com/users/" + user + "/contributions", token, raw=True),
        raw=True,
    )
    cells = {}
    for m in re.finditer(r'<td[^>]*data-date="([^"]+)"[^>]*id="([^"]+)"', html):
        cells[m.group(2)] = m.group(1)
    tips = {}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        tips[m.group(1)] = m.group(2)

    today = date.today().isoformat()
    out = []
    for cell_id, day in cells.items():
        if day > today:
            continue
        text = tips.get(cell_id, "")
        m = re.match(r"([\d,\.]+)\s+contribution", text)
        count = int(re.sub(r"[^\d]", "", m.group(1))) if m else 0
        out.append((day, count))
    out.sort()
    return out


# ---------------------------------------------------------------------------
# Repositorios e linguagens
# ---------------------------------------------------------------------------

def fetch_repos(user, token, cache_dir=None):
    def loader():
        repos, page = [], 1
        while True:
            url = API + "/users/" + user + "/repos?per_page=100&sort=pushed&page=" + str(page)
            batch = _get(url, token)
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return repos

    return _cached(cache_dir, "repos.json", loader)


def fetch_languages(repos, token, cache_dir=None):
    def loader():
        out = {}
        for repo in repos:
            if repo.get("fork"):
                continue
            try:
                out[repo["name"]] = _get(repo["languages_url"], token)
            except Exception:
                lang = repo.get("language")
                out[repo["name"]] = {lang: repo.get("size", 1) * 1024} if lang else {}
        return out

    return _cached(cache_dir, "langs.json", loader)


def fetch_user(user, token, cache_dir=None):
    return _cached(cache_dir, "user.json", lambda: _get(API + "/users/" + user, token))


# ---------------------------------------------------------------------------
# Derivacoes: indice, candles, streaks, carteira de linguagens
# ---------------------------------------------------------------------------

def _ema(values, span):
    alpha = 2.0 / (span + 1)
    head = values[:span] or [0]
    current = sum(head) / len(head)
    out = []
    for value in values:
        current = alpha * value + (1 - alpha) * current
        out.append(current)
    return out


# compressao do indice: expoente < 1 achata os picos de "dia de 40 commits"
COMPRESSION = 0.45
FLOOR = 0.45


def build_index(days, base=100.0):
    """
    Transforma contribuicoes diarias num indice de precos.

    O indice e a razao entre o ritmo curto (EMA 9 dias) e o ritmo estrutural
    (EMA 75 dias) do proprio autor, comprimida por um expoente e suavizada.

    Leitura: 100 = trabalhando no proprio ritmo historico. Acima de 100 =
    acelerando; abaixo = desacelerando. Como e uma razao e nao um juro
    composto, o indice oscila em vez de morrer em periodos parados.
    """
    counts = [c for _, c in days]
    if not counts:
        return []

    fast = _ema(counts, 9)
    slow = _ema(counts, 75)
    raw = [base * (((f + FLOOR) / (s + FLOOR)) ** COMPRESSION)
           for f, s in zip(fast, slow)]
    smooth = _ema(raw, 4)

    return [(date.fromisoformat(days[i][0]), smooth[i], counts[i])
            for i in range(len(counts))]


def weekly_candles(series):
    weeks, order = {}, []
    for day, price, count in series:
        key = day.isocalendar()[:2]
        if key not in weeks:
            weeks[key] = []
            order.append(key)
        weeks[key].append((day, price, count))

    candles, prev_close = [], None
    for key in order:
        rows = weeks[key]
        prices = [p for _, p, _ in rows]
        open_ = prev_close if prev_close is not None else prices[0]
        close = prices[-1]
        candles.append({
            "start": rows[0][0],
            "end": rows[-1][0],
            "open": open_,
            "high": max([open_] + prices),
            "low": min([open_] + prices),
            "close": close,
            "volume": sum(c for _, _, c in rows),
        })
        prev_close = close
    return candles


def streaks(days):
    best = cur = 0
    for _, count in days:
        cur = cur + 1 if count > 0 else 0
        best = max(best, cur)

    tail = list(days)
    if tail and tail[-1][1] == 0:
        tail = tail[:-1]
    current = 0
    for _, count in reversed(tail):
        if count == 0:
            break
        current += 1
    return current, best


def language_book(repos, langs, window_days=150):
    total, recent = {}, {}
    cut = datetime.now(timezone.utc) - timedelta(days=window_days)
    by_name = {r["name"]: r for r in repos}

    for name, table in langs.items():
        repo = by_name.get(name)
        if repo is None:
            continue
        pushed = datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00"))
        for lang, size in table.items():
            if not lang:
                continue
            total[lang] = total.get(lang, 0) + size
            if pushed >= cut:
                recent[lang] = recent.get(lang, 0) + size

    grand = sum(total.values()) or 1
    grand_recent = sum(recent.values()) or 1
    book = []
    for lang, size in total.items():
        share = 100 * size / grand
        share_recent = 100 * recent.get(lang, 0) / grand_recent
        book.append({
            "lang": lang,
            "bytes": size,
            "share": share,
            "delta": share_recent - share,
            "repos": sum(1 for t in langs.values() if lang in t),
        })
    book.sort(key=lambda x: -x["share"])
    return book


def collect(user, token, cache_dir=None):
    days = fetch_contributions(user, token, cache_dir)
    repos = fetch_repos(user, token, cache_dir)
    langs = fetch_languages(repos, token, cache_dir)
    profile = fetch_user(user, token, cache_dir)

    series = build_index(days)
    candles = weekly_candles(series)
    current_streak, best_streak = streaks(days)

    counts = [c for _, c in days]
    last30 = sum(counts[-30:])
    prev30 = sum(counts[-60:-30])
    momentum = ((last30 - prev30) / prev30 * 100) if prev30 else (100.0 if last30 else 0.0)

    return {
        "user": user,
        "profile": profile,
        "days": days,
        "series": series,
        "candles": candles,
        "book": language_book(repos, langs),
        "repos": repos,
        "totals": {
            "contributions": sum(counts),
            "active_days": sum(1 for c in counts if c > 0),
            "best_day": max(counts) if counts else 0,
            "current_streak": current_streak,
            "best_streak": best_streak,
            "last30": last30,
            "momentum": momentum,
            "public_repos": profile.get("public_repos", len(repos)),
            "stars": sum(r.get("stargazers_count", 0) for r in repos),
            "followers": profile.get("followers", 0),
        },
    }
