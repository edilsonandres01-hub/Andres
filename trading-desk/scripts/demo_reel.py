#!/usr/bin/env python3
"""Reproduce offline the TSLA trade shown in the TikTok/reel.

Video source: https://www.tiktok.com/@antonspain.ia/video/7701618162432806177
Upstream skills: https://github.com/Jakeschincariol/day-trader-skill (MIT)

Runs the day-trade pipeline against fixture data for Monday 19 Oct 2026:
  entry -> exit -> timemachine -> budget -> risk -> broker ticket

Nothing is sent to a broker. Paper trading only. Not financial advice.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(ROOT)
SKILL = os.path.join(REPO, "day-trader-bot")
FIX = os.path.join(SKILL, "tests", "fixtures")
NOW = "2026-10-19 10:15"

SKILLS = [
    ("trader-scanner", "Chart Scanner", "Escanea miles de gráficos buscando rupturas"),
    ("trader-news", "News Monitor", "Lee titulares y filings SEC"),
    ("trader-entry", "Entry Timer", "Marca el momento exacto de entrada"),
    ("trader-exit", "Exit Planner", "Fija stop y objetivo antes de entrar"),
    ("trader-timemachine", "Time Machine", "Repite el resto del día 10.000 veces"),
    ("trader-budget", "Budget Manager", "Dimensiona la posición a tu pérdida máxima"),
    ("trader-risk", "Risk Manager", "Bloquea cualquier orden fuera de límites"),
    ("trader-broker", "Order Executor", "Muestra el ticket; solo ejecuta con tu sí"),
    ("trader-alerts", "Price Alerts", "Avisa en stop, objetivo y cierre"),
    ("trader-analyst", "Earnings Analyst", "Resume cambios en resultados"),
    ("trader-pelosi", "Pelosi Tracker", "Lee declaraciones del Congreso de EE.UU."),
]


def run(cmd, cwd):
    print("\n$", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.stdout.strip():
        print(proc.stdout.rstrip())
    if proc.returncode != 0:
        if proc.stderr.strip():
            print(proc.stderr.rstrip(), file=sys.stderr)
        raise SystemExit(proc.returncode)
    return proc.stdout


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Demo offline del trade TSLA del video")
    ap.add_argument(
        "--workdir",
        default=os.path.join(ROOT, "runs", "reel-tsla"),
        help="carpeta de trabajo (se recrea)",
    )
    ap.add_argument(
        "--config",
        default=os.path.join(ROOT, "config", "config.reel5000.json"),
        help="reglas de riesgo/presupuesto",
    )
    ap.add_argument(
        "--budget-500",
        action="store_true",
        help="usar saldo inicial $500 del video (en vez del ejemplo oficial $5,000)",
    )
    args = ap.parse_args(argv)

    if not os.path.isdir(SKILL):
        raise SystemExit("no encuentro day-trader-bot/; clona el skill pack primero")

    work = os.path.abspath(args.workdir)
    if os.path.isdir(work):
        shutil.rmtree(work)
    trader = os.path.join(work, "trader")
    os.makedirs(trader)

    cfg_src = (
        os.path.join(ROOT, "config", "config.json")
        if args.budget_500
        else os.path.abspath(args.config)
    )
    shutil.copy2(cfg_src, os.path.join(trader, "config.json"))

    entry_fix = os.path.join(FIX, "trader-entry", "TSLA-2026-10-19-5m.json")
    tm_fix = os.path.join(FIX, "trader-timemachine", "TSLA-60d5m.json.gz")
    news_chart = os.path.join(FIX, "trader-news", "chart-TSLA.json")
    news_xml = os.path.join(FIX, "trader-news", "yahoo-TSLA.xml")

    summary = {
        "source_video": "https://www.tiktok.com/@antonspain.ia/video/7701618162432806177",
        "upstream": "https://github.com/Jakeschincariol/day-trader-skill",
        "symbol": "TSLA",
        "session": "2026-10-19",
        "now": NOW,
        "paper": True,
        "financial_advice": False,
        "skills": [{"id": i, "name": n, "job": j} for i, n, j in SKILLS],
        "steps": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    def load_trader(name):
        with open(os.path.join(trader, name), encoding="utf-8") as fh:
            return json.load(fh)

    # 1) Entry Timer — opening-range breakout at 10:15
    run(
        [
            sys.executable,
            os.path.join(SKILL, "trader-entry", "entry.py"),
            "check",
            "TSLA",
            "--setup",
            "orb",
            "--now",
            NOW,
            "--offline",
            entry_fix,
            "--write",
            os.path.join(trader, "entry.json"),
            "--json",
        ],
        work,
    )
    entry = load_trader("entry.json")
    summary["steps"].append({"skill": "trader-entry", "result": entry})

    # 2) Exit Planner — stop at OR midpoint, target 1R
    run(
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
            "--json",
        ],
        work,
    )
    plan = load_trader("plan.json")
    summary["steps"].append({"skill": "trader-exit", "result": plan})

    # 3) Time Machine — 10,000 replays
    run(
        [
            sys.executable,
            os.path.join(SKILL, "trader-timemachine", "timemachine.py"),
            "run",
            "--plan",
            os.path.join(trader, "plan.json"),
            "--offline",
            tm_fix,
            "--now",
            NOW,
            "--seed",
            "19",
            "--write",
            os.path.join(trader, "timemachine.json"),
            "--json",
        ],
        work,
    )
    tm = load_trader("timemachine.json")
    summary["steps"].append({"skill": "trader-timemachine", "result": tm})

    # 4) Budget Manager
    run(
        [
            sys.executable,
            os.path.join(SKILL, "trader-budget", "size.py"),
            "--plan",
            os.path.join(trader, "plan.json"),
            "--config",
            os.path.join(trader, "config.json"),
            "--limit",
            "--now",
            NOW,
            "--write",
            os.path.join(trader, "orders.json"),
            "--json",
        ],
        work,
    )
    sized = load_trader("orders.json")
    summary["steps"].append({"skill": "trader-budget", "result": sized})

    # 5) Risk Manager
    run(
        [
            sys.executable,
            os.path.join(SKILL, "trader-risk", "check.py"),
            "--orders",
            os.path.join(trader, "orders.json"),
            "--config",
            os.path.join(trader, "config.json"),
            "--now",
            NOW,
            "--out",
            os.path.join(trader, "risk.json"),
            "--json",
        ],
        work,
    )
    risk = load_trader("risk.json")
    summary["steps"].append({"skill": "trader-risk", "result": risk})

    # 6) Broker ticket (never places — only shows READY/BLOCKED)
    out = run(
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
            "--now",
            NOW,
            "--json",
        ],
        work,
    )
    ticket = json.loads(out)
    write_json(os.path.join(trader, "ticket.json"), ticket)
    summary["steps"].append({"skill": "trader-broker", "result": ticket})

    # optional news snapshot from fixtures (no network)
    if os.path.isfile(news_xml):
        news_out = {
            "note": "titulares de fixture offline (Yahoo TSLA del ejemplo)",
            "fixture": os.path.relpath(news_xml, REPO),
            "chart_fixture": os.path.relpath(news_chart, REPO) if os.path.isfile(news_chart) else None,
        }
        write_json(os.path.join(trader, "news_meta.json"), news_out)
        summary["steps"].append({"skill": "trader-news", "result": news_out})

    write_json(os.path.join(work, "summary.json"), summary)

    # Human-readable report
    print("\n" + "=" * 60)
    print("DEMO REEL TSLA — paper only — no es consejo financiero")
    print("=" * 60)
    print(f"Entrada:  {entry.get('status')} @ {entry.get('price')} ({entry.get('time')})")
    print(
        f"Plan:     stop {plan.get('stop')}  target {plan.get('target')}  "
        f"riesgo/acción {plan.get('risk_per_share')}"
    )
    mc = tm.get("mc") or {}
    if mc:
        print(
            f"Time Machine: target {100 * mc.get('p_target', 0):.1f}%  "
            f"stop {100 * mc.get('p_stop', 0):.1f}%  "
            f"ninguno {100 * mc.get('p_neither', 0):.1f}%  "
            f"({mc.get('replays', 0)} replays)"
        )
    verdict = tm.get("verdict") or ""
    if verdict:
        print(f"Veredicto: {verdict}")
    orders = sized.get("orders") or []
    if orders:
        o = orders[0]
        print(
            f"Orden:    {o.get('side')} {o.get('qty')} {o.get('symbol')} "
            f"limit {o.get('limit_price')}  SL {o.get('stop_loss_stop_price')}  "
            f"TP {o.get('take_profit_limit_price')}"
        )
    results = risk.get("results") or []
    if results:
        v0 = results[0]
        print(f"Riesgo:   {v0.get('verdict')} — max loss ${v0.get('max_loss')}")
    if ticket:
        t0 = ticket[0] if isinstance(ticket, list) else ticket
        print(f"Ticket:   {t0.get('status')}")
        print(f"          {t0.get('plain')}")
    print(f"\nResumen JSON: {os.path.join(work, 'summary.json')}")
    print("Para aprobar una orden real necesitas tu sí explícito + connector paper.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
