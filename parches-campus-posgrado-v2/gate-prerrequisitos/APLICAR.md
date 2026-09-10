# Gate de prerrequisitos del Máster IEP — cómo aplicar esta serie

El agente **no tiene permiso de escritura** en
`edilsonalvarez-create/campus-posgrado-v2`. Comprobado al empezar:

```
$ git push --dry-run
remote: Permission to edilsonalvarez-create/campus-posgrado-v2.git denied to cursor[bot].
fatal: unable to access 'https://github.com/edilsonalvarez-create/campus-posgrado-v2/': The requested URL returned error: 403
```

Son **4 commits sobre `main` en `632bf7a`**.

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/gate-prerrequisitos-9b8f main
git am /ruta/a/gate-prerrequisitos/*.patch
git push -u origin cursor/gate-prerrequisitos-9b8f
```

Si ya aplicaste `dashboard/`, lee **[Orden respecto a `dashboard/`](#orden-respecto-a-dashboard)**:
hay un conflicto de una sola pieza y se resuelve en dos minutos.

---

## El problema

El Máster IEP tiene una cascada lineal —11 asignaturas + TFM, cada una con
`courses.meta->>'prerequisiteSlug'` apuntando a la anterior— que **era
decorativa**.

`locked` se calculaba en un bucle de tres líneas dentro del handler del
programa, y esa era la única vez que alguien miraba la cascada para pintar algo:

```js
for (const a of asignaturas) {
  a.locked = !!(a.prerequisiteSlug && (progressBySlug[a.prerequisiteSlug] || 0) < 100);
}
```

El único control real en todo el backend estaba en `POST /api/progress`, y se
esquivaba sin esfuerzo. Con una cuenta recién registrada, sobre la Asignatura II
(bloqueada, prerrequisito `master-i` al 0 %):

```
### 2. GET /api/courses/master-ii (URL directa)
HTTP 200
{"title":"II. Innovación tecnológica: Principales Tecnologías Disruptivas","modulos":3,"recursos":15}

### 3. POST /api/progress (recurso "book")
HTTP 403
{"message":"Completa \"master-i\" para avanzar en esta asignatura."}

### 4. POST /api/activity/:resourceId (entrega de actividad)
HTTP 200
{"ok":true}

### 5. POST /api/formative/:resourceId (quiz formativo con la clave)
HTTP 200
{"score":3,"maxScore":3,"passed":true,...}

### 6. Efecto: ¿la lección de la asignatura bloqueada quedó completada?
{"completed":true,"progresoCurso":{"completed":1,"total":15,"percentage":7}}

### 7b. POST /api/exams/:id/attempts (abrir intento de examen)
HTTP 200
{"attemptId":"17f2611c-af0c-44d8-9bf2-1d836c3b2da2","preguntas":15}

### 8. POST /api/submissions (entregar el proyecto)
HTTP 201

### 9. POST /api/quiz-responses (vía legada)
HTTP 200
```

El 403 de la puerta principal era irrelevante: al lado había cinco puertas
abiertas, y dos de ellas (`/formative` y `/quiz-responses`) **insertan en
`progress`**, que es justo el dato del que depende toda la cascada.

## La semántica elegida: consultar sí, avanzar no

El commit `7aed5bf` («feat(ui): modo consulta para asignaturas bloqueadas
(P-17)») introdujo deliberadamente la posibilidad de ojear una asignatura
bloqueada, y su propio mensaje fija el contrato:

> El backend ya sirve el detalle de un curso bloqueado (solo las escrituras
> —progreso, examen, entrega— están vetadas por prerrequisito), así que basta
> la entrada en la UI.

Cerrar el agujero con un 403 en la lectura habría **roto una funcionalidad
intencional**: el botón «👁️ Ver en modo consulta →» de `MasterIEPPage` y el
banner ámbar de `CourseView` se habrían quedado apuntando a una pantalla de
error. Así que la regla es la que el producto ya prometía, solo que ahora de
verdad:

| Acción | Antes | Ahora |
|---|---|---|
| **Leer** una asignatura bloqueada | 200, sin decir que está bloqueada | **200**, con `locked`, `lockedReason` y el prerrequisito |
| **Avanzar** en ella | 200 por cinco rutas distintas | **403 `PREREQUISITE_LOCKED`** |

«Avanzar» es todo lo que deja rastro de aprovechamiento: registrar progreso,
entregar la actividad, responder el quiz formativo, abrir o entregar un intento
de examen, entregar el proyecto y matricularse o entregar hitos del TFM.

Lo que **no** se bloquea, porque leer no es avanzar: el detalle del curso, el
tutor, el foro, la posición de lectura (`PUT /courses/:id/resume`), la telemetría
(`POST /events`) y la matrícula (`POST /enrollments`, que no acredita nada).

## Una sola validación

Toda la regla vive en **`backend/lib/prerequisites.js`** y nadie más la
reimplementa. El núcleo es una función sin E/S, para que el mismo criterio sirva
tanto en un listado (una consulta para N cursos) como en la comprobación puntual
de una escritura:

```js
function evaluate({ prerequisiteSlug, prerequisiteTitle, prerequisiteTotal, prerequisiteCompleted }, user) {
  if (!prerequisiteSlug || isExemptRole(user)) return UNLOCKED;
  const total = Number(prerequisiteTotal || 0);
  const done = Number(prerequisiteCompleted || 0);
  const percentage = total > 0 ? Math.round((done / total) * 100) : 100;
  const locked = total > 0 && done < total;
  return { locked, lockedReason: locked ? lockedReason(prerequisiteTitle, prerequisiteSlug) : null, ... };
}
```

Alrededor, tres guardas de ruta que dejan el handler en una línea:

```js
if (await gate.denyResource(sendJSON, res, resourceId, user)) return;
if (await gate.denyCourse(sendJSON, res, course.id, user)) return;
if (await gate.denyCourseSlug(sendJSON, res, 'master-tfm', user)) return;
```

Criterio: **el prerrequisito directo debe estar al 100 % de sus recursos**. Es el
mismo que ya usaban el handler del programa y `POST /api/progress`, así que no
cambia lo que se ve, solo pasa a aplicarse. Una asignatura previa sin recursos no
bloquea: sería una trampa sin salida.

Roles exentos: `instructor`, `admin` y `director_tfm`. Un instructor sigue viendo
las 12 asignaturas abiertas, en el listado, en el programa y en el detalle, y
puede abrir sus exámenes para probarlos.

## Ficheros que toca cada commit

### `0001` — backend

| Fichero | Qué cambia |
|---|---|
| `backend/lib/prerequisites.js` | **Nuevo.** La regla completa: `evaluate`, `evaluateRow`, `stateForCourse/Slug/Resource`, las guardas `denyCourse/denyCourseSlug/denyResource`, los roles exentos y los fragmentos SQL reutilizables. |
| `backend/simple-server.js` | `courseSummary()` serializa `locked`; `coursesForUser()` resuelve las cifras del prerrequisito en la misma consulta (sin N+1); `GET /courses/:id`, `/native-courses/:id` y `/exams/:id/status` adjuntan el estado; el handler del programa deja de calcularlo por su cuenta; ocho rutas de escritura llaman a la guarda. `POST /api/progress` pierde sus 16 líneas de lógica duplicada. |

### `0002` — web

| Fichero | Qué cambia |
|---|---|
| `frontend/src/hooks/useCourses.ts` | `Course` declara `locked`, `lockedReason`, `prerequisiteSlug`, `prerequisiteTitle`, `prerequisitePercentage`. Sin esto, el `locked` del backend no lo veía nadie. |
| `frontend/src/hooks/usePrograms.ts` | `ProgramAsignatura` añade `lockedReason` y `prerequisiteTitle`. |
| `frontend/src/components/CourseCard.tsx` | Rama de render para bloqueado: 🔒, atenuada, con el motivo, y navega a `?preview=1` en vez de al modo trabajo. |
| `frontend/src/pages/ExploreCoursesPage.tsx` | Pasa el estado a la tarjeta y cuenta las bloqueadas. |
| `frontend/src/pages/CourseView.tsx` | El banner de modo consulta ya no depende solo de `?preview=1`: si el backend dice `locked`, se avisa igual. `ExamRunner`, `SubmissionForm`, `HandsOnSubmission`, `TfmMilestones`, `LessonFormative` y el botón de marcar completada se sustituyen por un aviso; el material de alrededor se sigue mostrando. |

### `0003` — móvil

| Fichero | Qué cambia |
|---|---|
| `mobile/src/hooks/cachePolicy.ts` | **Nuevo**, sin dependencias de React Native. Decide si una entrada de AsyncStorage sirve. `CACHE_VERSION = 2`, TTL de 5 min. |
| `mobile/src/hooks/cache.ts` | **Nuevo.** La E/S contra AsyncStorage e `invalidateCourseCache()`. |
| `mobile/src/hooks/useCourses.ts` | Deja de servir la caché a ciegas; revalida por detrás; solo cae a la copia rancia si la petición falla. |
| `mobile/src/hooks/useAuth.ts` | Interceptor: un 403 `PREREQUISITE_LOCKED` borra la caché en el acto. El logout también. |
| `mobile/src/screens/DashboardScreen.tsx` | Tarjeta bloqueada con 🔒, motivo y entrada en modo consulta. Tirar para refrescar salta la caché. |
| `mobile/scripts/cache-gate-check.mjs` | **Nuevo.** Arnés de verificación de la caché. |

### `0004` — CI

| Fichero | Qué cambia |
|---|---|
| `backend/scripts/gate-check.mjs` | **Nuevo.** 30 comprobaciones end-to-end de la cascada y de las vías de evasión. |
| `backend/package.json` | Script `gate-check`. |
| `.github/workflows/ci.yml` | Dos pasos nuevos tras el smoke: `npm run gate-check` y el arnés de la caché del móvil. |

## Endpoints afectados

### Escrituras: ahora 403 `PREREQUISITE_LOCKED`

| Endpoint | Antes | Ahora |
|---|---|---|
| `POST /api/progress` | 403 con `{message}` suelto | **403** `{code, message, prerequisiteSlug, prerequisiteTitle, prerequisitePercentage}` |
| `POST /api/activity/:resourceId` | 200 | **403** |
| `POST /api/formative/:resourceId` | 200 (e insertaba en `progress`) | **403** |
| `POST /api/exams/:resourceId/attempts` | 200 con 15 preguntas | **403** |
| `POST /api/exams/attempts/:attemptId` | 200 | **403** (defensa para intentos abiertos antes del gate) |
| `POST /api/submissions` | 201 | **403** |
| `POST /api/quiz-responses` | 200 (e insertaba en `progress`) | **403** |
| `POST /api/tfm/enroll` | 200 | **403** |
| `POST /api/tfm/milestones/:slug` | 200 | **403** |

Cuerpo del 403:

```json
{
  "code": "PREREQUISITE_LOCKED",
  "message": "Para avanzar en esta asignatura primero debes completar «I. Artificial Intelligence» al 100 %. Puedes consultar el material, pero no registrar progreso, entregar ni examinarte.",
  "prerequisiteSlug": "master-i",
  "prerequisiteTitle": "I. Artificial Intelligence",
  "prerequisitePercentage": 0
}
```

### Lecturas: siguen en 200, pero declaran el estado

| Endpoint | Qué añade |
|---|---|
| `GET /api/courses` | `locked`, `lockedReason`, `prerequisiteSlug`, `prerequisiteTitle`, `prerequisitePercentage` en cada elemento |
| `GET /api/courses/:id` | los mismos campos en el detalle |
| `GET /api/native-courses` y `/:id` | los mismos campos |
| `GET /api/programs/:slug` | `lockedReason` y `prerequisiteTitle` junto al `locked` que ya había |
| `GET /api/exams/:resourceId/status` | `locked`, `lockedReason`, `prerequisiteSlug`, `prerequisiteTitle`, y **`canStart: false`** si está bloqueado |

Ningún endpoint cambia de código de estado en la lectura, y ninguno deja de
servir contenido. Es el modo consulta de P-17, ahora explícito en el contrato.

## Verificación

Entorno completo en local: PostgreSQL 16 real, base creada de cero, **15
migraciones** (aplicadas dos veces, la segunda «nada que aplicar»), **seed dos
veces** (idempotente: 30 cursos / 92 módulos / 400 recursos / 217 lecciones / 58
exámenes las dos), backend en `:3001` y Vite en `:5173`. Es exactamente la
secuencia del workflow `ci.yml` que añadieron `bd42283` / `0bb0fb5`.

```
$ cd backend && BASE=http://localhost:3001/api node scripts/smoke.mjs
15 ok, 0 fallo(s)

$ npm run gate-check
30 ok, 0 fallo(s)

$ cd mobile && node --experimental-strip-types scripts/cache-gate-check.mjs
14 ok, 0 fallo(s)

$ npm --prefix frontend run type-check   → correcto
$ npm --prefix frontend run build        → correcto (✓ built in 6.5s)
```

`npm --prefix frontend run lint` sigue sin poder ejecutarse: el proyecto no tiene
fichero de configuración de ESLint. Es un problema previo, ajeno a esta serie, y
el workflow de CI tampoco lo invoca.

### Salida completa de `gate-check`

```
1. Estudiante nuevo: solo la Asignatura I está abierta
  ✓ master-i abierta
  ✓ II–XI y TFM bloqueadas
  ✓ el bloqueo viene con motivo legible

2. El listado genérico (Explorar Cursos / móvil) declara locked
  ✓ GET /courses serializa el campo locked
  ✓ GET /courses: I abierta, II bloqueada
  ✓ GET /courses: nombra el prerrequisito incumplido

3. Modo consulta (P-17): leer una asignatura bloqueada sigue dando 200
  ✓ GET /courses/master-ii → 200 (URL directa)
  ✓ el detalle se declara bloqueado
  ✓ el material se sirve completo

4. Vías de evasión desde una asignatura bloqueada: todas 403
  ✓ POST /progress → 403 PREREQUISITE_LOCKED
  ✓ POST /activity/:id → 403
  ✓ POST /formative/:id (con la clave correcta) → 403
  ✓ POST /exams/:id/attempts → 403 (no se abre el examen de 15 preguntas)
  ✓ POST /submissions → 403
  ✓ POST /quiz-responses (vía legada) → 403
  ✓ POST /tfm/enroll → 403
  ✓ POST /tfm/milestones/:slug → 403
  ✓ GET /exams/:id/status: canStart=false y locked=true

5. Ninguna de esas llamadas dejó progreso
  ✓ master-ii sigue en 0 recursos completados

6. Instructor: exento del gate
  ✓ GET /courses: el instructor no ve bloqueos
  ✓ GET /programs: el instructor ve las 12 abiertas
  ✓ GET /exams/:id/status: sin bloqueo para el instructor

7. Cascada: al completar la I se abre la II
  ✓ master-i al 100 % (15/15)
  ✓ master-ii se abrió
  ✓ master-iii sigue bloqueada
  ✓ ahora sí se puede abrir el examen de la II

8. Segundo escalón: al completar la II se abre la III
  ✓ master-ii al 100 % (15/15)
  ✓ master-iii se abrió
  ✓ master-iv sigue bloqueada
  ✓ la IV sigue devolviendo 403 en las escrituras

30 ok, 0 fallo(s)
```

La cascada se recorre por las vías reales del producto: las lecciones se
completan entregando la actividad y aprobando el quiz formativo, el proyecto lo
califica el instructor con ≥ 70 y el examen se aprueba respondiendo el intento.
El arnés lee la clave del banco de ítems directamente de la base, porque un
script no puede estudiarse la asignatura; es la única concesión, y no escribe
nada fuera de la API.

### Caché del móvil

```
1. Entradas de caché que deben descartarse
  ✓ formato antiguo sin versión → se borra
  ✓ versión anterior → se borra (versión 1 ≠ 2)
  ✓ caducada → no se sirve, pero se conserva para modo offline
  ✓ JSON corrupto → se borra
  ✓ sin entrada → nada que servir

2. Entradas que sí valen
  ✓ entrada v2 fresca → se sirve
  ✓ entrada caducada en modo offline → se sirve marcada como rancia

3. Caché sucia: bloqueada en el servidor, guardada como abierta
  ✓ un catálogo sin `locked` en una asignatura con prerrequisito NO es fiable
  ✓ un catálogo que declara `locked` sí es fiable

4. Lo que el móvil recibe hoy de la API
  ✓ GET /courses devuelve 12 asignaturas del Máster
  ✓ el payload real pasa el control de fiabilidad de la caché
  ✓ master-ii llega al móvil marcada como bloqueada
  ✓ llega con el motivo para pintarlo en la tarjeta

5. Aunque la caché mintiera, el servidor no cede
  ✓ una escritura desde el móvil con caché sucia → 403

14 ok, 0 fallo(s)
```

El caso que preocupaba —un estado bloqueado guardado en AsyncStorage como
abierto— queda cubierto por tres capas: la caché escrita antes de este cambio es
de otra versión y se borra entera; una entrada que no declare `locked` en una
asignatura con prerrequisito se considera no fiable aunque la versión cuadre; y
si aun así el móvil intentara escribir, recibe 403 y el interceptor tira la caché
en ese mismo momento. Sin conexión no se puede escribir, así que una copia rancia
nunca llega a abrir nada.

### Navegador

Chromium sobre Vite, con la sesión real de un estudiante recién registrado:

- `captura-1-explorar-cursos-con-cascada.png` — «Explorar Cursos» con «29 cursos
  encontrados · 🔒 11 bloqueados por la cascada del Máster (se pueden
  consultar)». La I en rojo, las demás atenuadas con su motivo.
- `captura-2-url-directa-modo-consulta.png` — entrar a `/courses/master-ii` **sin
  `?preview=1`** muestra el banner ámbar de modo consulta y el material completo.
- `captura-3-examen-bloqueado.png` — el examen de la II muestra «🔒 El examen de
  la asignatura no disponible todavía» en lugar del `ExamRunner`.
- `captura-4-explorar-tras-completar-I.png` — tras completar la I: contador a 10
  bloqueados, la II abierta al 0 %, la III todavía cerrada.
- `captura-5-master-iep-tras-completar-II.png` — «3 Desbloqueadas», I y II al
  100 %, III abierta, IV en adelante con candado.
- `captura-6-asignatura-i-sin-banner.png` — la Asignatura I no muestra ningún
  banner: sin regresión para lo que ya estaba abierto.

## Orden respecto a `dashboard/`

Las dos series tocan `frontend/src/hooks/useCourses.ts` y **chocan en los dos
sentidos**. Comprobado:

| Orden | Resultado |
|---|---|
| `dashboard` → `gate` con `git am` | conflicto en `useCourses.ts` |
| `gate` → `dashboard` con `git am` | conflicto en `useCourses.ts` |
| **`dashboard` → `gate` con `git am -3`** | **conflicto de una sola pieza, trivial** |

Los otros lotes no estorban: `plantillas/` no toca el frontend, y `deploy/` y
`limpieza/` están marcados como obsoletos.

### Resolución recomendada

Aplica primero `dashboard/` (ya está entregado y documentado) y luego esta serie
con merge a tres bandas:

```bash
git checkout -b cursor/gate-prerrequisitos-9b8f main
git am -3 /ruta/a/dashboard/*.patch          # limpio
git am -3 /ruta/a/gate-prerrequisitos/*.patch # se para en 0002
```

El conflicto es **puramente aditivo**: cada serie añade campos distintos a
`interface Course`. Se resuelve quedándose con **los dos lados**. El resultado
correcto es:

```ts
export interface Course {
  id: string
  slug?: string
  kind?: string
  title: string
  description: string
  imageUrl?: string
  published: boolean
  instructorId?: string
  modules?: any[]
  meta?: CourseMeta
  /**
   * Cascada de prerrequisitos del Máster. Lo calcula el backend
   * (backend/lib/prerequisites.js) y viene en TODAS las vistas de curso.
   * `locked` no oculta el material —se puede consultar— pero avanzar
   * (progreso, entregas, quizzes, exámenes) devuelve 403 PREREQUISITE_LOCKED.
   */
  locked?: boolean
  lockedReason?: string | null
  prerequisiteSlug?: string | null
  prerequisiteTitle?: string | null
  prerequisitePercentage?: number | null
  progress: {
    completed: number
    total: number
    percentage: number
  }
}
```

```bash
git add frontend/src/hooks/useCourses.ts
git am --continue
```

El árbol combinado se verificó entero: `git log` con los 6 commits (2 de
`dashboard` + 4 de esta serie) sobre `632bf7a`, `type-check` y `build` correctos,
**smoke 15/15** y **gate-check 30/30** contra PostgreSQL real.

Las dos series encajan bien de fondo, no solo de forma. `dashboard/` quitó las 12
asignaturas del panel principal porque el catálogo no traía `locked`; ahora lo
trae, así que esa decisión pasa de ser un parche a ser una elección de
navegación: el panel no las lista porque el Máster se cursa desde `/master-iep`,
no porque no hubiera manera de pintar el candado.

Ese mismo `dashboard/APLICAR.md` dejaba escrito lo que faltaba:

> «Explorar Cursos» sigue listando las 12 asignaturas del Máster sin marca de
> bloqueo […] si se quiere cerrarla también en el catálogo, lo coherente sería
> que `CourseCard` reciba el estado de bloqueo.

Es exactamente lo que hace `0002`.

## Antes de desplegar

El inventario de estudiantes afectados está en
[`ESTUDIANTES-AFECTADOS.md`](./ESTUDIANTES-AFECTADOS.md), con la consulta SQL
lista para correr. **Resultado: 0 estudiantes afectados en producción**, así que
la serie se puede desplegar sin migración de compatibilidad. Aun así, ahí están
las cuatro opciones de derechos adquiridos por si el inventario cambia entre hoy
y el despliegue: conviene volver a correr la consulta justo antes de mergear.
