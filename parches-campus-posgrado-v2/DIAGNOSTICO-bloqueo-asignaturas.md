# Diagnóstico forense — las asignaturas del Máster IEP aparecen desbloqueadas en el dashboard

**Tipo de trabajo:** diagnóstico de solo lectura. **No se ha modificado ni un archivo del producto.**
Todo el análisis se hizo sobre un clon propio en `/tmp/campus-v2-diagnostico`, con una base de datos
propia (`campus_diag`) y una API propia en el puerto `4102`. Los scripts de prueba viven en `/tmp`,
fuera del árbol del repositorio. Este informe es el único archivo que se añade.

**Repositorio analizado:** `edilsonalvarez-create/campus-posgrado-v2`, rama `main`.
**Commit analizado:** `632bf7a` (`HEAD` de `main` en el momento del diagnóstico).
El encargo citaba `860cd00`; `main` ya había avanzado 19 commits. Se comprobó que la divergencia
**no afecta al defecto**: entre `860cd00` y `632bf7a`, `frontend/src/pages/Dashboard.tsx` no cambia,
`courseSummary()` y `coursesForUser()` no cambian, y en `GET /api/programs/:slug` el único cambio son
5 líneas que añaden `internalCode` y `ects` al objeto de asignatura. El diagnóstico vale para ambos commits.

**Arquitectura real confirmada:** servidor `http` nativo de Node en `backend/simple-server.js` +
PostgreSQL vía `backend/db/pool.js`. `backend/src/**` (andamiaje NestJS) no se despliega y, de hecho,
ya fue borrado del árbol entre `860cd00` y `632bf7a`. Autenticación por scrypt + tokens opacos de 64
hex en `sessions` (verificado: el token devuelto por `POST /api/auth/register` mide 64 caracteres).

---

## 1. Tabla de entrega

