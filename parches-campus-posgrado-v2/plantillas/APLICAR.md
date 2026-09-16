# Cómo aplicar esta serie de parches

Igual que la serie `limpieza/`: el agente **no tiene permiso de escritura** en
`edilsonalvarez-create/campus-posgrado-v2` (`git push` devuelve
`403 Permission to edilsonalvarez-create/campus-posgrado-v2.git denied to cursor[bot]`),
así que el trabajo se entrega como parches.

Son 5 commits sobre `main` en `860cd00`.

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/handson-tfm-templates-21ab main
git am /ruta/a/plantillas/*.patch
git push -u origin cursor/handson-tfm-templates-21ab
```

Comprobado: `git am` aplica los 5 parches sin conflictos sobre un clon limpio de
`main`. Si algo fallara, `git am --abort` deja el repositorio como estaba.

**Es independiente de la serie `limpieza/` y de `deploy/`**: no toca ningún fichero
que aquellas modifiquen (allí se tocan `Dockerfile`, `backend/src/**`, documentación
y frontend; aquí, `plantillas/**`, `backend/db/seed.js` y `backend/db/seed-data/**`).
Se pueden aplicar en cualquier orden.

## Los 5 commits

| # | Commit | Qué añade |
|---|---|---|
| 0001 | `plantillas`: notebooks hands-on de las Asignaturas III y VI | `master-iii-benchmark-motores-datos.ipynb`, `master-vi-tres-problemas-ml.ipynb` |
| 0002 | `plantillas`: notebook hands-on de la Asignatura IX | `master-ix-rag-panel-metricas.ipynb` |
| 0003 | `plantillas`: notebook hands-on de la Asignatura X | `master-x-desplegar-operar-modelo.ipynb` |
| 0004 | `plantillas`: memoria del TFM | `backend/db/seed-data/tfm-memoria.md` |
| 0005 | `seed`: publicar las plantillas en el producto | `seed.js`, `handson/master-{iii,vi,ix,x}.js`, `tfm.js` |

## Qué contiene

### Los cuatro notebooks (`plantillas/handson/`)

Uno por cada asignatura con track hands-on ya definido en
`backend/db/seed-data/handson/` — III, VI, IX y X — que hasta ahora tenían
`notebookTemplateUrl: null`.

| Asignatura | Notebook | Celdas | Qué se practica |
|---|---|---:|---|
| III — Motores de datos | `master-iii-benchmark-motores-datos.ipynb` | 27 | Benchmark de pandas / Polars / DuckDB sobre la misma agregación, con tiempo y memoria pico medidos, y el punto en que Spark deja de compensar |
| VI — Machine Learning | `master-vi-tres-problemas-ml.ipynb` | 31 | Clasificación, regresión y no supervisado sobre el mismo dataset industrial, con línea base honesta, fuga de datos provocada y model card |
| IX — IA generativa | `master-ix-rag-panel-metricas.ipynb` | 31 | RAG con métricas de recuperación (hit rate, MRR, nDCG) separadas de las de generación (fundamentación, alucinación, abstención) y coste por consulta |
| X — AI Platforms | `master-x-desplegar-operar-modelo.ipynb` | 25 | Empaquetado del modelo, servicio HTTP medido de verdad, detección de deriva (PSI y KS), coste a 12 meses y CI/CD |

Todos: `nbformat` 4, salidas limpias (`"outputs": []`, `"execution_count": null`),
datos sintéticos generados en el propio notebook (ninguno exige un fichero que el
estudiante no tenga) y degradación limpia si falta una biblioteca opcional.

### La plantilla de la memoria del TFM (`backend/db/seed-data/tfm-memoria.md`)

Markdown, ~33 500 caracteres. Índice obligatorio + presupuesto de páginas por
capítulo + la rúbrica de cada hito junto al apartado que la satisface, formato y
citación APA 7, declaración de uso de IA generativa, qué se entrega en cada hito y
lista de verificación final.

Va en `backend/db/seed-data/` a propósito: el `Dockerfile` de producción solo copia
`backend/db`, así que es el único sitio desde el que el seed puede leerla en el
contenedor.

## Verificaciones realizadas

- Los 4 notebooks: JSON válido, `nbformat.validate` correcto y **ejecutados de
  principio a fin con `nbclient` sin un solo error** (3,1 s / 11,8 s / 2,9 s / 4,3 s)
  sobre Python 3 con numpy, pandas, scikit-learn, matplotlib, DuckDB y Polars.
  PySpark no estaba instalado y el notebook III lo omite de forma explícita, como
  está diseñado.
- PostgreSQL 16 real: migraciones + `node db/seed.js` desde el estado ya sembrado,
  y una segunda pasada para confirmar idempotencia (mismos recuentos, sin huérfanos).
- Comprobado en la base: los 4 `notebookTemplateUrl` resueltos, los 4
  `tfm_milestones.template_url` apuntando a su ancla, y el recurso
  `Plantilla de la memoria del TFM` (33 531 caracteres, `type = docs`,
  `stable_key = tfm-memoria`) dentro del módulo *Entrega del TFM*.
- API en marcha: `GET /api/courses/master-tfm` devuelve el markdown de la memoria y
  `GET /api/courses/master-iii` devuelve el enlace al notebook.
- `node --check backend/db/seed.js` y `npm --prefix frontend run build`: correctos.

## Nota sobre `PLANTILLAS_BASE_URL`

Los enlaces se construyen contra
`https://github.com/edilsonalvarez-create/campus-posgrado-v2/blob/main`, así que
**funcionan en cuanto la rama se mergee a `main`**. Si las plantillas se mueven a un
CDN, a un fork o a otra rama, basta con definir `PLANTILLAS_BASE_URL` y volver a
sembrar; no hay que tocar código.
