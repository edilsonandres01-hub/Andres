# `iso-42001/` — Unidad 8 de Ruta de Mando sobre ISO/IEC 42001

Un parche sobre `main` en `bde8fb7`. Independiente de los lotes de frontend
(`actividad-leccion/`, `preguntas-comprension/`): solo toca seed del aula.

## Qué añade

Una **Fase 6 · Gobierno de la IA — ISO/IEC 42001** al final del curso
*Ruta de Mando en Seguridad y QA*, con el mismo esquema de las Fases 0–5:

| Pieza | Igual que el resto del curso |
|---|---|
| Carril A (22 min) | SGIA, relación con 27001, cláusulas 4–10, Anexo A (38 controles), evaluación de impacto, quiz de 3, lectura guiada de 8 términos + caso de 7 pasos + 5 preguntas |
| Carril B (20 min) | ISO/IEC 25059 (extiende 25010), corrección por corte, robustez, intervenibilidad, datos A.7, puerta de calidad, misma lectura guiada |
| Entregable E7 (10 min) | Inventario real de sistemas de IA, alcance del SGIA, impacto del más crítico, puerta de calidad y Declaración de Aplicabilidad preliminar |
| Examen de unidad | 8 preguntas de opción múltiple |

Se añade como **Unidad 8** (después de «Los primeros 30 días») para no
reescribir las `stable_key` ya sembradas (`m1`–`m8`). El seed no destructivo
creará `m9` en el siguiente `AUTO_SEED=sync`.

También se menciona ISO/IEC 42001 Auditor Interno en la lección de tutoría
(Unidad 7), en el mismo espíritu que 27001: solo cuando ya exista un SGIA
real que auditar.

## Cómo aplicar

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/iso-42001-modulo-21ab main
git am /ruta/a/iso-42001/*.patch
git push -u origin cursor/iso-42001-modulo-21ab
```

Tras desplegar la imagen (el seed viaja en `COPY backend/db`), arrancar con
`AUTO_SEED=sync` o ejecutar `npm run seed` para que aparezca el módulo nuevo.

Ficheros tocados:

- `backend/db/seed-data/aula-ruta-mando-unidad-8-iso-42001.js` (nuevo)
- `backend/db/seed-data/aula-ruta-mando-seguridad-qa.js`
- `backend/db/seed-data/aulas.json`