| Elemento | Resultado |
|---|---|
| Fuente de verdad del bloqueo | **No existe en la base de datos.** No hay columna `locked`/`available` ni vista que la calcule (el único `locked` del esquema es `forum_threads.locked`, migración `014`, sin relación). La BD guarda solo los ingredientes: `courses.meta->>'prerequisiteSlug'` (JSONB, sembrado en `db/seed.js:515`) y las filas de `progress`. La disponibilidad es **derivada, y se deriva en un solo sitio**: un bucle de JavaScript dentro del handler del programa, `backend/simple-server.js:905-907` |
| Endpoint (dashboard) | `GET /api/courses` — `backend/simple-server.js:682-685` |
| Endpoint (Máster) | `GET /api/programs/:slug` (`/api/programs/master-iep`) — `backend/simple-server.js:870-930` |
| Función backend / serializador | Dashboard: `coursesForUser()` (`:216-236`) → `courseSummary()` (`:114-137`). Máster: serializador anónimo en línea dentro del propio handler (`:884-903`) + bucle de bloqueo (`:905-907`). **Son dos serializadores distintos y no comparten nada** |
| Campo de estado | `locked: boolean`. Presente en la respuesta de `/api/programs/:slug`; **ausente por completo** en la de `/api/courses` (`courseSummary` no lo emite, y no existe `isLocked`, `available` ni `accessStatus` en ningún otro nombre) |
| Componente frontend (dashboard) | `frontend/src/components/CourseCard.tsx` (props: `id`, `title`, `description`, `imageUrl?`, `progress`), invocado desde `frontend/src/pages/Dashboard.tsx:176-185` y `:200-209`, con datos de `useCourses()` (`frontend/src/hooks/useCourses.ts:19-27`) |
| Componente frontend (Máster) | `AsignaturaCard`, función local **privada** de `frontend/src/pages/MasterIEPPage.tsx:11-80` (props: `asignatura: ProgramAsignatura`, `prereqTitle`, `onOpen`, `onPreview`), con datos de `useProgram()` (`frontend/src/hooks/usePrograms.ts:38-47`) |
| Estado dentro del Máster | **Correcto.** Estudiante recién matriculado: `master-i` con `locked:false`, las otras 11 con `locked:true`. Se renderizan con candado 🔒, fondo gris, borde discontinuo, opacidad y sin navegación (`MasterIEPPage.tsx:24-41`). Verificado en píxeles: 10 candados tras completar I |
| Estado en Dashboard | **Todas disponibles.** Las 12 tarjetas se pintan con el mismo `CourseCard`, mismo degradado, misma barra de progreso y todas navegables a `/courses/:id`. Verificado en píxeles: **0 candados** en el dashboard con el mismo usuario y en el mismo instante en que el Máster muestra 10 |
| Punto exacto donde se pierde o se ignora | **`courseSummary()` en `backend/simple-server.js:114-137`, alimentada por `coursesForUser()` en `:216-236`.** Ahí muere la cadena: la consulta SQL de `coursesForUser` **sí** trae todo lo necesario (`c.*`, que incluye `meta` con `prerequisiteSlug`, más el `completed`/`total` por curso), pero el serializador emite `meta` en crudo y **nunca calcula ni añade `locked`**. El bucle que sí lo calcula (`:905-907`) está escrito dentro del handler de `/api/programs/:slug` y no es reutilizable. Segundo eslabón roto, independiente: aunque el backend emitiera el campo, `Course` en `useCourses.ts:4-17` no lo declara y `CourseCard` no tiene rama de render para bloqueado — la interfaz no sabría representarlo |
| Causa raíz | La regla de negocio «cada asignatura se desbloquea al 100 % de la anterior» **no está modelada como un dato ni como una función compartida**, sino escrita a mano en el interior de un handler. Existe una única implementación de la cascada (`:905-907`) y vive en el contexto del programa; el listado genérico de cursos, que es lo que consume el dashboard (y Explorar, y el móvil), sirve las mismas 12 filas de `courses` sin ese cálculo. No hay tipo compartido, ni contrato, ni prueba que obligue a los dos caminos a coincidir |
| Severidad | **Alta** en integridad académica; nula en confidencialidad de datos. La cascada es hoy **casi decorativa**: solo la respeta la vista del Máster. Comprobado en vivo con un usuario nuevo: se puede abrir una asignatura bloqueada (`GET /api/courses/master-ii` → **200** con sus 3 módulos y 15 recursos), entregar la actividad de una lección suya (**200**), aprobar su quiz formativo (**3/3, `passed:true`**) — lo que **inserta fila en `progress`** — y **abrir un intento de examen con 15 preguntas** (**200**). El único freno del backend es `POST /api/progress` (`:993-1009`), y ese camino es evitable |
| Corrección mínima recomendada | **(a) Backend, 1 función y 2 líneas de uso:** extraer el bucle `:905-907` a un helper único, p. ej. `applyProgramLocks(courses)`, que reciba las filas ya serializadas, construya el mapa `slug → percentage` y fije `locked` a partir de `meta.prerequisiteSlug`; llamarlo desde el handler del programa (donde ya está) **y** desde `coursesForUser()`, de forma que `courseSummary` emita `locked` y `prerequisiteSlug` (y opcionalmente `lockReason`) en **todo** listado de cursos. No hace falta migración ni cambio de SQL: `coursesForUser` ya trae `meta` y el progreso de las 12 asignaturas en la misma consulta. **(b) Frontend, contrato + una rama de render:** añadir `locked?: boolean` y `prerequisiteSlug?: string \| null` a `Course` (`useCourses.ts`) y una rama bloqueada en `CourseCard` (candado, opacidad, `disabled`, texto «Completa X para desbloquear»), con lo que Dashboard, `ExploreCoursesPage` y cualquier futuro listado la heredan gratis. **(c) Cierre del gate en servidor (imprescindible, y no lo cubre la mitigación):** mover la comprobación de prerrequisito de `POST /api/progress` a un guard compartido y aplicarlo también en `POST /api/activity/:resourceId`, `POST /api/formative/:resourceId`, `POST /api/exams/:resourceId/attempts`, `POST /api/submissions` y `POST /api/tfm/enroll`; y marcar `GET /api/courses/:id` como consulta (`readOnly: true`) cuando la asignatura esté bloqueada, en lugar de servirla como si estuviera abierta |

---

## 2. Veredicto explícito

