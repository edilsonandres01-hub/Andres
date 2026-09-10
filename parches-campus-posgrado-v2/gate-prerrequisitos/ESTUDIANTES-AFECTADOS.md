# Inventario de estudiantes afectados por el gate de prerrequisitos

**Resultado: 0 estudiantes afectados.** Ejecutado contra la base de **producción
real** (Railway, proyecto `campus-posgrado-v2`, servicio Postgres, entorno
`production`) el 2026-09-08, con la sesión en solo lectura. Las dos consultas
—la estricta y la de red amplia— devuelven `(0 rows)`.

La serie del gate se puede desplegar **sin migración de compatibilidad ni
cláusula de derechos adquiridos**. Aun así, más abajo quedan las opciones
propuestas por si el inventario cambia entre hoy y el despliegue: lo prudente es
volver a correr la consulta justo antes de mergear.

---

## Cómo se ejecutó

El host `postgres.railway.internal` no es accesible desde fuera de la red privada
de Railway, así que se creó un **proxy TCP temporal** por la API GraphQL:

```graphql
mutation { tcpProxyCreate(input: {
  environmentId: "999addf0-825b-4095-b28a-7291fbf5622a",
  serviceId: "39838d15-e275-4df2-9a99-b2d3d7832faf",
  applicationPort: 5432
}) { id domain proxyPort } }
```

```json
{"data":{"tcpProxyCreate":{"id":"f9c04d91-3106-4a19-81a1-c89f9a9428ac","domain":"altaria.proxy.rlwy.net.","proxyPort":55703,"applicationPort":5432}}}
```

Antes de crearlo se comprobó que **no había ninguno preexistente**
(`{"data":{"tcpProxies":[]}}`), para no tocar infraestructura ajena.

### El proxy quedó eliminado

```json
{"data":{"tcpProxyDelete":true}}
```

Verificado después de borrarlo:

```json
{"data":{"tcpProxies":[]}}
```

### Solo lectura, y demostrado

Todas las sesiones se abrieron con `PGOPTIONS='-c default_transaction_read_only=on'`.
No se ejecutó ningún `UPDATE`, `DELETE`, `INSERT` ni DDL. Comprobación explícita
de que la protección estaba activa —se intentó crear una tabla a propósito y la
base lo rechazó:

```
$ psql ... -c "CREATE TABLE zz_no(x int);"
ERROR:  cannot execute CREATE TABLE in a read-only transaction
```

---

## Lo que hay hoy en producción

```
 usuarios | estudiantes | filas_progress | entregas | intentos | asignaturas
----------+-------------+----------------+----------+----------+-------------
        4 |           3 |              5 |        0 |        2 |          12
```

```
             email              |      name       |    role    | created_at
--------------------------------+-----------------+------------+------------
 instructor@example.com         | Instructor Demo | instructor | 2026-09-04
 test@example.com               | Test User       | student    | 2026-09-04
 smoke1788890800530@example.com | Smoke           | student    | 2026-09-08
 smoke1788884593740@example.com | Smoke           | student    | 2026-09-08
```

Dónde está **todo** el progreso registrado:

```
             email              |         slug         |  programa  | recursos_completados | total
--------------------------------+----------------------+------------+----------------------+-------
 smoke1788884593740@example.com | master-i             | master-iep |                    1 |    15
 smoke1788890800530@example.com | master-i             | master-iep |                    1 |    15
 test@example.com               | aula-ai-for-everyone |            |                    3 |    26
```

Intentos de examen:

```
             email              |   slug   | attempt_no | score | passed |  status
--------------------------------+----------+------------+-------+--------+-----------
 smoke1788884593740@example.com | master-i |          1 |  0.00 | f      | submitted
 smoke1788890800530@example.com | master-i |          1 |  0.00 | f      | submitted
```

Y el resto: 0 certificados, 2 respuestas de quiz formativo, 2 actividades, 0
matrículas de TFM, 32 matrículas.

**Por qué el resultado es 0.** Todo el progreso del Máster está en `master-i`,
que es la primera asignatura y **no tiene prerrequisito**: nunca puede estar
adelantada. Lo de `test@example.com` está en `aula-ai-for-everyone`, un aula
suelta que no pertenece al programa (`meta.programSlug` nulo) y a la que la
cascada no aplica. Los dos usuarios `smoke…@example.com` son de pruebas
automatizadas, no alumnos.

## La consulta

Fichero: [`inventario-estudiantes-afectados.sql`](./inventario-estudiantes-afectados.sql).
Red más amplia: [`inventario-red-amplia.sql`](./inventario-red-amplia.sql).

