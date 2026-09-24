-- Consulta B (red más amplia): CUALQUIER rastro de actividad de un estudiante
-- en una asignatura del Máster cuyo prerrequisito directo no esté al 100 %,
-- aunque no haya dejado fila en `progress` (intentos de examen suspensos,
-- entregas sin calificar, quiz formativo no superado, actividades sueltas).
-- ESTRICTAMENTE DE SOLO LECTURA.
WITH asig AS (
  SELECT c.id, c.slug, c.title, (c.meta->>'programOrder')::int AS orden,
         c.meta->>'prerequisiteSlug' AS prereq_slug
  FROM courses c WHERE c.meta->>'programSlug' = 'master-iep'
),
totales AS (
  SELECT a.id AS course_id, count(r.id) AS total
  FROM asig a JOIN modules m ON m.course_id = a.id JOIN resources r ON r.module_id = m.id
  GROUP BY a.id
),
completado AS (
  SELECT p.user_id, m.course_id, count(*) AS n
  FROM progress p JOIN resources r ON r.id = p.resource_id JOIN modules m ON m.id = r.module_id
  WHERE p.completed GROUP BY 1, 2
),
pct AS (
  SELECT a.id AS course_id, u.id AS user_id,
         floor(COALESCE(co.n, 0) * 100.0 / NULLIF(t.total, 0))::int AS pct
  FROM asig a CROSS JOIN users u
  JOIN totales t ON t.course_id = a.id
  LEFT JOIN completado co ON co.course_id = a.id AND co.user_id = u.id
  WHERE u.role = 'student'
),
actividad AS (
  SELECT p.user_id, m.course_id, 'progress' AS rastro, count(*) AS n
    FROM progress p JOIN resources r ON r.id = p.resource_id JOIN modules m ON m.id = r.module_id
   GROUP BY 1,2
  UNION ALL
  SELECT ea.user_id, m.course_id, 'exam_attempt', count(*)
    FROM exam_attempts ea JOIN resources r ON r.id = ea.resource_id JOIN modules m ON m.id = r.module_id
   GROUP BY 1,2
  UNION ALL
  SELECT s.user_id, s.course_id, 'submission', count(*)
    FROM submissions s WHERE s.course_id IS NOT NULL GROUP BY 1,2
  UNION ALL
  SELECT fr.user_id, m.course_id, 'formative', count(*)
    FROM formative_responses fr JOIN resources r ON r.id = fr.resource_id JOIN modules m ON m.id = r.module_id
   GROUP BY 1,2
  UNION ALL
  SELECT asu.user_id, m.course_id, 'activity', count(*)
    FROM activity_submissions asu JOIN resources r ON r.id = asu.resource_id JOIN modules m ON m.id = r.module_id
   GROUP BY 1,2
  UNION ALL
  SELECT qr.user_id, m.course_id, 'quiz_response', count(*)
    FROM quiz_responses qr JOIN resources r ON r.id = qr.resource_id JOIN modules m ON m.id = r.module_id
   GROUP BY 1,2
)
SELECT u.email, a.orden AS n_asignatura, a.slug AS asignatura,
       act.rastro, act.n AS cuantos,
       a.prereq_slug AS prerrequisito_incumplido,
       COALESCE(pp.pct, 0) AS pct_del_prerrequisito
FROM actividad act
JOIN asig a  ON a.id = act.course_id
JOIN users u ON u.id = act.user_id AND u.role = 'student'
JOIN asig pa ON pa.slug = a.prereq_slug
LEFT JOIN pct pp ON pp.course_id = pa.id AND pp.user_id = act.user_id
WHERE COALESCE(pp.pct, 0) < 100
ORDER BY a.orden DESC, u.email, act.rastro;