> ## **El problema era B.**

**El estado se pierde antes de llegar al dashboard.** El endpoint que alimenta el dashboard
(`GET /api/courses`) **no devuelve el campo**: `locked` no existe en ningún punto de esa respuesta.
No es que el dashboard lo ignore, es que nunca lo recibe.

Con dos precisiones que conviene dejar por escrito, porque cambian la corrección:

- De las tres variantes que enumera la hipótesis B, la que se cumple es la primera («el endpoint no
  devuelve el campo»). Las otras dos **no**: el mapper no *descarta* un valor que existiera antes
  —nadie lo calcula nunca en ese camino— y la consulta **no** se hace sin contexto: el SQL de
  `coursesForUser()` ya trae `meta.prerequisiteSlug` y el progreso curso a curso. La materia prima
  llega hasta el navegador; lo que no llega es la conclusión.
- **La hipótesis C acierta en el diagnóstico estructural y falla en su segunda mitad.** Es verdad que
  la lógica de cascada existe *solo* dentro del contexto del programa, y ese es el origen del defecto
  (por eso la corrección (a) consiste en sacarla de ahí). Pero C afirma que el listado genérico «ni
  puede ni intenta» calcularla: **no lo intenta, y sí puede**. Todo lo necesario está ya en la misma
  consulta y en las mismas filas. No hay impedimento de contexto: hay una función que no se escribió.

**La hipótesis A queda descartada** con la respuesta cruda de la API: el backend *no* devuelve
`locked` en `/api/courses` (§4, evidencia E3). Lo que sí es cierto —y es un segundo defecto latente,
independiente— es que el dashboard **tampoco sabría leerlo**: `Course` no declara el campo y
`CourseCard` no tiene rama de bloqueo. Si mañana alguien añade `locked` en el backend creyendo que
arregla el dashboard, el dashboard seguirá pintando 12 tarjetas idénticas. Por eso la corrección
mínima tiene dos mitades.

**La hipótesis D queda descartada.** No hay documentación que declare intencional este
comportamiento; toda la documentación afirma lo contrario:

- `MASTER_IEP_INTEGRATION.md:33` — «Gate lineal: cada asignatura se desbloquea al completar la anterior.»
- `frontend/src/pages/MasterIEPPage.tsx:170` — texto visible al usuario: «Cada asignatura se desbloquea al completar el 100 % de la anterior.»
- `backend/simple-server.js:993` — comentario del gate: «si el curso tiene asignatura previa sin terminar, no se avanza».

El dashboard contradice a las tres.

---

## 3. Trazabilidad completa, los dos flujos en paralelo

| Eslabón | Flujo DASHBOARD (`/`) | Flujo MÁSTER (`/master-iep`) |
|---|---|---|
| **Base de datos** | `courses.meta` (JSONB) con `prerequisiteSlug`, `programOrder`, `track`; filas de `progress`. Sin columna de bloqueo. ✅ el dato bruto está | Idéntico: misma tabla, mismas 12 filas. ✅ |
| **Consulta SQL** | `coursesForUser()` `:223-234`: `SELECT c.* … , (subselect) AS total, (subselect) AS completed FROM courses c WHERE c.published`. Trae `meta` completo y el progreso de cada curso. ✅ **el estado es calculable aquí** | Handler `:872-880`: `SELECT c.*, total, completed … WHERE c.meta->>'programSlug' = $1 ORDER BY (c.meta->>'programOrder')::int`. Prácticamente la misma consulta, filtrada por programa. ✅ |
| **Serializador** | `courseSummary()` `:114-137`. Emite `id, slug, kind, title, description, imageUrl, instructorId, published, source, url, note, meta, createdAt, progress`. **❌ AQUÍ SE PIERDE: no calcula ni emite `locked`** | Objeto en línea `:891-903` + bucle `:905-907`: `a.locked = !!(a.prerequisiteSlug && (progressBySlug[a.prerequisiteSlug] || 0) < 100)`. ✅ el estado nace aquí |
| **Respuesta de la API** | 29 cursos; los 12 del Máster llevan `meta.prerequisiteSlug`, `meta.programOrder` y `progress`, y **ningún** `locked` (❌) | 4 tramos con 12 asignaturas, cada una con `locked: true\|false` (✅) |
| **Hook / cliente** | `useCourses()` (`useCourses.ts:19-27`) con `interface Course` que declara 8 campos y **no incluye `meta` ni `locked`** (❌ doble pérdida: aunque el backend lo enviara, el tipo lo esconde) | `useProgram()` (`usePrograms.ts:38-47`) con `interface ProgramAsignatura` que declara **`locked: boolean`** en la línea 20 (✅) |
| **Componente** | `CourseCard` (`CourseCard.tsx:3-13`): 5 props, ninguna de estado. Sin rama de bloqueo. Raíz = `<button onClick={() => navigate('/courses/'+id)}>` **siempre habilitado** (❌) | `AsignaturaCard` (`MasterIEPPage.tsx:11-80`): `if (asignatura.locked) return <div …>` — `<div>` no navegable, 🔒 en el título, `bg-gray-100`, `border-dashed`, `opacity-80` y el motivo del bloqueo (✅) |
| **Píxeles** | 12 tarjetas rojas idénticas, todas pulsables, **0 candados** | 2 tarjetas activas + **10 candados** con «Completa "…" para desbloquear» |

