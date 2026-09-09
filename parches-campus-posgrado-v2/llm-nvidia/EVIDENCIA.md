# Evidencia de las pruebas contra la API real de NVIDIA

Todo lo de aquí está medido contra `https://integrate.api.nvidia.com/v1` el
2026-09-09 con la clave de producción (prefijo `nvapi-8eV…`), usando datos reales
del repositorio: la lección **«IA y Toma de Decisiones Automatizadas»**
(`backend/db/seed-data/master-i-lecciones.js`, la primera de la Asignatura I) y la
rúbrica **`rubric-master-i`** (`backend/db/seed-data/rubrics.js`, criterios
`entrada-salida`, `clasificacion`, `automatizacion`, `riesgo-etico`).

## Aviso sobre el modelo usado en cada prueba

**La cuota de `moonshotai/kimi-k3` de esta clave se agotó a mitad del trabajo.**
Tras dos llamadas correctas (01:29 y 01:30 UTC), el endpoint devolvió
`429 Too Many Requests` de forma **continuada durante más de dos horas**, hasta el
final de la sesión. El límite es **por modelo, no por cuenta**: mientras kimi-k3
daba 429, `GET /v1/models` seguía en 200 y `openai/gpt-oss-20b` respondía 200 con
normalidad en el mismo endpoint y con la misma clave.

No es un artefacto de sondear demasiado: se dejó la clave **20 minutos sin ninguna
petición** y el primer intento posterior volvió a dar 429.

Lo que la cuenta puede llamar de verdad tampoco coincide con el catálogo. `GET
/v1/models` lista 81 modelos, pero:

| Modelo | Resultado |
|---|---|
| `moonshotai/kimi-k3` | **429** sostenido |
| `moonshotai/kimi-k2.6` | **404** `Not found for account '5rmdDxPc…'` |
| `openai/gpt-oss-20b` | 200 (y algún 504 puntual bajo carga) |
| `meta/llama-3.1-8b-instruct` | 410 `end of life` |

**Consecuencia operativa:** aunque estos parches se mergeen y se desplieguen, con
esta clave el tutor recibirá 429 de kimi-k3 y degradará a su FAQ de respaldo hasta
que la cuenta recupere cuota o crédito para ese modelo. Rotar la clave —que hay que
hacerlo— **no arregla esto por sí solo**: una clave nueva de la misma cuenta hereda
las mismas cuotas. Como `LLM_MODEL` es una variable de entorno, cambiar a un modelo
con cuota es un cambio de configuración en Railway, sin tocar el código.

Por eso la evidencia está partida:

- **Lo medido con `moonshotai/kimi-k3`**: el comportamiento del presupuesto de
  razonamiento y la aceptación de `reasoning_effort`. Es lo específico del modelo.
- **Lo medido con `openai/gpt-oss-20b`** (otro modelo de razonamiento del **mismo
  endpoint**, elegido porque es el que quedaba con cuota): las tres funciones de
  negocio de principio a fin y las dos rutas HTTP. El transporte, el parseo y la
  detección de truncación son idénticos —`callOpenAICompatible` no sabe qué modelo
  le han pasado—, así que esto valida el camino de código completo.

`gpt-oss-20b` presenta exactamente el mismo comportamiento problemático que
kimi-k3: devuelve `reasoning_content`, ese razonamiento consume `max_tokens`, y
`content` llega a valer **`null`** cuando el presupuesto se agota antes de empezar
a responder.

---

## 1. El razonamiento consume `max_tokens` (kimi-k3)

`max_tokens: 20`, prompt «Responde exactamente: OK»:

```
finish_reason: length
usage: {"prompt_tokens":93,"completion_tokens":20,"total_tokens":113}
message keys: content,role,reasoning_content
reasoning_content: 103 caracteres
content: ""            <- vacío
```

Los 20 tokens se gastaron enteros en pensar. Con `max_tokens: 200` y
`reasoning_effort: "max"` el mismo prompt sí termina:

```
finish_reason: stop
usage: {"prompt_tokens":92,"completion_tokens":66,"total_tokens":158}
reasoning_content: 215 caracteres
content: "OK"
```

El mismo patrón en `openai/gpt-oss-20b` con `max_tokens: 200`:

```
finish_reason: length   completion_tokens: 200
content: None           <- literalmente null en el JSON
reasoning_content: 'The user wrote "di OK". That seems maybe a typo...'
```

Ese `null` es la razón de que el transporte haga `String(raw || '')` en lugar de
confiar en que `content` sea una cadena.

## 2. `reasoning_effort`: el enum lo impone el modelo, no el endpoint

Es el hallazgo que más condiciona la configuración. Mismo endpoint, misma clave,
resultados distintos según el modelo:

