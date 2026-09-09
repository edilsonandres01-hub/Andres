# Parches para `edilsonalvarez-create/campus-posgrado-v2`

Estos parches se generaron desde una VM efímera y se guardan aquí porque el agente
**no tiene permiso de escritura** sobre `edilsonalvarez-create/campus-posgrado-v2`
(`403: Permission denied to cursor[bot]`). No hay ramas ni PRs en el repo destino:
hay que aplicarlos a mano.

Base sobre la que se generaron: `main` en `860cd00`, salvo `dashboard/` y
`gate-prerrequisitos/`, que son posteriores y se generaron sobre `main` en
`632bf7a`.

| Lote | Estado | Base |
|---|---|---|
| `llm-nvidia/` | **vigente** | `632bf7a` |
| `gate-prerrequisitos/` | **vigente** | `632bf7a` |
| `dashboard/` | vigente | `632bf7a` |
| `plantillas/` | vigente | `860cd00` |
| `deploy/` | **obsoleto** (entró en `main` por otra vía) | `860cd00` |
| `limpieza/` | **obsoleto** (entró en `main` por otra vía) | `860cd00` |

---

## AVISO: `deploy/` y `limpieza/` YA NO HACEN FALTA

Comprobado el 2026-09-08 contra `main` en `632bf7a`. Mientras estos parches se
preparaban, `main` avanzó 19 commits y **el mismo trabajo entró por otra vía**:

| Commit en `main` | Reemplaza a |
|---|---|
| `5e206b3` fix(docker): incluir backend/lib en la imagen | todo `deploy/` y `limpieza/0004` |
| `97bca96` chore(backend): eliminar código muerto (ai-grader.js + árbol NestJS) | `limpieza/0001`–`0003` |
| `1edfd74` docs(veracidad): MASTER_IEP_INTEGRATION.md refleja el sistema real | `limpieza/0005` |
| `93e47d2` fix(master): referencia interna + ECTS en vez de officialCode espurio | `limpieza/0006` |

Verificado en `main`: `backend/src/` y `backend/ai-grader.js` ya no existen, y el
`Dockerfile` ya tiene `COPY backend/lib ./lib` en su línea 10.

**No apliques `deploy/` ni `limpieza/`**: fallarán o generarán conflictos. Se
conservan solo como registro de la investigación. Producción ya arranca: los
endpoints `/api/tfm`, `/api/exams/:id/status` y `/api/me/review-plan` responden 401
(existen y piden sesión) en lugar de 404.

**Sigue vigente:** `plantillas/` (no está en `main`; los cuatro
`notebookTemplateUrl` siguen a `null`) y `dashboard/` (generado sobre `632bf7a`).

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

## `plantillas/` — 4 notebooks hands-on + memoria del TFM

Cinco parches. Serie independiente: no comparte ningún fichero con `deploy/` ni con
`limpieza/`. Ver `plantillas/APLICAR.md`.

```bash
git checkout -b cursor/handson-tfm-templates-21ab main
git am /ruta/a/plantillas/*.patch
git push -u origin cursor/handson-tfm-templates-21ab
```

Los enlaces a las plantillas apuntan a `.../blob/main/plantillas/...`, así que
empiezan a funcionar en cuanto la rama entre en `main`.

## `dashboard/` — el panel principal deja de listar las asignaturas del Máster

Dos parches. El panel listaba las 12 asignaturas del Máster (las 11 del plan + el
TFM) como tarjetas sueltas, duplicando el acceso al Máster y saltándose la cascada de
desbloqueo: `GET /api/courses` no devuelve `locked`, así que las 12 se veían iguales
y todas abiertas aunque solo la I lo estuviera. Ahora solo se ven dentro de
`/master-iep`, y el bloque del Máster del panel muestra el progreso agregado del
programa. El criterio es el dato de relación `meta.programSlug`, no el título.
Ver `dashboard/APLICAR.md`.

**Independiente de `deploy/`, `limpieza/` y `plantillas/`**: solo toca
`frontend/src/pages/Dashboard.tsx` y `frontend/src/hooks/useCourses.ts`, que ninguna
de ellas modifica.

```bash
git checkout -b cursor/dashboard-sin-asignaturas-del-master-bfca main
git am /ruta/a/dashboard/*.patch
git push -u origin cursor/dashboard-sin-asignaturas-del-master-bfca
```

## `gate-prerrequisitos/` — la cascada del Máster se aplica de verdad, en el servidor