El punto de divergencia es inequívoco: **el eslabón «serializador»**. Los dos flujos comparten base de
datos y consultas casi idénticas; se separan al serializar, y ya no vuelven a juntarse. El frontend del
dashboard hereda esa carencia y añade la suya (tipo sin el campo, componente sin la rama).

---

## 4. Evidencia empírica con estudiante recién matriculado

**Entorno levantado de verdad** (no simulado): PostgreSQL 16 local, base de datos `campus_diag` creada
para este diagnóstico, `node db/migrate.js` → 15 migraciones aplicadas, `node db/seed.js` con
`SEED_DEMO_DATA=true` → 30 cursos / 92 módulos / 400 recursos / 217 lecciones / 58 exámenes,
`node simple-server.js` en `PORT=4102`, y `vite` en `5261` apuntando a esa API.
Docker no estaba disponible, de modo que no se usó `docker-compose.yml`; se empleó el PostgreSQL del
sistema. **Nunca se apuntó a la base de producción** (el entorno traía un `DATABASE_URL` de Railway en
las variables; todas las órdenes se ejecutaron con `env -u PGHOST -u PGPORT -u PGUSER -u PGDATABASE
-u PGPASSWORD DATABASE_URL='postgres://postgres:postgres@127.0.0.1:5432/campus_diag'`).

### E1 — Usuario nuevo por la API

```
POST /api/auth/register  {"email":"nuevo-diag-1788895960@example.com","name":"Estudiante Nuevo Diag","password":"Password123"}
→ 201, accessToken de 64 caracteres hex
```

### E2 — Un recién registrado no está matriculado en nada

```json
{"userId":"ec677cb1-e5d4-42b0-9165-61c7b7e60821","totalCourses":0,"averageProgress":0,"courses":{}}
```

`GET /api/progress` sale vacío porque `POST /api/auth/register` no matricula en nada
(`simple-server.js:612-630`: solo inserta en `users` y crea sesión). El dashboard filtra por matrícula
(`Dashboard.tsx:23-24`), así que hasta que el estudiante se matricule no ve tarjetas. Para reproducir
el defecto tal y como se ve en producción se matriculó al usuario nuevo en las 12 asignaturas mediante
`POST /api/enrollments` (el mismo endpoint que usa el flujo real de matriculación), y **a partir de ahí
el dashboard se comporta exactamente igual que con la cuenta sembrada**.

### E3 — `GET /api/courses` (endpoint del dashboard): la asignatura II, bloqueada, servida como abierta

JSON crudo, recortando solo `description` y los campos de texto largo de `meta` (marcados con `...`):