| Modelo | `reasoning_effort` | Resultado |
|---|---|---|
| `moonshotai/kimi-k3` | `"max"` | **200** |
| `openai/gpt-oss-20b` | `"max"` | **400** `Input should be 'low', 'medium' or 'high'` |
| `openai/gpt-oss-20b` | `"minimal"` / `"none"` / `"ultra-turbo"` | **400**, mismo mensaje |

En `gpt-oss-20b`, con los valores que sí admite, el efecto sobre el razonamiento
es grande (mismo prompt de calificación, `max_tokens: 3000`):

| `reasoning_effort` | latencia | `completion_tokens` | razonamiento | respuesta |
|---|---|---|---|---|
| *(sin el parámetro)* | 26,2 s | 448 | 1605 c | 366 c |
| `low` | 12,1 s | 301 | 506 c | 753 c |
| `medium` | 19,4 s | 652 | 2125 c | 564 c |
| `high` | 64,9 s | 1786 | 7061 c | 538 c |

De `high` a `low` el razonamiento cae 14×. **Decisión:** `LLM_REASONING_EFFORT`
existe pero va **vacía por defecto** y no se fija por función. Hardcodear el
`"max"` del ejemplo original habría roto con 400 cualquier modelo que no sea
kimi-k3, y un 400 es un error de configuración que el código —correctamente— no
reintenta. Además, el problema que había que resolver era la truncación, y eso lo
arregla el presupuesto de tokens sin sacrificar calidad de respuesta; bajar el
esfuerzo es la palanca para latencia y coste, no para corrección.

## 3. Las tres funciones, con datos reales del repositorio

Modelo `openai/gpt-oss-20b`, presupuestos por defecto (3000 / 6000 / 16000).

### `tutor()` — respeta el prompt y no revela el quiz

Se le pasa la lección completa **incluyendo las respuestas correctas del quiz** y
se le pregunta directamente por ellas:

> **Pregunta:** «En la pregunta 1 del quiz, ¿cuál de las cuatro opciones es la
> correcta? Dímela directamente, tengo prisa.»
>
> **Respuesta:** «¿Has revisado la parte de la lección donde se explica cómo
> evaluar una propuesta de IA? Allí se detalla qué criterios usar para decidir si
> una solución "entiende" al cliente realmente, y cómo formularla en términos de
> entrada‑salida evaluable. Busca esa sección y reflexiona sobre cuál de las
> opciones se alinea con ese marco. ¿Qué pistas te ayudan a descartar las demás
> respuestas?»

En español, socrático, sin revelar la opción correcta y sin filtrar razonamiento.

```
CONSUMO · finish_reason=stop prompt=1415 completion=200 total=1615
          caracteres: razonamiento=234  respuesta=655
```

### `gradeSuggestion()` — JSON con la forma exacta

Entrega evaluada: un memo escrito para la rúbrica, fuerte en entrada/salida y
deliberadamente flojo en el criterio ético (acaba con «hay que vigilar que el
modelo no se equivoque demasiado»).

```
typeof: object | claves: criteria,overall
criteria es array: true | n: 4
keys devueltas: entrada-salida,clasificacion,automatizacion,riesgo-etico
coinciden con la rúbrica: true
forma {key,levelPoints,comment} en todos: true
overall es string: true

CONSUMO · finish_reason=stop prompt=780 completion=1034 total=1814
          caracteres: razonamiento=2549  respuesta=1970
```

El razonamiento (2549 c) es **mayor que la respuesta** (1970 c): con el
presupuesto antiguo de 1200 tokens esta llamada quedaba al filo.

### `draftItems()` — array JSON válido

`n = 3` ítems sobre la misma lección:

```
es array: true | n: 3
todos con la forma esperada: true
  (stem string, options[4], correctIndex entero 0-3, explanations[4],
   difficulty ∈ {baja,media,alta}, cognitive ∈ {aplicacion,analisis})

CONSUMO · finish_reason=stop prompt=816 completion=2462 total=3278
          caracteres: razonamiento=5639  respuesta=4838
```

**2462 tokens de salida para 3 ítems.** La llamada real usa `n = 6`: proyectado,
~5000 tokens, es decir **por encima del límite antiguo de 4000**. Este es el caso
que se truncaba en silencio.

Primer ítem generado (recortado):

```json
{
  "stem": "Un fabricante de turbinas quiere usar IA para predecir fallos de equipos basándose en lecturas de vibración y temperatura...",
  "options": ["Convertir cualquier entrada en un diagnóstico sin datos históricos",
              "Aprender a predecir la probabilidad de fallo futuro a partir de ejemplos históricos",
              "Alterar el firmware del equipo para operación automática sin supervisión",
              "Resolver cualquier problema de ingeniería sin intervención humana"],
  "correctIndex": 1,
  "explanations": ["...", "...", "...", "..."],
  "difficulty": "media",
  "cognitive": "aplicacion"
}
```

## 4. Las rutas HTTP, sobre PostgreSQL real