```sql
-- Estudiantes con progreso en una asignatura cuyo prerrequisito directo NO está
-- al 100 %. ESTRICTAMENTE DE SOLO LECTURA.
--   SET default_transaction_read_only = on;
WITH asig AS (
  SELECT c.id, c.slug, c.title,
         (c.meta->>'programOrder')::int AS orden,
         c.meta->>'prerequisiteSlug'    AS prereq_slug
  FROM courses c
  WHERE c.meta->>'programSlug' = 'master-iep'
),
totales AS (                       -- recursos que tiene cada asignatura
  SELECT a.id AS course_id, count(r.id) AS total_recursos
  FROM asig a
  JOIN modules   m ON m.course_id = a.id
  JOIN resources r ON r.module_id = m.id
  GROUP BY a.id
),
avance AS (                        -- progreso real por (estudiante, asignatura)
  SELECT p.user_id, a.id AS course_id, count(*) AS recursos_completados
  FROM progress p
  JOIN resources r ON r.id = p.resource_id
  JOIN modules   m ON m.id = r.module_id
  JOIN asig      a ON a.id = m.course_id
  WHERE p.completed
  GROUP BY p.user_id, a.id
),
pct AS (
  SELECT av.user_id, a.id AS course_id, a.slug, a.title, a.orden, a.prereq_slug,
         av.recursos_completados, t.total_recursos,
         floor(av.recursos_completados * 100.0 / NULLIF(t.total_recursos, 0))::int AS pct
  FROM avance av
  JOIN asig    a ON a.id = av.course_id
  JOIN totales t ON t.course_id = av.course_id
),
adelantadas AS (
  SELECT p.user_id, p.slug AS asignatura, p.title AS asignatura_titulo, p.orden,
         p.pct AS pct_asignatura, p.recursos_completados, p.total_recursos, p.course_id,
         p.prereq_slug AS prerrequisito, pa.title AS prerrequisito_titulo,
         COALESCE(pp.pct, 0) AS pct_prerrequisito
  FROM pct p
  JOIN asig pa     ON pa.slug = p.prereq_slug
  LEFT JOIN pct pp ON pp.user_id = p.user_id AND pp.course_id = pa.id
  WHERE p.prereq_slug IS NOT NULL
    AND COALESCE(pp.pct, 0) < 100      -- el prerrequisito NO está completo
)
SELECT u.email, u.name AS estudiante, u.role,
       ad.orden AS n_asignatura, ad.asignatura, ad.asignatura_titulo,
       ad.recursos_completados || '/' || ad.total_recursos || ' (' || ad.pct_asignatura || '%)' AS progreso_en_juego,
       ad.prerrequisito AS prerrequisito_incumplido, ad.prerrequisito_titulo,
       ad.pct_prerrequisito AS pct_del_prerrequisito,
       (SELECT count(*) FROM progress p2
          JOIN resources r2 ON r2.id = p2.resource_id
          JOIN modules   m2 ON m2.id = r2.module_id
         WHERE m2.course_id = ad.course_id AND p2.user_id = ad.user_id
           AND p2.completed AND r2.type = 'lesson')                     AS lecciones,
       (SELECT count(*) FROM submissions s
         WHERE s.user_id = ad.user_id AND s.course_id = ad.course_id)   AS entregas,
       (SELECT count(*) FROM exam_attempts ea
          JOIN resources r3 ON r3.id = ea.resource_id
          JOIN modules   m3 ON m3.id = r3.module_id
         WHERE m3.course_id = ad.course_id AND ea.user_id = ad.user_id) AS intentos_examen,
       (SELECT count(*) FROM grades g
          JOIN submissions s2 ON s2.id = g.submission_id
         WHERE s2.user_id = ad.user_id AND s2.course_id = ad.course_id) AS notas,
       (SELECT count(*) FROM certificates ce
         WHERE ce.user_id = ad.user_id AND ce.course_id = ad.course_id) AS certificados
FROM adelantadas ad
JOIN users u ON u.id = ad.user_id
ORDER BY ad.pct_asignatura DESC,     -- gravedad: cuánto progreso se quedaría cerrado
         ad.pct_prerrequisito ASC,   -- cuán lejos está de cumplir el requisito
         u.email, ad.orden;
```

### La consulta está validada, no solo «devuelve cero»

Un `(0 rows)` puede ser un acierto o un fallo de la consulta. Para descartar lo
segundo, la misma consulta se corrió contra una **base local de pruebas** en la
que se sembraron a propósito dos casos adelantados. Los detectó, con el detalle
completo y ordenados por gravedad:

```
-[ RECORD 1 ]------------+----------------------------------------------------------------
email                    | smoke…@example.com
n_asignatura             | 7
asignatura               | master-vii
asignatura_titulo        | VII. Prompts Multimodales y Adaptación a Contextos Complejos
progreso_en_juego        | 12/15 (80%)
prerrequisito_incumplido | master-vi
prerrequisito_titulo     | VI. Machine Learning
pct_del_prerrequisito    | 0
lecciones                | 6
entregas                 | 0
intentos_examen          | 0
notas                    | 0
certificados             | 0
-[ RECORD 2 ]------------+----------------------------------------------------------------
email                    | test@example.com
n_asignatura             | 3
asignatura               | master-iii
asignatura_titulo        | III. Big Data Dentro de la informática
progreso_en_juego        | 4/16 (25%)
prerrequisito_incumplido | master-ii
prerrequisito_titulo     | II. Innovación tecnológica: Principales Tecnologías Disruptivas
pct_del_prerrequisito    | 0
lecciones                | 4
...
```

