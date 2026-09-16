# `preguntas-comprension/` — opciones seleccionables y botón Comprobar respuesta

Un parche sobre `main` en `bde8fb7` (aplica también encima del lote `actividad-leccion/`).

## El bug

Las **Preguntas de comprensión** de la lectura guiada eran una lista de texto
con «Ver respuesta»: no se podía marcar una opción ni comprobarla. El quiz
formativo de la lección sí tenía botón, pero las opciones no se veían como
seleccionables.

## El arreglo

- En la lectura guiada, cada pregunta es un conjunto de botones; hay un
  **Comprobar respuesta** por pregunta, con acierto/error y explicación.
- En «Comprueba tu comprensión» de la lección, cada opción tiene un radio y el
  botón se llama **Comprobar respuesta**.

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/preguntas-comprension-21ab main
git am /ruta/a/preguntas-comprension/*.patch
git push -u origin cursor/preguntas-comprension-21ab
```

Independiente del resto de lotes salvo que comparte
`frontend/src/pages/CourseView.tsx` con `actividad-leccion/`. Si aplicas
ambos, aplica primero `actividad-leccion/` y luego este.
