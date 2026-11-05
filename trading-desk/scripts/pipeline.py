#!/usr/bin/env python3
"""Orquestador del pipeline day-trader (paper por defecto).

Flujo (como en el video / day-trader-skill):
  scanner → news → entry → exit → timemachine → budget → risk → broker

Sin `--live` solo corre la demo offline TSLA del reel.
Con `--live SYMBOL` usa datos públicos de Yahoo (puede fallar por rate-limit).
Nunca envía órdenes: el ticket queda en READY esperando tu sí.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
SKILL = os.path.join(REPO, "day-trader-bot")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pipeline day-trader (paper)")
    ap.add_argument("--live", metavar="SYMBOL", help="ticker en vivo (Yahoo), p.ej. TSLA")
    ap.add_argument("--now", help='hora NY fija, p.ej. "2026-10-19 10:15"')
    ap.add_argument("--budget-500", action="store_true", help="usar config de $500 del video")
    ap.add_argument("--workdir", default=os.path.join(ROOT, "runs", "live"))
    args = ap.parse_args(argv)

    if not args.live:
        demo = os.path.join(ROOT, "scripts", "demo_reel.py")
        cmd = [sys.executable, demo]
        if args.budget_500:
            cmd.append("--budget-500")
        return subprocess.call(cmd)

    symbol = args.live.upper().strip()
    work = os.path.abspath(args.workdir)
    trader = os.path.join(work, "trader")
    os.makedirs(trader, exist_ok=True)

    cfg = os.path.join(
        ROOT,
        "config",
        "config.json" if args.budget_500 else "config.reel5000.json",
    )
    subprocess.check_call(["cp", cfg, os.path.join(trader, "config.json")])

    now_args = ["--now", args.now] if args.now else []

    steps = [
        [
            sys.executable,
            os.path.join(SKILL, "trader-entry", "entry.py"),
            "check",
            symbol,
            "--setup",
            "orb",
            *now_args,
            "--write",
            os.path.join(trader, "entry.json"),
        ],
        [
            sys.executable,
            os.path.join(SKILL, "trader-exit", "exit.py"),
            "plan",
            "--stop",
            "or-mid",
            "--target",
            "1R",
            "--from",
            os.path.join(trader, "entry.json"),
            "--config",
            os.path.join(trader, "config.json"),
            "--write",
            os.path.join(trader, "plan.json"),
        ],
        [
            sys.executable,
            os.path.join(SKILL, "trader-timemachine", "timemachine.py"),
            "run",
            "--plan",
            os.path.join(trader, "plan.json"),
            *now_args,
            "--write",
            os.path.join(trader, "timemachine.json"),
        ],
        [
            sys.executable,
            os.path.join(SKILL, "trader-budget", "size.py"),
            "--plan",
            os.path.join(trader, "plan.json"),
            "--config",
            os.path.join(trader, "config.json"),
            "--limit",
            *now_args,
            "--write",
            os.path.join(trader, "orders.json"),
        ],
        [
            sys.executable,
            os.path.join(SKILL, "trader-risk", "check.py"),
            "--orders",
            os.path.join(trader, "orders.json"),
            "--config",
            os.path.join(trader, "config.json"),
            *now_args,
            "--out",
            os.path.join(trader, "risk.json"),
        ],
        [
            sys.executable,
            os.path.join(SKILL, "trader-broker", "ticket.py"),
            "show",
            "--orders",
            os.path.join(trader, "orders.json"),
            "--risk",
            os.path.join(trader, "risk.json"),
            "--config",
            os.path.join(trader, "config.json"),
            *now_args,
        ],
    ]

    print(f"Pipeline LIVE paper para {symbol}")
    print("No es consejo financiero. Nada se envía al broker sin tu sí.\n")
    for cmd in steps:
        print("$", " ".join(cmd))
        code = subprocess.call(cmd, cwd=work)
        if code != 0:
            return code
        print()
    print(f"Artefactos en {trader}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
