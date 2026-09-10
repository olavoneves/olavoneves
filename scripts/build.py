#!/usr/bin/env python3
"""
Ponto de entrada do ONVS Terminal.

    python scripts/build.py --user olavoneves --out assets/onvs-terminal.svg

Variaveis de ambiente:
    GH_TOKEN / GITHUB_TOKEN  aumenta o limite da API (opcional, mas recomendado)
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import onvs_data
import render_terminal


def main():
    parser = argparse.ArgumentParser(description="Gera a capa animada do perfil.")
    parser.add_argument("--user", default="olavoneves")
    parser.add_argument("--out", default="assets/onvs-terminal.svg")
    parser.add_argument("--cache-dir", default=None,
                        help="reaproveita respostas da API (uso local, evita rate limit)")
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    data = onvs_data.collect(args.user, token, args.cache_dir)
    svg = render_terminal.render(data)

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)

    t = data["totals"]
    print("[ONVS] {}  ->  {} ({:.1f} KB)".format(
        datetime.now().strftime("%Y-%m-%d %H:%M"), args.out, len(svg) / 1024))
    print("[ONVS] {} contribuicoes / {} dias ativos / {} semanas / {} linguagens".format(
        t["contributions"], t["active_days"], len(data["candles"]), len(data["book"])))


if __name__ == "__main__":
    main()