Cuatro parches. La cascada lineal del Máster (11 asignaturas + TFM, cada una con
`meta.prerequisiteSlug`) era **decorativa**: `locked` se calculaba en un bucle de tres
líneas dentro del handler de `/api/programs`, y el único control real vivía en
`POST /api/progress`, que se esquivaba entregando la actividad, aprobando el quiz
formativo (que inserta en `progress`) o abriendo directamente un intento de examen de
15 preguntas. Comprobado en vivo: con una cuenta nueva se podía cursar entera una
asignatura bloqueada.

Ahora la regla vive en un solo sitio, `backend/lib/prerequisites.js`, y la consumen
todas las superficies. La semántica respeta el **modo consulta** de `7aed5bf`: leer
una asignatura bloqueada sigue devolviendo 200 con el material completo —el payload
lo declara con `locked` y `lockedReason`—, pero avanzar devuelve **403
`PREREQUISITE_LOCKED`**. Cierra además «Explorar Cursos», `CourseView` y el dashboard
móvil, incluida la invalidación de la caché de `AsyncStorage`.
Ver `gate-prerrequisitos/APLICAR.md`.

Verificado contra PostgreSQL real: smoke **15/15**, `gate-check` **30/30**, caché del
móvil **14/14**, `type-check` y `build` correctos. Inventario de estudiantes afectados
en producción: **0** (`gate-prerrequisitos/ESTUDIANTES-AFECTADOS.md`, con la consulta
SQL de solo lectura incluida).

**Choca con `dashboard/`**: ambos tocan `frontend/src/hooks/useCourses.ts`. El
conflicto es aditivo y se resuelve quedándose con los dos lados; el detalle exacto
está en `gate-prerrequisitos/APLICAR.md`.

```bash
git checkout -b cursor/gate-prerrequisitos-9b8f main
git am -3 /ruta/a/dashboard/*.patch            # primero
git am -3 /ruta/a/gate-prerrequisitos/*.patch  # se para en 0002; ver APLICAR.md
git push -u origin cursor/gate-prerrequisitos-9b8f
```

## `llm-nvidia/` — el LLM deja de ser Anthropic y pasa a NVIDIA NIM (kimi-k3)

Tres parches. La integración entera vive en `backend/lib/llm.js`, así que el
cambio se concentra ahí: `LLM_PROVIDER` acepta ahora `nvidia` y
`openai-compatible` además de `anthropic` y del `none` por defecto, hablando el
formato OpenAI (`system` como primer mensaje de `messages`, respuesta en
`choices[0].message.content`, sin streaming). **Anthropic sigue operativo**: misma
URL, mismas cabeceras, mismos presupuestos de tokens que antes.

El problema real no era traducir el formato sino que `moonshotai/kimi-k3` es un
**modelo de razonamiento**: gasta parte de `max_tokens` en su cadena de
pensamiento (`message.reasoning_content`) antes de escribir la respuesta. Con los
límites heredados de Claude la salida se truncaba, y `gradeSuggestion` y
`draftItems` se tragaban el JSON incompleto devolviendo `null` / `[]`, indistinguible
de «el modelo no dijo nada». Ahora los presupuestos son 3000/6000/16000
(configurables), `reasoning_content` se descarta siempre en el transporte, y una
respuesta con `finish_reason: "length"` lanza `LLM_TRUNCATED` en lugar de callarse.
Ver `llm-nvidia/APLICAR.md`.

**Independiente de `plantillas/`, `dashboard/` y `gate-prerrequisitos/`.** Solo
comparte `backend/simple-server.js` con el gate, y ahí cambia una línea de
comentario. Comprobado: los cuatro lotes aplicados en cadena sobre `632bf7a` solo
producen el conflicto ya conocido entre `dashboard/` y `gate-prerrequisitos/` en
`frontend/src/hooks/useCourses.ts`.

```bash
git checkout -b cursor/llm-nvidia-nim-2328 main
git am /ruta/a/llm-nvidia/*.patch
git push -u origin cursor/llm-nvidia-nim-2328
```

Las variables de Railway ya están puestas (ver más abajo), pero **no hacen nada
hasta que estos parches entren en `main`**: el código desplegado no entiende
`LLM_PROVIDER=nvidia`.

## Orden recomendado

Con `main` en `632bf7a`, los lotes que quedan por aplicar son `llm-nvidia/`,
`plantillas/`, `dashboard/` y `gate-prerrequisitos/`:

0. **`llm-nvidia/`** — independiente; el más pequeño y el único que no toca el
   frontend salvo un literal de texto. Puede ir en cualquier posición.
1. **`plantillas/`** — independiente de todo lo demás; no toca el frontend.
2. **`dashboard/`** — antes que el gate, porque el conflicto se resuelve mejor en
   ese sentido (`git am -3` deja una sola pieza que resolver).
