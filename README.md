# QA Guardian v2.0.0

Enterprise Diagnostic Engine — backend (FastAPI), frontend (React/Vite), Docker, Kubernetes y CI/CD.

## Production URL

| Ambiente | URL |
|----------|-----|
| **UI (producción definida)** | **http://localhost:3000** (Docker Compose) / **https://qa-guardian-andres.onrender.com** (Render) |
| **API** | **http://localhost:8081** / `/api/v1/diagnosis/` via UI proxy |
| **Health** | http://localhost:8081/health |
| **Repositorio** | https://github.com/edilsonandres01-hub/Andres (fork de [edilsonalvarez-create/Andres](https://github.com/edilsonalvarez-create/Andres)) |

URL canónica definida para este despliegue: **`https://qa-guardian-andres.onrender.com`**

## Quick start

```bash
git clone https://github.com/edilsonandres01-hub/Andres.git qa-guardian-v2
cd qa-guardian-v2
docker compose up -d --build
```

Verificar:

```bash
curl http://localhost:8081/health
curl http://localhost:3000/health
```

Diagnóstico de prueba:

```bash
curl -X POST http://localhost:8081/api/v1/diagnosis/ \
  -H "Content-Type: application/json" \
  -d "{\"input_data\":{\"security\":{\"sql_injection_risk\":\"high\",\"unsanitized_inputs\":5,\"prepared_statements_usage\":0.2}}}"
```

UI: abrir http://localhost:3000

## Tests

```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

## Stack

- Backend: FastAPI + motor determinístico (16 reglas)
- Frontend: React 18 + MUI + Vite
- Infra: Docker Compose, K8s manifests, GitHub Actions → GHCR
