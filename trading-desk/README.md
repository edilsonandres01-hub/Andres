# Trading Desk — bot del video de @antonspain.ia

Reproduce el sistema del TikTok
[Claude + 11 skills para preparar operaciones](https://www.tiktok.com/@antonspain.ia/video/7701618162432806177):
escanea gráficos, lee noticias, marca entrada/stop/objetivo, simula el resto del
día **10.000 veces** y deja el ticket en paper hasta que digas **yes**.

El motor son las 11 skills MIT de
[Jakeschincariol/day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill)
vendored en `../day-trader-bot/`. Esta carpeta añade orquestación, config del
video ($500 paper) y un dashboard local.

> **No es consejo financiero.** Paper trading por defecto. Nada se envía a un
> bróker sin tu confirmación explícita.

## Las 11 skills

| Comando | Rol |
| --- | --- |
| `/trader-scanner` | Chart Scanner — miles de gráficos / rupturas ORB |
| `/trader-news` | News Monitor — titulares + SEC 8-K |
| `/trader-entry` | Entry Timer — dispara la entrada barra a barra |
| `/trader-exit` | Exit Planner — stop y objetivo antes de entrar |
| `/trader-timemachine` | Time Machine — 10.000 replays + historial |
| `/trader-budget` | Budget Manager — tamaño según pérdida máxima |
| `/trader-risk` | Risk Manager — PASS o BLOCK |
| `/trader-broker` | Order Executor — ticket paper, espera tu sí |
| `/trader-alerts` | Price Alerts — stop / target / flat |
| `/trader-analyst` | Earnings Analyst — hechos XBRL |
| `/trader-pelosi` | Pelosi Tracker — disclosures del Congreso |

## Quick start

```bash
# 1) Demo offline del trade TSLA del video (sin red)
python3 trading-desk/scripts/demo_reel.py

# 2) Misma demo con saldo $500 del gancho del video
python3 trading-desk/scripts/demo_reel.py --budget-500

# 3) Dashboard
python3 trading-desk/web/app.py
# → http://127.0.0.1:8787

# 4) Pipeline en vivo (Yahoo público; puede rate-limitar)
python3 trading-desk/scripts/pipeline.py --live TSLA
```

Tests del skill pack (315, offline):

```bash
cd day-trader-bot && python3 -m unittest discover -s tests -v
```

## Flujo de una operación

```
scanner → news → entry → exit → timemachine → budget → risk → broker
                                                              ↑
                                                     tu "yes" aquí
```

Artefactos en `trading-desk/runs/*/trader/` (`entry.json`, `plan.json`,
`timemachine.json`, `orders.json`, `risk.json`, `ticket.json`).

## Config

- `config/config.json` — saldo inicial **$500**, paper, pérdida máx $25/trade
- `config/config.reel5000.json` — ejemplo oficial del reel ($5.000 / $50)

## Instalación en Claude Code (opcional)

```bash
cp -r day-trader-bot/trader-* ~/.claude/skills/
```

O como plugin (instrucciones en `day-trader-bot/README.md`).

## Atribución

- Skills y herramientas Python: © 2026 Jake Schincariol, licencia MIT
- Video de referencia: @antonspain.ia