```json
{
  "id": "08460e54-370a-49c2-b4be-8023dd426921",
  "slug": "master-ii",
  "kind": "program",
  "title": "II. Innovación tecnológica: Principales Tecnologías Disruptivas",
  "description": "Las tecnologías disruptivas como ecosistema interconectado, ...",
  "instructorId": "e8d1a890-6ff1-4377-8b34-55a0bb0db17f",
  "published": true,
  "meta": {
    "ects": 6,
    "hours": 30,
    "track": "PRO-essentials",
    "weeks": "Sem. 5–7",
    "mastery": "...",
    "practice": "...",
    "contenidos": ["<8 elementos>"],
    "deliverable": "...",
    "legacyTitle": "Innovación tecnológica: Big Data, IoT, Cloud y Blockchain",
    "programSlug": "master-iep",
    "internalCode": "IEP-II-INTERNO",
    "officialCode": "IEP-II-INTERNO",
    "programOrder": 2,
    "prerequisiteSlug": "master-i"
  },
  "createdAt": "2026-09-08T19:31:46.010Z",
  "progress": { "completed": 0, "total": 15, "percentage": 0 }
}
```

Nótese lo que hay y lo que no: **está** `meta.prerequisiteSlug: "master-i"` y **está** el progreso;
**no está** `locked`. La respuesta lleva los ingredientes y no lleva la conclusión.

Barrido de las 12, mismo usuario, misma llamada:

```
 1 | master-i     | locked=AUSENTE | pct=0 | prereqSlug(en meta)=-
 2 | master-ii    | locked=AUSENTE | pct=0 | prereqSlug(en meta)=master-i
 3 | master-iii   | locked=AUSENTE | pct=0 | prereqSlug(en meta)=master-ii
 …
12 | master-tfm   | locked=AUSENTE | pct=0 | prereqSlug(en meta)=master-xi
```

Comprobación de nombres alternativos sobre los 29 cursos devueltos:
`algún item con campo locked/isLocked/available?: false`.

### E4 — `GET /api/programs/master-iep` (endpoint del Máster): el mismo usuario, el mismo instante

```json
{
  "id": "08460e54-370a-49c2-b4be-8023dd426921",
  "slug": "master-ii",
  "title": "II. Innovación tecnológica: Principales Tecnologías Disruptivas",
  "track": "PRO-essentials",
  "programOrder": 2,
  "prerequisiteSlug": "master-i",
  "internalCode": "IEP-II-INTERNO",
  "officialCode": "IEP-II-INTERNO",
  "ects": 6,
  "contenidos": ["<8 elementos>"],
  "progress": { "completed": 0, "total": 15, "percentage": 0 },
  "locked": true
}
```

Mismo `id`, mismo `progress`, y aquí sí `"locked": true`. Barrido completo:

```
 1 | master-i     | locked=false | pct=0 | prereq=-
 2 | master-ii    | locked=true  | pct=0 | prereq=master-i
 3 | master-iii   | locked=true  | pct=0 | prereq=master-ii
 …
12 | master-tfm   | locked=true  | pct=0 | prereq=master-xi
```

**Estado esperado para un recién llegado: I desbloqueada, II a XI y TFM bloqueadas. Es exactamente lo
que dice `/api/programs/master-iep` y exactamente lo que `/api/courses` no dice.**

### E5 — La cuenta sembrada reproduce el síntoma reportado

`test@example.com` (matriculada por el seed en 16 cursos):

```
test@example.com -> matriculado en 16 cursos; tarjetas "En Progreso": 16
de ellas, asignaturas del máster: 12
con campo locked en /api/courses: 0
bloqueadas según /api/programs: 11 de 12
```

---

## 5. Validación de la cascada

Se completó la Asignatura I para el usuario nuevo. **Se hizo manipulando directamente la tabla
`progress`** (y se deja constancia expresa): completar las 15 lecciones por la API habría exigido
entregar 15 actividades y aprobar 15 quizzes, porque `POST /api/progress` rechaza las lecciones con
formativo (`:985-991`) y el completado real lo decide `recomputeLessonProgress()` (`:501-534`).

```sql
INSERT INTO progress (user_id, resource_id, completed)
SELECT '<uuid del usuario>', r.id, true
  FROM resources r JOIN modules m ON m.id=r.module_id JOIN courses c ON c.id=m.course_id
 WHERE c.slug='master-i'
ON CONFLICT (user_id, resource_id) DO UPDATE SET completed = true, completed_at = now();
-- INSERT 0 15   →   master-i: 15/15   |   master-ii: 0/15
```

