#!/usr/bin/env python3
"""Mesa de trading — dashboard local (stdlib only).

Sirve la UI de las 11 skills y el último summary.json de la demo reel.
No ejecuta órdenes. Paper / investigación solamente.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
SUMMARY = os.path.join(ROOT, "runs", "reel-tsla", "summary.json")
HOST = os.environ.get("DESK_HOST", "127.0.0.1")
PORT = int(os.environ.get("DESK_PORT", "8787"))

SKILLS = [
    {"id": "trader-scanner", "name": "Chart Scanner", "cmd": "/trader-scanner", "job": "Escanea miles de gráficos buscando rupturas ORB, flags y rebotes."},
    {"id": "trader-news", "name": "News Monitor", "cmd": "/trader-news", "job": "Sigue titulares y filings SEC de cada ticker vigilado."},
    {"id": "trader-entry", "name": "Entry Timer", "cmd": "/trader-entry", "job": "Observa barra a barra y marca el momento de entrada."},
    {"id": "trader-exit", "name": "Exit Planner", "cmd": "/trader-exit", "job": "Fija stop y objetivo antes de arriesgar un dólar."},
    {"id": "trader-timemachine", "name": "Time Machine", "cmd": "/trader-timemachine", "job": "Repite el resto de la sesión 10.000 veces con barras reales."},
    {"id": "trader-budget", "name": "Budget Manager", "cmd": "/trader-budget", "job": "Dimensiona la posición a tu pérdida máxima."},
    {"id": "trader-risk", "name": "Risk Manager", "cmd": "/trader-risk", "job": "Bloquea cualquier orden fuera de tus límites."},
    {"id": "trader-broker", "name": "Order Executor", "cmd": "/trader-broker", "job": "Muestra el ticket paper; solo avanza con tu sí."},
    {"id": "trader-alerts", "name": "Price Alerts", "cmd": "/trader-alerts", "job": "Avisa en stop, objetivo y aplanado antes del cierre."},
    {"id": "trader-analyst", "name": "Earnings Analyst", "cmd": "/trader-analyst", "job": "Resume qué cambió en los resultados (SEC XBRL)."},
    {"id": "trader-pelosi", "name": "Pelosi Tracker", "cmd": "/trader-pelosi", "job": "Lee declaraciones públicas de trades del Congreso."},
]


def load_summary():
    if not os.path.isfile(SUMMARY):
        return None
    with open(SUMMARY, encoding="utf-8") as fh:
        return json.load(fh)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, content_type):
        with open(path, "rb") as fh:
            body = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            return self.send_file(os.path.join(STATIC, "index.html"), "text/html; charset=utf-8")
        if path == "/styles.css":
            return self.send_file(os.path.join(STATIC, "styles.css"), "text/css; charset=utf-8")
        if path == "/app.js":
            return self.send_file(os.path.join(STATIC, "app.js"), "application/javascript; charset=utf-8")
        if path == "/api/skills":
            return self.send_json({"skills": SKILLS, "paper": True})
        if path == "/api/summary":
            summary = load_summary()
            if summary is None:
                return self.send_json(
                    {
                        "ok": False,
                        "hint": "Ejecuta: python3 trading-desk/scripts/demo_reel.py",
                    },
                    404,
                )
            return self.send_json({"ok": True, "summary": summary})
        if path == "/health":
            return self.send_json({"status": "ok", "paper": True})
        self.send_json({"error": "not found"}, 404)


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Trading Desk UI → http://{HOST}:{PORT}")
    print("Paper only. Not financial advice.")
    server.serve_forever()


if __name__ == "__main__":
    main()
