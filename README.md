# QA Guardian v2.0.0

Enterprise Diagnostic Engine — backend (FastAPI), frontend (React/Vite), Docker, Kubernetes y CI/CD.

## URL de despliegue (definida)

| Ambiente | URL |
|----------|-----|
| **Publica (live)** | **https://exclusively-sorts-objects-attitudes.trycloudflare.com** |
| **UI local** | **http://localhost:3100** |
| **API local** | **http://localhost:8181** |
| **Health** | http://localhost:8181/health |
| **Repo activo** | https://github.com/edilsonandres01-hub/Andres |
| **Repo solicitado** | https://github.com/edilsonalvarez-create/Andres *(sin permisos de push con la cuenta autenticada; contenido en el fork)* |

## Quick start

```bash
git clone https://github.com/edilsonandres01-hub/Andres.git qa-guardian-v2
cd qa-guardian-v2
docker compose up -d --build
```

Verificar:

```bash
curl http://localhost:8181/health
curl http://localhost:3100/health
```

Diagnostico de prueba:

```bash
curl -X POST http://localhost:8181/api/v1/diagnosis/ \
  -H "Content-Type: application/json" \
  -d "{\"input_data\":{\"security\":{\"sql_injection_risk\":\"high\",\"unsanitized_inputs\":5,\"prepared_statements_usage\":0.2}}}"
```

UI: abrir **http://localhost:3100** o la URL publica Cloudflare.

## Tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Stack

- Backend: FastAPI + motor deterministico (16 reglas)
- Frontend: React 18 + MUI + Vite
- Infra: Docker Compose, K8s manifests, GitHub Actions -> GHCR, Render blueprint
