-- ============================================================================
-- INVENTARIO DE ESTUDIANTES AFECTADOS POR EL GATE DE PRERREQUISITOS
-- Máster IEP (campus-posgrado-v2) — consulta ESTRICTAMENTE DE SOLO LECTURA.
-- No contiene UPDATE / DELETE / INSERT ni DDL.
--
-- Identifica a los estudiantes con progreso en una asignatura cuyo
-- prerrequisito directo NO está al 100 %: son los que, al activar el gate,
-- verían cerrada una asignatura en la que ya habían avanzado.
--
-- Ejecutar con la sesión en solo lectura:
--   SET default_transaction_read_only = on;
--   \i inventario.sql
-- ============================================================================

WITH asig AS (
  SELECT c.id,
         c.slug,
         c.title,
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
  SELECT p.user_id,
         a.id AS course_id,
         count(*) AS recursos_completados
  FROM progress p
  JOIN resources r ON r.id = p.resource_id
  JOIN modules   m ON m.id = r.module_id
  JOIN asig      a ON a.id = m.course_id
  WHERE p.completed
  GROUP BY p.user_id, a.id
),
pct AS (
  SELECT av.user_id,
         a.id AS course_id, a.slug, a.title, a.orden, a.prereq_slug,
         av.recursos_completados,
         t.total_recursos,
         floor(av.recursos_completados * 100.0 / NULLIF(t.total_recursos, 0))::int AS pct
  FROM avance av
  JOIN asig    a ON a.id = av.course_id
  JOIN totales t ON t.course_id = av.course_id
),
-- % del prerrequisito para ese mismo estudiante (0 si nunca lo tocó)
adelantadas AS (
  SELECT p.user_id,
         p.slug            AS asignatura,
         p.title           AS asignatura_titulo,
         p.orden,
         p.pct             AS pct_asignatura,
         p.recursos_completados,
         p.total_recursos,
         p.course_id,
         p.prereq_slug     AS prerrequisito,
         pa.title          AS prerrequisito_titulo,
         COALESCE(pp.pct, 0) AS pct_prerrequisito
  FROM pct p
  JOIN asig pa            ON pa.slug = p.prereq_slug
  LEFT JOIN pct pp        ON pp.user_id = p.user_id AND pp.course_id = pa.id
  WHERE p.prereq_slug IS NOT NULL
    AND COALESCE(pp.pct, 0) < 100      -- <-- el prerrequisito NO está completo
)
SELECT u.email,
       u.name                                   AS estudiante,
       u.role,
       ad.orden                                 AS n_asignatura,
       ad.asignatura,
       ad.asignatura_titulo,
       ad.recursos_completados || '/' || ad.total_recursos || ' (' || ad.pct_asignatura || '%)' AS progreso_en_juego,
       ad.prerrequisito                         AS prerrequisito_incumplido,
       ad.prerrequisito_titulo,
       ad.pct_prerrequisito                     AS pct_del_prerrequisito,
       -- detalle de lo que hay en juego dentro de la asignatura adelantada
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
ORDER BY ad.pct_asignatura DESC,          -- gravedad: cuánto se perdería de vista
         ad.pct_prerrequisito ASC,        -- cuán lejos está de cumplir el requisito
         u.email, ad.orden;
