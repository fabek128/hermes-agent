# LM Studio API — Referencia Completa

## Base URL

```
http://<host>:1234
```

## OpenAI-Compatible Endpoints

### GET /v1/models

Lista todos los modelos disponibles (formato OpenAI):

```bash
curl http://localhost:1234/v1/models
```

Response:
```json
{
  "data": [
    {"id": "qwen/qwen3-coder-30b", "object": "model", "owned_by": "organization_owner"}
  ],
  "object": "list"
}
```

### POST /v1/chat/completions

Chat completion estándar:

```bash
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistralai/ministral-3-3b",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7,
    "max_tokens": 2048,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  }'
```

Response:
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you today?"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 9,
    "total_tokens": 19
  }
}
```

### Streaming (SSE)

Añadir `"stream": true` para Server-Sent Events:

```bash
curl -N http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "mistralai/ministral-3-3b", "messages": [{"role": "user", "content": "Count to 5"}], "stream": true}'
```

Cada evento SSE:
```
data: {"id":"...","choices":[{"delta":{"content":"1"},"index":0}]}
...
data: [DONE]
```

### POST /v1/completions

Legacy text completion:

```bash
curl http://localhost:1234/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "mistralai/ministral-3-3b", "prompt": "The meaning of life is", "max_tokens": 50}'
```

### POST /v1/embeddings

Genera embeddings:

```bash
curl http://localhost:1234/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-nomic-embed-text-v1.5",
    "input": "Hello world"
  }'
```

Response:
```json
{
  "object": "list",
  "data": [{
    "object": "embedding",
    "index": 0,
    "embedding": [0.123, -0.456, ...]
  }],
  "model": "text-embedding-nomic-embed-text-v1.5",
  "usage": {"prompt_tokens": 2, "total_tokens": 2}
}
```

Batch input (múltiples textos):
```json
{"input": ["text1", "text2", "text3"], "model": "..."}
```

## Native Management API (Go backend ≥0.3.x)

### GET /api/v1/models

Lista detallada con metadatos completos. Respuesta tiene forma `{"models": [...]}`.

Cada modelo incluye:
- `key` — identificador único (usar para `model` en load)
- `publisher` — ej: "qwen", "deepseek"
- `display_name` — nombre legible
- `architecture` — ej: "qwen3_moe", "llama", "gemma4"
- `format` — "mlx" o "gguf"
- `quantization` — `{"name": "4bit", "bits_per_weight": 4}`
- `params_string` — ej: "30B", "8B"
- `size_bytes` — tamaño en disco
- `max_context_length` — ventana de contexto máxima
- `loaded_instances` — array; vacío = no cargado. Cada instancia tiene `id`, `config.context_length`, `config.eval_batch_size`
- `capabilities`:
  - `vision`: boolean
  - `trained_for_tool_use`: boolean
  - `reasoning`: object con `allowed_options` array (si aplica)
- `variants` — array de variantes (ej: `["qwen/qwen3-coder-30b@4bit"]`)
- `selected_variant` — variante activa

### POST /api/v1/models/load

Carga un modelo:

```json
// Request
{"model": "deepseek/deepseek-r1-0528-qwen3-8b"}

// Success (200)
{"type": "llm", "instance_id": "deepseek/deepseek-r1-0528-qwen3-8b", "load_time_seconds": 5.867, "status": "loaded"}

// Error — resource exhaustion (200 con error)
{"error": {"type": "model_load_failed", "message": "Failed to load LLM '...': Error: Model loading was stopped due to insufficient system resources..."}}
```

### POST /api/v1/models/unload

Descarga un modelo:

```json
// Request
{"instance_id": "qwen/qwen3-coder-30b"}

// Success (200)
{"instance_id": "qwen/qwen3-coder-30b"}

// Error — missing field (200)
{"error": {"message": "Missing required field 'instance_id'", "type": "invalid_request", "code": "missing_required_parameter", "param": "instance_id"}}
```

## Endpoints que NO existen

Estos devuelven 404 con `{"error":"Unexpected endpoint or method. (GET/POST <path>)"}`:

- `/api/v1/info` (GET)
- `/api/v1/status` (GET)
- `/api/v1/config` (GET)
- `/api/v1/health` (GET)
- `/health` (GET)
- `/openapi.json` (GET)

## Consideraciones

- **Timeout**: Los modelos grandes (30B) pueden tardar 1-2 minutos en cargar en Mac M1
- **Unload** es instantáneo
- **Contexto práctico**: El `max_context_length` declarado suele ser optimista para modelos grandes. En M1 32GB, un modelo 30B MLX 4bit funciona bien hasta ~16k tokens
- **No hot-swap**: No se puede cargar un modelo mientras otro está cargado (recursos insuficientes). Siempre unload → load
- **Instance IDs múltiples**: Algunos modelos tienen varias instancias (ej: `modelo` y `modelo:2`). Descargar todas antes de cargar otro