Antes de eso, el gate de escritura del backend se comportó como debía:

```
POST /api/progress {"resourceId":"<recurso de master-ii>"}
HTTP/1.1 403 Forbidden
{"message":"Completa \"master-i\" para avanzar en esta asignatura."}
```

Después de completar la I:

```
--- /api/courses (dashboard) ---            --- /api/programs/master-iep (Máster) ---
 1 | master-i     | locked=AUSENTE | pct=100     1 | master-i     | locked=false | pct=100
 2 | master-ii    | locked=AUSENTE | pct=0       2 | master-ii    | locked=false | pct=0
 3 | master-iii   | locked=AUSENTE | pct=0       3 | master-iii   | locked=true  | pct=0
 4 | master-iv    | locked=AUSENTE | pct=0       4 | master-iv    | locked=true  | pct=0
desbloqueadas (Máster): master-i, master-ii
```

Y el gate se abrió sin intervención:

```
POST /api/progress {"resourceId":"<el mismo recurso de master-ii>"}
HTTP/1.1 200 OK
{"ok":true}
```

**Conclusión de esta fase: la cascada funciona.** Se desbloquea la II al terminar la I, ni una más.
Y **los dos flujos divergen en ese mismo instante**: el Máster pasa de 11 bloqueadas a 10, y el
dashboard no cambia nada porque nunca supo que hubiera algo bloqueado. **Esa divergencia, medida sobre
el mismo usuario y el mismo `id` de curso, es la prueba central del diagnóstico.**

### Verificación en píxeles (Vite + Chromium headless, sesión real del usuario nuevo)

| Vista | Resultado medido |
|---|---|
| `/` (Dashboard) | 12 tarjetas de asignatura (11 en «En Progreso» + la I en «Completados»), todas navegables, **0 apariciones de 🔒**, 0 textos «para desbloquear» |
| `/master-iep` | **10 apariciones de 🔒** y 10 textos «para desbloquear», contador «2 Desbloqueadas» |

Capturas guardadas fuera del repositorio, en `/tmp/diag-evidencia/shot-01-dashboard.png` y
`shot-02-master-iep.png`. En la primera se ven las once tarjetas rojas idénticas (II … XI + TFM);
en la segunda, las mismas asignaturas en gris con candado. Misma sesión, mismo minuto, misma base de datos.

---

## 6. Riesgo residual

La mitigación en curso (dejar de listar las asignaturas en el dashboard) **no toca ninguno de los dos
eslabones rotos**: `courseSummary` sigue sin emitir `locked` y `CourseCard` sigue sin saber pintarlo.
Retira una de las puertas; el resto siguen abiertas. Por orden de gravedad:

1. **`GET /api/courses/:id` sirve una asignatura bloqueada como si estuviera abierta.** Medido:
   `GET /api/courses/master-ii` con la I al 0 % → **HTTP 200**, con `modules: 3` y 15 recursos, y sin
   campo `locked` en el detalle. Cualquiera con la URL `/courses/master-ii` entra. No hace falta el
   dashboard: basta teclear la ruta, seguir un enlace antiguo o un marcador.
2. **El gate de prerrequisito solo existe en `POST /api/progress`, y es evitable.** Grep de
   `prerequisiteSlug` en todo el backend: dos apariciones, `:894` (cálculo para el Máster) y `:994`
   (gate). Todo lo demás escribe sin comprobar nada. Verificado en vivo sobre `master-iv`, bloqueada
   (prerrequisito `master-iii` al 0 %) para el usuario nuevo:

   ```
   POST /api/activity/<lección de master-iv>        → HTTP 200
   POST /api/formative/<lección de master-iv>       → {"score":3,"maxScore":3,"passed":true}
   fila en progress para esa lección                 → t   (¡creada!)
   estado del Máster tras esto                       → {"slug":"master-iv","locked":true,"progress":{"completed":1,"total":14,"percentage":7}}
   POST /api/exams/<examen de master-iv>/attempts   → {"attemptNo":1,"preguntas":15}
   ```

   Es decir: `recomputeLessonProgress()` (`:501-534`) inserta en `progress` **saltándose** el gate que
   `POST /api/progress` sí aplica, y el motor de exámenes reparte un intento de 15 preguntas de una
   asignatura bloqueada. Se acumula progreso en una asignatura marcada como bloqueada (`locked:true` con
   `percentage:7` en la propia respuesta del Máster: un estado incoherente ya observable).
