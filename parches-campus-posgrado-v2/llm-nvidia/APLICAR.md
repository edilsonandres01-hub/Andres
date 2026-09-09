# `llm-nvidia/` — migrar la integración del LLM de Anthropic a NVIDIA NIM

Tres parches sobre `main` en `632bf7a`. Sustituyen Anthropic por el endpoint
OpenAI-compatible de NVIDIA NIM con el modelo `moonshotai/kimi-k3`, **sin retirar
el camino de Anthropic**, y arreglan el problema que un modelo de razonamiento
introduce en las dos funciones que devuelven JSON.

```bash
git clone https://github.com/edilsonalvarez-create/campus-posgrado-v2
cd campus-posgrado-v2
git checkout -b cursor/llm-nvidia-nim-2328 main
git am /ruta/a/llm-nvidia/*.patch
git push -u origin cursor/llm-nvidia-nim-2328
```

## Los tres parches

| # | Commit | Qué hace |
|---|---|---|
| 0001 | `feat(llm)` | Proveedor OpenAI-compatible junto al de Anthropic. Traducción de formato. Clave genérica `LLM_API_KEY`. |
| 0002 | `fix(llm)` | Presupuesto de tokens de razonamiento, detección de truncación, timeout y reintentos. |
| 0003 | `docs(llm)` | `.env.example` y las guías de despliegue; se retiran las referencias a `ANTHROPIC_API_KEY`. |

Ficheros tocados: `backend/lib/llm.js` (el grueso), `backend/.env.example`,
`backend/simple-server.js` (un comentario), `frontend/src/components/GradingPanel.tsx`
(un texto de aviso), `DEPLOY.md`, `DEPLOY_AUTOMATIZADO.md`,
`DEPLOYMENT_QUICK_START.md`, `MASTER_IEP_INTEGRATION.md`.

## Decisiones de diseño

**Nombre del proveedor: `nvidia` *y* `openai-compatible`.** Los dos van por el
mismo transporte. `nvidia` trae la base URL por defecto
(`https://integrate.api.nvidia.com/v1`) para que la configuración de Railway sean
tres variables y no cuatro; `openai-compatible` exige declarar `LLM_BASE_URL` y
sirve para cualquier otro endpoint `/chat/completions` (vLLM, Groq, Together, un
NIM autohospedado) sin volver a tocar el código. Poner solo `nvidia` habría atado
el código a un proveedor; poner solo `openai-compatible` habría obligado a
declarar una URL que en el 100% de los casos actuales es la misma.

**Clave genérica `LLM_API_KEY`, no una por proveedor.** Con una variable por
proveedor, cambiar de motor obliga a añadir una variable y borrar otra, y durante
la transición conviven dos claves de dos servicios distintos: es exactamente la
configuración engañosa que produce el fallo «la clave está puesta pero el
servidor no la lee». Con `LLM_API_KEY` el cambio de proveedor es un único par
`LLM_PROVIDER` + `LLM_API_KEY`. `ANTHROPIC_API_KEY` se sigue leyendo, pero **solo**
con `LLM_PROVIDER=anthropic`, para no romper despliegues antiguos.

## Variables de entorno

| Variable | Def. | Para qué |
|---|---|---|
| `LLM_PROVIDER` | `none` | `none` \| `nvidia` \| `openai-compatible` \| `anthropic` |
| `LLM_API_KEY` | — | **secreto**, clave del proveedor activo |
| `ANTHROPIC_API_KEY` | — | **secreto**, alias histórico; solo con `LLM_PROVIDER=anthropic` |
| `LLM_MODEL` | `moonshotai/kimi-k3` (o `claude-sonnet-5` con anthropic) | tutor y asistencia de nota |
| `LLM_MODEL_HEAVY` | `moonshotai/kimi-k3` (o `claude-opus-5`) | borrador del banco de ítems |
| `LLM_BASE_URL` | NVIDIA con `nvidia`; obligatoria con `openai-compatible` | raíz de la API, sin `/chat/completions` |
| `LLM_MAX_TOKENS_TUTOR` | `3000` (`700` con anthropic) | presupuesto de `tutor()` |
| `LLM_MAX_TOKENS_GRADE` | `6000` (`1200`) | presupuesto de `gradeSuggestion()` |
| `LLM_MAX_TOKENS_ITEMS` | `16000` (`4000`) | presupuesto de `draftItems()` |
| `LLM_REASONING_EFFORT` | vacía | se manda como `reasoning_effort` solo si tiene valor |
| `LLM_TIMEOUT_MS` | `180000` | corta la petición; `fetch` no trae timeout |
| `LLM_MAX_RETRIES` | `2` | reintentos ante 429/5xx, espera exponencial con techo de 20 s |