Servidor local (`simple-server.js`) contra una base sembrada con el seed completo
(217 lecciones, 58 exámenes) y apuntando a NVIDIA.

```
POST /api/tutor/:resourceId                       -> 200  (3m 5s)
  {"answer":"Lo siento, pero no puedo decirte la respuesta directamente.
   Revisa la sección **“Conceptos clave”** y el ejemplo de la lección; allí
   podrás identificar cuál de los criterios define una propuesta de IA como un
   proyecto real. ¿Qué parte de esa definición te resulta más útil...",
   "refused":false,"disabled":false}

POST /api/submissions/:id/grade-suggestion        -> 200  (59s)
  {"suggestion":{"criteria":[
     {"key":"entrada-salida","levelPoints":35,"comment":"...la entrada es el
       texto libre del ticket más metadatos... y la salida es una etiqueta de
       prioridad P1‑P4, cumpliendo con la exigencia de la rúbrica."},
     {"key":"clasificacion","levelPoints":25,"comment":"...clasificación
       supervisada (con 180 000 tickets etiquetados)..."},
     {"key":"automatizacion","levelPoints":20,"comment":"...automatizar solo
       cuando la probabilidad supera 0,85, con revisión trimestral..."},
     {"key":"riesgo-etico","levelPoints":0,"comment":"No se identifica un riesgo
       ético concreto ni su mecanismo..."}],
   "overall":"Competente"}}
```

El 0 en `riesgo-etico` confirma que el modelo está leyendo la entrega y no
rellenando: es justo el criterio que el memo dejaba cojo a propósito.

**Latencia:** 3 minutos para el tutor es mucho para una ruta interactiva. Sale de
un prompt de ~1400 tokens (la lección entera) más el razonamiento del modelo. Es
un argumento a favor de `LLM_REASONING_EFFORT=low` si en producción molesta, y la
razón de que `LLM_TIMEOUT_MS` valga 180000 por defecto.

## 5. La truncación deja de ser un fallo mudo — A/B

Misma petición, misma API, mismo presupuesto deliberadamente corto
(`LLM_MAX_TOKENS_GRADE=200`), lo único que cambia es el código:

```
PARSEO ANTIGUO (try/catch -> null)
  -> 200  {"suggestion":null}

CÓDIGO NUEVO
  -> 502  {"message":"El modelo no respondió: LLM_TRUNCATED: gradeSuggestion
           agotó max_tokens=200 (prompt 741, completion 200). El razonamiento
           del modelo consumió el presupuesto; sube el límite por variable de
           entorno."}
```

Arriba, el instructor ve un panel vacío y no tiene forma de saber por qué. Abajo,
el error dice qué pasó y qué variable tocar.

## 6. Degradación y no-regresión

Con el código nuevo y `LLM_PROVIDER=none`, contra PostgreSQL real:

```
backend/scripts/smoke.mjs   ->  15 ok, 0 fallo(s)
```

Y las funciones devuelven lo mismo que antes sin lanzar nada:

```
enabled()        -> false
tutor()          -> {"text":null,"disabled":true}
gradeSuggestion()-> null
draftItems()     -> []
```

Comprobación de la selección de proveedor:

| `LLM_PROVIDER` | clave | `enabled()` | modelos | presupuestos |
|---|---|---|---|---|
| `none` | — | `false` | — | — |
| `anthropic` | `ANTHROPIC_API_KEY` | `true` | `claude-sonnet-5` / `claude-opus-5` | 700 / 1200 / 4000 |
| `nvidia` | `LLM_API_KEY` | `true` | `moonshotai/kimi-k3` | 3000 / 6000 / 16000 |
| `openai-compatible` sin `LLM_BASE_URL` | `LLM_API_KEY` | `false` | — | — |

La traducción de formato, verificada interceptando la petición saliente:

```
nvidia    -> POST https://integrate.api.nvidia.com/v1/chat/completions
             cabeceras: content-type, authorization
             body: model, max_tokens, messages, stream
             ¿system de primer nivel?: false      messages[0].role: system
anthropic -> POST https://api.anthropic.com/v1/messages
             cabeceras: content-type, x-api-key, anthropic-version
             body: model, max_tokens, system, messages
             ¿system de primer nivel?: true       messages[0].role: user
```

Y con una respuesta que trae `reasoning_content` contaminado a propósito con un
JSON falso, el objeto devuelto **no lo contiene**: el razonamiento se descarta
antes del `JSON.parse`.

## 7. Convivencia con los otros lotes

Los cuatro lotes vigentes aplicados en cadena sobre `632bf7a`:

```
llm-nvidia -> plantillas -> dashboard          los tres limpios
                         -> gate-prerrequisitos  conflicto en
                                                 frontend/src/hooks/useCourses.ts
```

Ese conflicto es el ya documentado entre `dashboard/` y `gate-prerrequisitos/`.
`llm-nvidia` aplicado directamente encima de `gate-prerrequisitos/` entra limpio.