3. **`ExploreCoursesPage`** (`frontend/src/pages/ExploreCoursesPage.tsx:8`, `:97-105`) consume el mismo
   `useCourses()` y el mismo `CourseCard`, y además **no filtra por matrícula**: muestra los 29 cursos
   publicados, con las 12 asignaturas entre ellos, todas abiertas. El propio dashboard tiene el botón
   «Explorar Cursos» (`Dashboard.tsx:76-81`). **Esta es la reaparición inmediata y garantizada del
   defecto en cuanto se retiren las tarjetas del panel.**
4. **App móvil, `mobile/src/screens/DashboardScreen.tsx`.** Llama a `useCourses.getCourses()`
   (`mobile/src/hooks/useCourses.ts:34` → `GET /api/courses`) y filtra únicamente
   `courses.filter(c => c.progress.percentage < 100)`: **ni por matrícula ni por bloqueo**. Su
   `interface Course` tampoco declara `locked`. Es el mismo defecto, en peor grado, y además con
   **caché en `AsyncStorage`** (`COURSES_CACHE_KEY`), de modo que el listado sobreviviría offline a
   cualquier corrección de servidor hasta que se refresque.
5. **El buscador de `ExploreCoursesPage`** filtra en cliente por título y descripción sobre esa misma
   lista, así que buscar «Machine Learning» devuelve la asignatura VI abierta aunque esté bloqueada.
6. **Panel de instructor** (`InstructorDashboard.tsx:18`, `:24`): mismo `useCourses()`, filtrado por
   `c.instructorId === user?.id`. No es un fallo de cara al estudiante (un instructor debe ver sus
   asignaturas), pero es un cuarto consumidor del endpoint sin noción de bloqueo, y hereda el defecto
   si algún día se reutiliza para vistas de alumno.
7. **`ReviewPlan`** (`GET /api/me/review-plan`, `simple-server.js:1728-1762`) propone lecciones de
   refuerzo por `skill_mastery` y navega a `/courses/:slug/:resourceId` sin consultar el bloqueo; si un
   alumno acumula intentos en una asignatura bloqueada (posible, por el punto 2), el propio campus le
   ofrecerá el enlace de entrada.
8. **`POST /api/tfm/enroll`** (`:1413-1422`) no comprueba la XI: el TFM se puede matricular sin haber
   terminado el programa.
9. **Riesgo de diseño, el que hará que esto vuelva:** hay **dos** representaciones del catálogo
   (`courseSummary` y el objeto de asignatura del programa) y **dos** tarjetas (`CourseCard` y
   `AsignaturaCard`), sin tipo común ni prueba que las compare. Cualquier vista nueva que llame a
   `GET /api/courses` reintroducirá el defecto sin que nada avise: es exactamente lo que ya pasó cuatro
   veces (dashboard web, Explorar, buscador, móvil).

---

## 7. Acta del hallazgo

Registro para seguimiento. **Este defecto NO debe cerrarse por el hecho de que las tarjetas dejen de
mostrarse en el dashboard.**

**Título.** El estado de bloqueo de las asignaturas del Máster IEP no existe en `GET /api/courses`, de
modo que todo listado genérico de cursos las presenta como disponibles.

**Causa raíz.** La cascada de prerrequisitos está implementada como un bucle de tres líneas en el
interior del handler `GET /api/programs/:slug` (`backend/simple-server.js:905-907`) en lugar de estar
modelada como dato o como función compartida. El serializador del catálogo, `courseSummary()`
(`:114-137`), usado por `coursesForUser()` (`:216-236`) y por tanto por `GET /api/courses`, no lo
calcula ni lo emite. Como agravante independiente, el contrato del frontend para ese endpoint
(`interface Course`, `frontend/src/hooks/useCourses.ts:4-17`) no declara el campo y `CourseCard` no
tiene rama de render para el estado bloqueado.