Ninguna variable anterior cambia de significado. `LLM_PROVIDER=none` sigue siendo
el valor por defecto y la degradación es la de siempre: el tutor devuelve su FAQ
de respaldo y `/api/submissions/:id/grade-suggestion` responde 501 `LLM_DISABLED`.

## El problema de verdad: el razonamiento consume `max_tokens`

`kimi-k3` es un modelo de razonamiento. Devuelve un campo extra
`choices[0].message.reasoning_content` con la cadena de pensamiento, y **ese
pensamiento se paga del mismo presupuesto de `max_tokens` que la respuesta**.
Medido contra la API real: con `max_tokens: 20` y el prompt «responde
exactamente: OK», la respuesta vuelve con `finish_reason: "length"`,
`completion_tokens: 20`, `reasoning_content` de 103 caracteres y `content`
**vacío**. Los 20 tokens se fueron enteros en pensar.

Con los límites heredados de Claude (700 / 1200 / 4000) eso rompe las tres
funciones, y de la peor manera posible en dos de ellas: `gradeSuggestion` y
`draftItems` sacaban el JSON con `raw.match(/\{[\s\S]*\}/)` dentro de un
`try/catch` que devolvía `null` o `[]`. Un JSON cortado a la mitad producía
exactamente el mismo valor que «el modelo no tenía nada que decir»: un fallo mudo.

Lo que hacen los parches:

1. **Presupuestos acordes al modelo y configurables.** 3000 / 6000 / 16000 cuando
   el proveedor es de razonamiento; los 700 / 1200 / 4000 de siempre cuando es
   `anthropic`, para no cambiar el comportamiento del camino que ya existía.
2. **`reasoning_content` se descarta siempre**, en el transporte. No llega al
   usuario ni entra en el `JSON.parse`. Como red adicional se eliminan también los
   bloques `<think>…</think>` en línea, que es como lo devuelven otros modelos.
3. **La truncación se detecta y se grita.** El transporte devuelve
   `{ text, truncated, usage }`, con `truncated` desde `finish_reason === 'length'`
   (o `stop_reason === 'max_tokens'` en Anthropic). `gradeSuggestion` y
   `draftItems` lanzan `LLM_TRUNCATED` con el presupuesto y el consumo reales; una
   salida no parseable lanza `LLM_BAD_JSON`. La ruta de `/grade-suggestion` ya
   convertía las excepciones en **502 con el mensaje**, así que el fallo pasa a ser
   visible sin tocar el servidor. `tutor()` devuelve la respuesta parcial —sigue
   siendo mejor que el fallback genérico— pero deja el aviso en el log.

## Robustez de red

El plan del que sale la clave devuelve **429 `Too Many Requests` con mucha
facilidad**: durante estas pruebas, dos llamadas seguidas a `moonshotai/kimi-k3`
agotaron la cuota y el endpoint respondió 429 durante más de una hora, mientras
`GET /v1/models` seguía devolviendo 200. Por eso 0002 añade reintentos con espera
exponencial (techo de 20 s) ante 429 y 5xx, y un timeout explícito: `fetch` no
trae ninguno y una llamada con 16 000 tokens de presupuesto tarda minutos.

Si el tutor empieza a tardar en producción, mira los 429 en el log antes que
nada; es un límite de cuota del proveedor, no del código.

## Relación con los otros lotes

**Independiente.** Comprobado aplicando los cuatro lotes vigentes sobre `632bf7a`:

```
llm-nvidia → plantillas → dashboard   : los tres limpios
+ gate-prerrequisitos                 : conflicto en frontend/src/hooks/useCourses.ts
```

Ese conflicto es el ya conocido entre `dashboard/` y `gate-prerrequisitos/` y no
tiene nada que ver con este lote: `llm-nvidia` aplicado *encima* de
`gate-prerrequisitos/` solo entra limpio. El único fichero que este lote comparte
con otro es `backend/simple-server.js`, que también toca `gate-prerrequisitos/`,
pero aquí solo se cambia una línea de comentario muy lejos de sus cambios.

Se puede aplicar en cualquier posición del orden. Lo natural es el primero, porque
es el más pequeño y no toca el frontend salvo un literal de texto.

## Después de mergear

Las variables de Railway del servicio de app en producción **ya están puestas**
(`LLM_PROVIDER=nvidia`, `LLM_MODEL` y `LLM_MODEL_HEAVY` a `moonshotai/kimi-k3`,
`LLM_API_KEY` con la clave; `ANTHROPIC_API_KEY` borrada). Hasta que estos parches
entren en `main`, el código desplegado no entiende `LLM_PROVIDER=nvidia` y el
tutor degrada a su FAQ de respaldo: **la configuración está lista pero inerte**.
En cuanto el merge se despliegue, el tutor pasa a responder con kimi-k3 sin
tocar nada más.

**Rota la clave antes de mergear.** La que hay en Railway se compartió por chat.
