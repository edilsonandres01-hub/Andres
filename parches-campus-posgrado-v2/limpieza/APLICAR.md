# Cómo aplicar esta serie de parches

El agente **no tiene permiso de escritura** en
`edilsonalvarez-create/campus-posgrado-v2` (`git push` devuelve
`403 Permission to edilsonalvarez-create/campus-posgrado-v2.git denied to cursor[bot]`),
así que el trabajo se entrega como parches en lugar de como rama remota.

Son 7 commits sobre `main` en `860cd00`.

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/dead-code-cleanup-21ab main
git am /tmp/patches/cleanup/*.patch
git push -u origin cursor/dead-code-cleanup-21ab
```

Comprobado: `git am` aplica los 7 parches sin conflictos sobre un clon limpio de
`main` y produce un árbol idéntico al que se verificó.

Si algo fallara, `git am --abort` deja el repositorio como estaba.

## Los 7 commits

| # | Commit |
|---|---|
| 0001 | `chore(backend)`: eliminar el scaffold NestJS muerto (`backend/src/**`) |
| 0002 | `chore(backend)`: eliminar `backend/ai-grader.js` (código muerto) |
| 0003 | `chore(backend)`: eliminar la config huérfana (`nest-cli.json`, `tsconfig.json`) y alinear `.env.example` |
| 0004 | `fix(deploy)`: copiar `backend/lib` en la imagen y arreglar los scripts de arranque |
| 0005 | `docs`: corregir la documentación para que describa el sistema realmente desplegado |
| 0006 | `fix(frontend)`: que la tarjeta de asignatura nunca quede sin referencia de código |
| 0007 | `fix(mobile)`: apuntar la app al backend que realmente responde |

## Verificaciones realizadas

- `node --check` sobre los 49 archivos JS del backend: todos correctos.
- PostgreSQL 16 real, 15 migraciones aplicadas y seed ejecutado desde cero:
  30 cursos, 92 módulos, 400 recursos, 217 lecciones, 58 exámenes.
- `backend/scripts/smoke.mjs` contra el servidor en marcha: **15 ok, 0 fallos**.
- Arranque replicando exactamente los `COPY` del `Dockerfile` corregido, con la
  base de datos vacía: migra, siembra y levanta el servidor.
- `npm --prefix frontend run type-check` y `npm --prefix frontend run build`:
  correctos.