(Las filas sintéticas se borraron después. Se insertaron en la base **local** de
pruebas; producción no se tocó en ningún momento.)

### Segunda red, más amplia

La consulta principal se apoya en filas de `progress`. Un estudiante podría haber
dejado rastro en una asignatura adelantada **sin** llegar a completar ningún
recurso: un intento de examen suspenso, una entrega sin calificar, un quiz
formativo no superado, una actividad suelta. `inventario-red-amplia.sql` recorre
`progress`, `exam_attempts`, `submissions`, `formative_responses`,
`activity_submissions` y `quiz_responses`. También devuelve `(0 rows)`.

---

## Estrategia de compatibilidad (propuesta, NO ejecutada)

Hoy no hace falta ninguna: **el inventario está vacío y nadie pierde acceso**. Lo
que sigue queda documentado por si el inventario cambia antes del despliegue, o
por si en el futuro se endurece la regla.

Ninguna de estas opciones está implementada ni ejecutada. Es decisión del
usuario.

### A) Cláusula de derechos adquiridos por usuario y curso

Una tabla `prerequisite_grants (user_id, course_id, granted_by, reason,
granted_at)` que `lib/prerequisites.js` consulta antes de bloquear. Se rellena
una sola vez, con el resultado exacto del inventario.

- **A favor.** Quirúrgica y auditable: solo abre lo que ya estaba abierto de
  hecho, deja constancia de quién lo concedió y por qué, y no toca ni una fila de
  `progress`. La regla sigue siendo una sola función.
- **En contra.** Una migración y una consulta más en el camino caliente (se
  resuelve con un índice sobre `(user_id, course_id)` y con la exención en
  memoria para los roles). Hay que decidir si la concesión es permanente o
  caduca.
- **Cuándo.** Es la opción por defecto si el inventario devuelve pocas filas.

### B) Desbloqueo retroactivo del prerrequisito ya superado de facto

Para quien acabó una asignatura posterior sin cerrar la anterior, dar por
superada también la anterior.

- **A favor.** No añade estado nuevo: la cascada queda coherente por sí sola y el
  gate no necesita excepciones.
- **En contra.** **Falsea el expediente.** Escribe en `progress` recursos que el
  estudiante nunca hizo y puede disparar `evaluateCourseCompletion`, emitiendo
  certificados —de asignatura, de tramo y hasta de programa— que no se han
  ganado. Con certificados de por medio es difícil de revertir.
- **Cuándo.** Solo si dirección académica decide expresamente convalidar, y
  entonces mejor como convalidación explícita (opción A con `reason =
  'convalidación'`) que como progreso inventado.

### C) Flag de acceso concedido manualmente

`users.prerequisites_waived boolean` o un rol `student_legacy` exento del gate.

- **A favor.** Trivial de implementar: una condición más en `isExemptRole`.
- **En contra.** Es todo o nada. Abre las 12 asignaturas al estudiante, no solo
  la que tenía adelantada, y deja la cascada sin efecto justo para quien ya
  demostró que se la salta. Además se olvida puesto.
- **Cuándo.** Como salida de emergencia mientras se prepara A, nunca como
  solución final.

### D) Aplicar la regla solo a matrículas posteriores a una fecha

Comparar `enrollments.created_at` (o `users.created_at`) con una fecha de corte.

- **A favor.** Cero estado nuevo, una línea en el gate, y la promesa a los
  alumnos actuales se respeta entera.
- **En contra.** El campus queda con dos reglas conviviendo indefinidamente, y
  eso hay que sostenerlo en el código y explicarlo en soporte. `enrollments` hoy
  tiene 32 filas y no distingue Máster de aulas sueltas, así que la fecha de
  corte sería aproximada.
- **Cuándo.** Si el inventario devolviera muchas filas y no compensara tratarlas
  una a una.

### Recomendación

**Desplegar tal cual.** El inventario está vacío, no hay nada que preservar y
cualquier mecanismo de compatibilidad sería estado muerto desde el primer día.

Si al volver a correr la consulta antes de mergear apareciera alguna fila, la
opción **A** es la adecuada: es la única que preserva el acceso sin falsear el
expediente ni desactivar la cascada.

## Antes de desplegar, repetir esto

```bash
# 1. Crear el proxy TCP (guardar el id que devuelve)
# 2. Ejecutar en solo lectura
PGOPTIONS='-c default_transaction_read_only=on' \
  psql -h <host-proxy> -p <puerto> -U postgres -d railway \
  -x -f inventario-estudiantes-afectados.sql

PGOPTIONS='-c default_transaction_read_only=on' \
  psql -h <host-proxy> -p <puerto> -U postgres -d railway \
  -f inventario-red-amplia.sql

# 3. Borrar el proxy y verificar que no queda ninguno
```
