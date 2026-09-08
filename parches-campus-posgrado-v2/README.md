# Parches para `edilsonalvarez-create/campus-posgrado-v2`

Estos parches se generaron desde una VM efímera y se guardan aquí porque el agente
**no tiene permiso de escritura** sobre `edilsonalvarez-create/campus-posgrado-v2`
(`403: Permission denied to cursor[bot]`). No hay ramas ni PRs en el repo destino:
hay que aplicarlos a mano.

Base sobre la que se generaron: `main` en `860cd00`.

## `deploy/` — arreglo crítico de despliegue

El contenedor de Railway se cae al arrancar. `simple-server.js` hace
`require('./lib/llm')` en su línea 8, pero ningún `Dockerfile` copia `backend/lib`,
así que el proceso muere con `MODULE_NOT_FOUND` antes de escuchar y antes de aplicar
las migraciones. Railway mantiene viva la imagen anterior, por eso producción sirve
código de hace 11 commits.

Son dos líneas. Se pueden escribir a mano en lugar de aplicar el parche:

- `Dockerfile`, tras `COPY backend/simple-server.js ./simple-server.js`:
  `COPY backend/lib ./lib`
- `backend/Dockerfile`, tras `COPY simple-server.js ./simple-server.js`:
  `COPY lib ./lib`

## `limpieza/` — código muerto y documentación

Siete parches. El `0004` incluye el mismo arreglo del `Dockerfile` que `deploy/`,
así que **aplica una cosa o la otra, no las dos**. Ver `limpieza/APLICAR.md`.

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/dead-code-cleanup-21ab main
git am /ruta/a/limpieza/*.patch
git push -u origin cursor/dead-code-cleanup-21ab
```

## `plantillas/` — contenido que faltaba (4 notebooks + memoria del TFM)

Cinco parches. Añaden las cuatro plantillas hands-on de las Asignaturas III, VI, IX
y X (que tenían `notebookTemplateUrl: null`), la plantilla de la memoria del TFM y
el cableado del seed para que todo sea alcanzable desde el producto. Los cuatro
notebooks se ejecutaron de principio a fin sin errores. Ver `plantillas/APLICAR.md`.

**Independiente de `deploy/` y de `limpieza/`**: no comparte ningún fichero con ellas.

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/handson-tfm-templates-21ab main
git am /ruta/a/plantillas/*.patch
git push -u origin cursor/handson-tfm-templates-21ab
```

## Backup de producción

`backup-produccion-rowcounts.txt` es solo el recuento de filas. **El dump completo
NO está aquí** porque contiene datos reales de usuarios. Se generó en
`/tmp/backups/campus-posgrado-20260908-122825.sql` dentro de la VM, que es efímera.

La base de producción sigue intacta en `001_init.sql` (las migraciones nunca llegaron
a correr porque el contenedor se caía antes), así que ese backup se puede rehacer
idéntico en cualquier momento con `pg_dump` antes de mergear el arreglo.

## Pendiente de decisión del usuario

- **`ANTHROPIC_API_KEY`**: falta en Railway. El resto de la configuración del LLM
  (`LLM_PROVIDER=anthropic`, `LLM_MODEL`, `LLM_MODEL_HEAVY`) ya está puesta. Sin la
  clave el tutor degrada limpiamente en vez de fallar.
- **`officialCode` de las asignaturas V, VIII y TFM**: hoy muestran
  `IEP-V-INTERNO`, `IEP-VIII-INTERNO` e `IEP-TFM-INTERNO`. Para poner los códigos
  oficiales reales basta con definir `OFFICIAL_CODE_V`, `OFFICIAL_CODE_VIII` y
  `OFFICIAL_CODE_TFM` y volver a sembrar; no hay que tocar código.
