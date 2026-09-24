# `actividad-leccion/` — el textarea de Actividad no arrastra texto entre lecciones

Un parche sobre `main` en `bde8fb7`.

## El bug

Al pasar de una lección a otra (por ejemplo Carril A → Carril B de la Unidad 2),
el apartado **Actividad (20 min)** seguía mostrando el texto escrito en la
lección anterior, con el botón en **✓ Guardada**. El backend guarda cada
entrega por `resource_id` y responde bien; el fallo era solo de React:

1. `CourseView` reutiliza `LessonFormative` cuando cambia `resource.id`
   (mismo componente, misma posición, sin `key`).
2. El `useEffect` solo escribía el textarea **si** la lección nueva ya tenía
   una entrega. Si no la tenía, no tocaba el estado y quedaba el texto viejo.

## El arreglo

- `LessonFormative` reinicia textarea, «Guardada», respuestas del quiz y
  resultado al cambiar de `resourceId`, y rellena solo con la entrega de
  **esa** lección (o vacío).
- `CourseView` remonta el cuerpo de la lección, el tutor y el formulario
  formativo con `key` del recurso, para que no se reutilice estado local.

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/fix-actividad-leccion-21ab main
git am /ruta/a/actividad-leccion/*.patch
git push -u origin cursor/fix-actividad-leccion-21ab
```

Independiente del resto de lotes: solo toca
`frontend/src/components/LessonFormative.tsx` y
`frontend/src/pages/CourseView.tsx`.