**Comportamiento observado.** Un estudiante matriculado ve las 12 asignaturas (11 del plan + TFM) como
tarjetas idénticas y todas accesibles en el dashboard, mientras `/master-iep` muestra correctamente 11
de 12 con candado para ese mismo usuario en ese mismo momento. Al completar la Asignatura I, el Máster
desbloquea la II y el dashboard no cambia porque nunca reflejó bloqueo alguno.

**Evidencia.** §4 y §5 de este informe: respuestas JSON crudas de los dos endpoints para un usuario
registrado por API (`POST /api/auth/register`) contra un entorno local completo (15 migraciones + seed
+ servidor); `locked` presente y correcto en `/api/programs/master-iep`, inexistente en `/api/courses`
(comprobado también para `isLocked`, `available`, `accessStatus`); 403 y posterior 200 del gate de
`POST /api/progress` demostrando que la cascada sí funciona en el servidor; conteo en píxeles: 0
candados en el dashboard frente a 10 en el Máster, misma sesión.

**Mitigación aplicada (por otro agente, en paralelo).** Retirar las 12 asignaturas del listado del
dashboard filtrando por `meta.programSlug === 'master-iep'`, dejando `/master-iep` como única puerta de
entrada. Entregada como serie de parches en `parches-campus-posgrado-v2/dashboard/`
(`0001-fix-dashboard-…`, `0002-feat-dashboard-…`) sobre `main` en `632bf7a`. **Es una mitigación de
superficie, correcta en su objetivo y suficiente para el síntoma reportado, que no corrige la causa
raíz:** tras aplicarla, `GET /api/courses` sigue devolviendo las 12 asignaturas sin `locked` y
`CourseCard` sigue sin saber representarlo.

**Riesgo residual.** Detallado en §6. Resumen: el defecto reaparece tal cual en `ExploreCoursesPage`
(accesible desde el propio dashboard, y sin filtro de matrícula), en su buscador y en el dashboard de la
app móvil (que además cachea el listado); la entrada directa por URL a una asignatura bloqueada
funciona (`GET /api/courses/:id` → 200 con todo el contenido); y el gate de prerrequisito, que solo
vive en `POST /api/progress`, se puede evitar por `POST /api/activity` + `POST /api/formative`
(que escriben en `progress` a través de `recomputeLessonProgress`) y por `POST /api/exams/:id/attempts`.
Mientras la disponibilidad no se calcule en un único sitio compartido por todos los listados y no se
aplique en servidor a todas las escrituras, cualquier vista nueva que consuma `GET /api/courses`
reintroducirá el defecto sin aviso.

**Estado propuesto.** Mitigado en el dashboard · **causa raíz abierta**.

---

## 8. Reproducibilidad

Entorno usado en este diagnóstico, para quien quiera repetirlo (todo fuera del árbol del repositorio):

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2 /tmp/campus-v2-diagnostico
cd /tmp/campus-v2-diagnostico/backend && npm install
createdb campus_diag   # o: psql -c 'CREATE DATABASE campus_diag;'
export DATABASE_URL='postgres://postgres:postgres@127.0.0.1:5432/campus_diag'
node db/migrate.js && SEED_DEMO_DATA=true node db/seed.js
PORT=4102 node simple-server.js &

# usuario nuevo + los dos endpoints
TOKEN=$(curl -s -X POST localhost:4102/api/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"nuevo@example.com","name":"Nuevo","password":"Password123"}' | jq -r .accessToken)
curl -s localhost:4102/api/courses            -H "Authorization: Bearer $TOKEN" | jq '[.[] | select(.meta.programSlug=="master-iep") | {slug, locked, pct:.progress.percentage}]'
curl -s localhost:4102/api/programs/master-iep -H "Authorization: Bearer $TOKEN" | jq '[.tracks[].asignaturas[] | {slug, locked, pct:.progress.percentage}]'
```

El primer `jq` devuelve `locked: null` en las 12; el segundo, `false` en `master-i` y `true` en las
otras once.