3. **`gate-prerrequisitos/`** — al final. Es el único lote que toca el backend, el
   móvil y el CI, así que conviene que sea el último en entrar y el que se valide
   sobre el árbol ya completo. Se verificó exactamente así: árbol combinado
   `dashboard` + `gate` sobre `632bf7a`, con smoke 15/15 y gate-check 30/30.

`deploy/` y `limpieza/` ya no se aplican (ver el aviso de arriba). El orden
histórico que describían las secciones siguientes queda solo como registro.

Aviso: `main` avanzó de `860cd00` a `632bf7a`, y los lotes `deploy/`, `limpieza/` y
`plantillas/` se generaron sobre el primero. `limpieza/0001`–`0003` y `limpieza/0006`
ya **no aplican limpiamente** sobre el `main` actual, porque parte de lo que hacían
entró por otra vía (el scaffold NestJS ya no existe y `MasterIEPPage.tsx` ya trae el
cambio de la referencia interna). Conviene regenerar esos lotes sobre `632bf7a`; el
detalle está en `dashboard/APLICAR.md`.

Tras mergear, Railway construirá y esta vez arrancará: aplicará las migraciones
002→015 y el seed. Ese camino ya se ensayó sobre una restauración de los datos reales
de producción, sin pérdidas, y `smoke.mjs` pasó 15/15.

## Backup de producción

`backup-produccion-rowcounts.txt` es solo el recuento de filas. **El dump completo
NO está aquí** porque contiene datos reales de usuarios. Se generó en
`/tmp/backups/campus-posgrado-20260908-122825.sql` dentro de la VM, que es efímera.

**Corrección (2026-09-08, comprobado en producción en solo lectura).** Este párrafo
decía que la base de producción «sigue intacta en `001_init.sql` porque las
migraciones nunca llegaron a correr». Ya no es cierto: al conectarse por un proxy TCP
temporal para el inventario del gate se encontraron tablas de las migraciones
007–015 (`exam_attempts`, `formative_responses`, `activity_submissions`,
`tfm_enrollments`, `certificates`, `quiz_responses`). El esquema está al día; lo que
apenas tiene contenido son los datos: 4 usuarios (3 con rol `student`, dos de ellos
de pruebas automatizadas), 5 filas en `progress`, 0 entregas, 2 intentos de examen y
0 certificados. Detalle completo en
`gate-prerrequisitos/ESTUDIANTES-AFECTADOS.md`.

Aun así el backup se puede rehacer con `pg_dump` en cualquier momento antes de
mergear.

## Configuración del LLM en Railway (2026-09-09)

Servicio de app en producción (`campus-posgrado-v2`, entorno `production`). Estado
final tras la migración a NVIDIA:

| Variable | Valor |
|---|---|
| `LLM_PROVIDER` | `nvidia` |
| `LLM_MODEL` | `moonshotai/kimi-k3` |
| `LLM_MODEL_HEAVY` | `moonshotai/kimi-k3` |
| `LLM_API_KEY` | *(secreto, 70 caracteres, prefijo `nvapi-8eV…`)* |
| `ANTHROPIC_API_KEY` | **borrada** |

`LLM_BASE_URL` no hace falta: con `LLM_PROVIDER=nvidia` el código usa
`https://integrate.api.nvidia.com/v1` por defecto. Los presupuestos de tokens
tampoco están declarados; se usan los valores por defecto del código
(3000 / 6000 / 16000).

Dos avisos importantes:

- **Está inerte hasta que se mergee `llm-nvidia/`.** El código desplegado solo
  entiende `LLM_PROVIDER=anthropic`, así que hoy el tutor degrada a su FAQ de
  respaldo. Verificado en producción tras el cambio: `/api/tutor/:id` responde
  **200** con `disabled: true` y el texto de respaldo, y `/api/health` y
  `/api/courses` siguen en 200. No se rompe nada; simplemente no hay IA.
- **`ANTHROPIC_API_KEY` se borró y con ella se perdió el valor.** Antes del cambio
  había una clave de Anthropic válida y el tutor respondía de verdad. Si hay que
  volver atrás hay que pegar una clave nueva desde la consola de Anthropic; la
  anterior empezaba por `sk-ant-api03…`.
- **La clave de NVIDIA hay que rotarla**: se compartió por chat antes de ponerla.

## Pendiente de decisión del usuario
- **`officialCode` de las asignaturas V, VIII y TFM**: hoy muestran
  `IEP-V-INTERNO`, `IEP-VIII-INTERNO` e `IEP-TFM-INTERNO`. Para poner los códigos
  oficiales reales basta con definir `OFFICIAL_CODE_V`, `OFFICIAL_CODE_VIII` y
  `OFFICIAL_CODE_TFM` y volver a sembrar; no hay que tocar código.
