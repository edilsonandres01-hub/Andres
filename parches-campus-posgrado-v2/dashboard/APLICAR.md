# Cómo aplicar esta serie de parches

El agente **no tiene permiso de escritura** en
`edilsonalvarez-create/campus-posgrado-v2` (`git push --dry-run` devuelve
`403 Permission to edilsonalvarez-create/campus-posgrado-v2.git denied to cursor[bot]`),
así que el trabajo se entrega como parches en lugar de como rama remota.

Son 2 commits sobre `main` en **`632bf7a`** (el `HEAD` de `main` cuando se generaron;
los lotes anteriores de esta carpeta se hicieron sobre `860cd00`, que ya quedó atrás).

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/dashboard-sin-asignaturas-del-master-bfca main
git am /ruta/a/dashboard/*.patch
git push -u origin cursor/dashboard-sin-asignaturas-del-master-bfca
```

Comprobado: `git am` aplica los 2 parches sin conflictos sobre un clon limpio de
`main` en `632bf7a` y produce el árbol que se verificó en vivo. Si algo fallara,
`git am --abort` deja el repositorio como estaba.

## El problema

El panel principal listaba las 12 asignaturas del Máster IEP (las 11 del plan
oficial + el TFM) como tarjetas sueltas, mezcladas con las aulas, la biblioteca y
los cursos nativos. Dos consecuencias:

1. **Acceso duplicado.** El panel ya tenía un bloque rojo de acceso al Máster que
   lleva a `/master-iep`; las 12 tarjetas eran una segunda puerta al mismo sitio.
2. **La cascada de desbloqueo se saltaba.** El campo `locked` solo lo calcula
   `GET /api/programs/:slug`, comparando el progreso del prerrequisito
   (`meta.prerequisiteSlug`) con el 100 %. `GET /api/courses` —que es lo que
   alimenta el panel— no devuelve `locked`, y `CourseCard` navega a
   `/courses/:id` sin condiciones. Resultado: con la cuenta de prueba, donde
   `GET /api/programs/master-iep` devuelve `locked: true` en 11 de las 12
   asignaturas, el panel las pintaba **todas iguales y todas abiertas**. Ni el
   backend ni `CourseView` bloquean nada: el candado es únicamente de interfaz y
   solo lo respeta `MasterIEPPage`.

Al dejar de listarlas en el panel, la única vía de entrada vuelve a ser
`/master-iep`, que sí aplica la cascada.

## El criterio de datos

La pertenencia al Máster se decide por **`courses.meta->>'programSlug' = 'master-iep'`**,
que es la misma relación que usa `GET /api/programs/:slug` para armar el programa y
`evaluateTrackAndProgramme` para emitir los certificados de tramo. No se filtra por
título, por numeral romano ni por `kind`:

- `kind = 'program'` **no** sirve: `modulo-puente-mlops` es `kind='program'` sin
  `programSlug` (es una adición propia del campus, no del pensum oficial) y debe
  seguir apareciendo como curso suelto.
- El resto del catálogo (`aula`, `library`, `native`) no tiene `programSlug` y no
  se ve afectado.

Comprobado contra la API real: de los 29 cursos publicados, exactamente 12 traen
`meta.programSlug = 'master-iep'` (`master-i` … `master-xi`, `master-tfm`, con
`programOrder` 1..12).

## Dónde va el filtro y por qué en el cliente

`GET /api/courses` es el **catálogo compartido**: lo consumen el panel
(`Dashboard.tsx`), «Explorar Cursos» (`ExploreCoursesPage.tsx`) y el listado del
panel de instructor (`InstructorDashboard.tsx`), los tres a través del mismo hook
`useCourses()`. Filtrar en el servidor habría vaciado también el catálogo de
«Explorar Cursos» y dejado al instructor sin sus asignaturas para gestionar, que es
justo lo que no se quería romper.

Como `courseSummary()` ya incluye `meta` en la respuesta, el cliente tiene el dato
de pertenencia sin tocar la API. El filtro queda en `Dashboard.tsx`, con el
predicado compartido `belongsToProgram()` en `hooks/useCourses.ts` para que la
regla viva en un solo sitio.

**Sin cambios en el backend.** `GET /api/programs/master-iep` sigue devolviendo sus
12 elementos y `smoke.mjs` sigue en 15/15.

## Los 2 commits

| # | Commit |
|---|---|
| 0001 | `fix(dashboard)`: las asignaturas del Máster solo se ven dentro del programa |
| 0002 | `feat(dashboard)`: progreso agregado del Máster en su tarjeta de acceso |

`0001` añade `CourseMeta`, `Course.meta` y `belongsToProgram()` a
`hooks/useCourses.ts`, excluye las asignaturas de programa de «En Progreso» y
«Completados», y corrige los contadores de la bienvenida (decían «matriculado en 16
de 29» mientras se listaban 4).

`0002` enriquece el bloque rojo del Máster que **ya existía** —no se duplica— con el
progreso del programa completo: asignaturas terminadas sobre las 11 del plan, el
porcentaje global de `GET /api/programs/master-iep` con su barra, el recuento de
lecciones y cuál es la siguiente asignatura desbloqueada. Mismo lenguaje visual
(Tailwind, rojo primario); no se rediseña nada más.

## Qué se ve ahora en el panel

- **Bloque del Máster** (uno solo) → `/master-iep`, con «1 de 11 asignaturas
  completadas · 8 %», la barra, «15/177 lecciones» y «Siguiente: II. Innovación
  tecnológica: Principales Tecnologías Disruptivas».
- **Recurso complementario**: Cursos Nativos (sin cambios).
- **En Progreso**: solo los cursos sueltos matriculados — AI for Everyone, Elements
  of AI, Biblioteca del Máster, Fundamentos de Inteligencia Artificial — con un
  subtítulo que aclara dónde se cursan las asignaturas del Máster.
- Ninguna de las 12 asignaturas aparece como tarjeta suelta.

Ver `captura-1-dashboard-sin-asignaturas.png`,
`captura-2-dashboard-con-asignatura-i-completa.png`,
`captura-3-master-iep-cascada-intacta.png` y
`captura-4-asignatura-i-abierta.png`.

## Verificaciones realizadas

Todo contra PostgreSQL 16 real (base `campus_dash`, 15 migraciones + seed con
`SEED_DEMO_DATA=true`: 30 cursos, 92 módulos, 400 recursos, 217 lecciones, 58
exámenes, 32 matrículas), backend en `:3011` y Vite en `:5199`, navegando con
Chromium sobre la sesión real de `test@example.com` / `Password123`:

**API (`curl` con sesión real)**

- `GET /api/courses` → 29 cursos, 12 con `meta.programSlug='master-iep'`,
  `modulo-puente-mlops` con `kind='program'` y sin `programSlug`.
- `GET /api/programs/master-iep` → `progress {completed:0,total:177,percentage:0}`,
  4 tramos, `master-i` con `locked:false` y las otras 11 con `locked:true`. Tras
  marcar completa la Asignatura I: `percentage:8`, `master-i` al 100 % y
  `master-ii` desbloqueada.

**Navegador**

- Panel: 0 asignaturas del Máster listadas, 1 solo bloque del Máster, progreso
  agregado «0 de 11 asignaturas completadas · 0/177 lecciones · Siguiente:
  I. Artificial Intelligence».
- Tras completar la Asignatura I en la base: «1 de 11 asignaturas completadas ·
  8 % · 15/177 lecciones · Siguiente: II. Innovación tecnológica…», y la
  Asignatura I **no** reaparece en «Completados».
- `/master-iep`: las 12 siguen ahí, 11 con candado 🔒 y su mensaje «Completa "…"
  para desbloquear», el contador «Desbloqueadas: 1» y los 3 certificados + TFM.
- Asignatura I: se abre en `/courses/master-i/<resourceId>`, con la lección
  «IA y Toma de Decisiones Automatizadas» completa (diagrama, vídeos, actividad y
  quiz formativo). 12 entradas de contenido en la barra lateral.
- «Explorar Cursos»: sigue mostrando **29 cursos encontrados**, incluidas las
  asignaturas del Máster y el módulo puente → no se rompió el catálogo.
- Panel de instructor con `instructor@example.com`: sigue mostrando
  «Mis Cursos (29)» con las 12 asignaturas → no se rompió la vista de gestión.
- Modo oscuro (`class="dark"` en `<html>`): el bloque del Máster y las tarjetas se
  siguen viendo igual que antes del cambio.

**Suites**

- `cd backend && BASE=http://localhost:3011/api node scripts/smoke.mjs` →
  **15 ok, 0 fallos**.
- `npm --prefix frontend run type-check` → correcto.
- `npm --prefix frontend run build` → correcto.
- `npm --prefix frontend run lint` no se puede ejecutar: falla en `main` sin este
  cambio porque el proyecto no tiene fichero de configuración de ESLint
  (`ESLint couldn't find a configuration file`). Es un problema previo.

## Orden respecto a los otros lotes de esta carpeta

**Esta serie es independiente.** Toca solo dos ficheros:

- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/hooks/useCourses.ts`

Ninguno de los dos lo toca `deploy/`, `limpieza/` ni `plantillas/`, así que **el
orden es indiferente y no hay conflictos posibles con ellas**. Verificado aplicando
la serie sobre `main` limpio y también sobre un árbol con el parche
`limpieza/0006` ya integrado: `git am` limpio en los dos casos, y
`type-check` + `build` correctos en el árbol combinado.

### Aviso sobre `limpieza/0006` (no es culpa de esta serie)

`limpieza/0006` modifica `frontend/src/pages/MasterIEPPage.tsx` y **ya no aplica
sobre el `main` actual por su cuenta**: `main` avanzó de `860cd00` a `632bf7a` e
incorporó por otra vía el mismo cambio que ese parche introducía. El conflicto es
en el bloque de la referencia interna / ECTS de `AsignaturaCard`:

```
<<<<<<< ours      (main actual: internalCode + ects con render condicional)
=======
>>>>>>> theirs    (limpieza/0006: <p title={codigo.title}>{codigo.text}</p>)
```

Se resuelve quedándose con la versión de `main`, que ya cubre la intención del
parche. Lo mismo pasa con `limpieza/0001`–`0003`: el scaffold NestJS que borraban ya
no existe en `main` y `backend/.env.example` conflictúa. Conviene regenerar el lote
`limpieza/` sobre `632bf7a` antes de aplicarlo.

## Lo que queda fuera de este cambio

«Explorar Cursos» sigue listando las 12 asignaturas del Máster sin marca de
bloqueo, porque es el catálogo completo y el requisito era el panel principal. La
puerta sin candado que quedaba en la pantalla de inicio ya está cerrada; si se
quiere cerrarla también en el catálogo, lo coherente sería que `CourseCard` reciba
el estado de bloqueo, o que «Explorar Cursos» agrupe las asignaturas bajo una
entrada al Máster igual que el panel. Es un cambio aparte y con más superficie.
