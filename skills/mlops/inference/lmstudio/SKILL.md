---
name: lmstudio
description: Manage LM Studio local inference server — load/unload models, chat, embeddings, server status, and model discovery.
version: 1.0.0
author: fabek128
platforms: [linux, macos]
metadata:
  hermes:
    tags: [lm-studio, local-llm, inference, model-management, apple-silicon, gguf, mlx]
---

# LM Studio

Use this skill when managing a local LM Studio inference server. Covers model loading/unloading, chat completions, embeddings, server monitoring, and model discovery via the native management API.

> ⚠️ **Two server generations**: LM Studio Express (≤0.2.x, detected via missing management API) only supports OpenAI-compatible endpoints. The Go backend (≥0.3.x) adds the native `/api/v1/models`, `/api/v1/models/load`, and `/api/v1/models/unload` endpoints. The skill auto-detects which version is running.

## When to use

- Switch the active model on LM Studio (unload + load)
- List available models with their capabilities (quant, context, format)
- Run a chat completion against a loaded model
- Generate embeddings for RAG
- Check what models are currently loaded in memory
- Diagnose server connectivity from the Linux host to the Mac running LM Studio
- Get a recommendation for which model to use for a given task

## Quick Start

```bash
# Base URL
HOST="http://<lm-studio-host>:1234"

# Check if reachable
curl -s -o /dev/null -w "%{http_code}" $HOST/v1/models
# Expect: 200

# Check if management API exists (Go backend)
curl -s $HOST/api/v1/models | python3 -c "import json,sys; d=json.load(sys.stdin); print('management: OK' if 'models' in d else 'no')"
```

## Server Info

**Default host** (from this setup): `10.125.115.109:1234` — Mac M1 via VPN ZeroTier.

### Health check (no dedicated endpoint)

Since `/api/v1/health`, `/health`, and `/api/v1/info` do NOT exist on this server version, use:

```bash
# Method 1: check /v1/models as liveness probe
curl -s -o /dev/null -w "%{http_code}" http://10.125.115.109:1234/v1/models
# 200 = alive

# Method 2: check management API availability
curl -s http://10.125.115.109:1234/api/v1/models | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    if 'models' in d: print('✅ Server reachable, management API available')
    else: print('⚠️ Server reachable, unexpected response')
except: print('❌ Server unreachable')
"
```

---

## API Endpoints Reference

### OpenAI-Compatible (all versions)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/models` | GET | List models (IDs only) |
| `/v1/chat/completions` | POST | Chat completion |
| `/v1/completions` | POST | Legacy text completion |
| `/v1/embeddings` | POST | Text embeddings |

### Native Management API (Go backend ≥0.3.x only)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/models` | GET | Detailed model list with loaded state, capabilities |
| `/api/v1/models/load` | POST | Load a model |
| `/api/v1/models/unload` | POST | Unload a model |

> ⚠️ `/api/v1/info`, `/api/v1/status`, `/api/v1/config`, `/api/v1/health` and `/health` do **NOT** exist. They return HTTP 404 with `{"error":"Unexpected endpoint or method."}`.

---

## Tool: Model Management

### List all models (detailed)

```bash
curl -s http://<host>:1234/api/v1/models | python3 -c "
import sys,json
d=json.load(sys.stdin)
for m in d['models']:
    li = m.get('loaded_instances', [])
    status = '🟢 LOADED' if li else '⚪'
    caps = m.get('capabilities', {})
    v = '👁' if caps.get('vision') else ''
    t = '🔧' if caps.get('trained_for_tool_use') else ''
    r = '🧠' if caps.get('reasoning') else ''
    print(f'{status} {m[\"key\"]} ({m[\"params_string\"]}) {m[\"format\"]} {m[\"quantization\"][\"name\"]} ctx={m[\"max_context_length\"]} {v}{t}{r}')
print(f'\nTotal: {len(d[\"models\"])} models')
"
```

Example output:
```
🟢 LOADED mistralai/ministral-3-3b (3B) gguf Q4_K_M ctx=262144 👁🔧
🟢 LOADED carnice-9b (9.0B) gguf Q4_K_M ctx=262144 🔧
⚪ qwen/qwen3-coder-30b (30B) mlx 4bit ctx=262144 🔧
⚪ nvidia/nemotron-3-nano-4b (4.0B) gguf Q4_K_M ctx=1048576 🔧🧠
```

### List only loaded models

```bash
curl -s http://<host>:1234/api/v1/models | python3 -c "
import sys,json
d=json.load(sys.stdin)
for m in d['models']:
    li = m.get('loaded_instances', [])
    if li:
        print(f'{m[\"key\"]} ({m[\"params_string\"]})')
        for inst in li:
            print(f'  instance_id: {inst[\"id\"]}  ctx: {inst[\"config\"][\"context_length\"]}')
"
```

### Load a model

```bash
curl -X POST http://<host>:1234/api/v1/models/load \
  -H "Content-Type: application/json" \
  -d '{"model": "mistralai/ministral-3-3b"}'
```

**Response** (200, load time varies by model size — ~36s for 3B on M1):
```json
{"type": "llm", "instance_id": "mistralai/ministral-3-3b", "load_time_seconds": 36.287, "status": "loaded"}
```

**Error** (resource exhaustion):
```json
{"error": {"type": "model_load_failed", "message": "Failed to load LLM '...': Error: Model loading was stopped due to insufficient system resources..."}}
```

### Unload a model

```bash
curl -X POST http://<host>:1234/api/v1/models/unload \
  -H "Content-Type: application/json" \
  -d '{"instance_id": "mistralai/ministral-3-3b"}'
```

**Response** (200, instantaneous):
```json
{"instance_id": "mistralai/ministral-3-3b"}
```

**Error** (missing field):
```json
{"error": {"message": "Missing required field 'instance_id'", "type": "invalid_request", "param": "instance_id"}}
```

### Switch model (unload + load)

```bash
# Step 1: find loaded models
LOADED=$(curl -s http://<host>:1234/api/v1/models | python3 -c "
import sys,json
d=json.load(sys.stdin)
for m in d['models']:
    for inst in m.get('loaded_instances', []):
        print(inst['id'])
")

# Step 2: unload each
for id in $LOADED; do
  curl -s -X POST http://<host>:1234/api/v1/models/unload \
    -H "Content-Type: application/json" \
    -d "{\"instance_id\": \"$id\"}"
done

# Step 3: load target
curl -s -X POST http://<host>:1234/api/v1/models/load \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen/qwen3-coder-30b"}'
```

Or use the Python script `scripts/switch_model.py` for a cleaner approach.

---

## Tool: Chat Completion

```bash
curl -s http://<host>:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistralai/ministral-3-3b",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7,
    "max_tokens": 2048
  }' | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d['choices'][0]['message']['content'])
"
```

**Parameters supported**: `model`, `messages`, `temperature`, `max_tokens`, `top_p`, `stop`, `frequency_penalty`, `presence_penalty`, `seed`.

**Streaming**: Set `"stream": true` in the request body for SSE streaming (not recommended from terminal() — use for CLI testing only).

---

## Tool: Embeddings

```bash
curl -s http://<host>:1234/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-nomic-embed-text-v1.5",
    "input": "The text to embed"
  }' | python3 -c "
import sys,json
d=json.load(sys.stdin)
vec = d['data'][0]['embedding']
print(f'Vector dimension: {len(vec)}')
print(f'First 5 values: {vec[:5]}')
"
```

Available embedding models:
- `text-embedding-nomic-embed-text-v1.5` (335M, dim=768, ctx=2048, Q4_K_M)
- `text-embedding-qwen3-embedding-8b` (8B, dim=4096, ctx=40k, Q4_K_M)

---

## Tool: Text Completion (Legacy)

```bash
curl -s http://<host>:1234/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistralai/ministral-3-3b",
    "prompt": "Once upon a time",
    "max_tokens": 100
  }'
```

---

## Model Recommendation by Task

| Task | Best Model | Why |
|------|-----------|-----|
| **Coding** | `qwen/qwen3-coder-30b` | 30B, trained for tool use, large context |
| **Reasoning** | `deepseek/deepseek-r1-0528-qwen3-8b` | Native reasoning, MLX optimized |
| **Chat / Agent** | `carnice-9b` | 9B, tool use capable, fast |
| **Vision** | `mistralai/ministral-3-3b` or `google/gemma-4-e4b` | Vision + tool use |
| **Embedding (RAG)** | `text-embedding-qwen3-embedding-8b` | 8k dim, 40k context, high quality |
| **Small/Quick** | `mistralai/ministral-3-3b` | 3B, fast, vision+tool use |
| **Long context** | `nvidia/nemotron-3-nano-4b` | 1M context, reasoning+tool use |

---

## Complete Models Table (Current Server)

| Model | Params | Format | Quant | Context | Vision | Tools | Reasoning |
|-------|--------|--------|-------|---------|:-----:|:-----:|:---------:|
| mistralai/ministral-3-3b | 3B | GGUF | Q4_K_M | 262k | ✅ | ✅ | ❌ |
| carnice-9b | 9.0B | GGUF | Q4_K_M | 262k | ❌ | ✅ | ❌ |
| text-embedding-qwen3-embedding-8b | 8B | GGUF | Q4_K_M | 40k | ❌ | ❌ | ❌ |
| text-embedding-mxbai-embed-large-v1 | 335M | GGUF | F16 | 512 | ❌ | ❌ | ❌ |
| qwen/qwen3-coder-30b | 30B | MLX | 4bit | 262k | ❌ | ✅ | ❌ |
| qwen/qwen2.5-coder-14b | 14B | MLX | 4bit | 32k | ❌ | ❌ | ❌ |
| nvidia/nemotron-3-nano-4b | 4.0B | GGUF | Q4_K_M | 1M | ❌ | ✅ | ✅ |
| google/gemma-4-e4b | 7.5B | GGUF | Q4_K_M | 131k | ✅ | ✅ | ✅ |
| deepseek/deepseek-r1-0528-qwen3-8b | 8B | MLX | 4bit | 131k | ❌ | ❌ | ✅ |
| text-embedding-nomic-embed-text-v1.5 | 335M | GGUF | Q4_K_M | 2k | ❌ | ❌ | ❌ |

---

## Scripts

### `scripts/probe_server.py`

Detects server version and capabilities. Run before any other operation to know what's available:

```bash
python3 ~/.hermes/skills/devops/lmstudio/scripts/probe_server.py [--host http://<host>:1234]
```

Output:
```
Server: 10.125.115.109:1234
Status: ✅ Reachable
Version: Go backend (≥0.3.x)
Management API: ✅ Available
Models: 10 total, 3 loaded
```

### `scripts/switch_model.py`

Switches the active model: unloads all current models, loads the target:

```bash
python3 ~/.hermes/skills/devops/lmstudio/scripts/switch_model.py --target qwen/qwen3-coder-30b [--host http://<host>:1234]
```

---

## Error Handling

| Scenario | Symptom | Action |
|----------|---------|--------|
| Server not running | `curl: (7) Connection refused` | Open LM Studio on the Mac, start the local server |
| Wrong host/IP | Timeout or connection refused | Verify the ZeroTier IP: `ping 10.125.115.109` |
| No model loaded | Chat/embed returns 404 or error | Load a model first with `POST /api/v1/models/load` |
| Insufficient resources | `model_load_failed` error | Unload current model(s), then load target |
| Management API missing | `/api/v1/models` returns 404 | Server is Express build; use GUI for model management |
| Model name typo | Load succeeds but `model_load_failed` | Match model ID exactly from `/api/v1/models` output |
| Timeout on load | Command hangs >60s | Larger models (30B) take 1-2 minutes; increase timeout |

## Pitfalls

- **Only 1 model at a time** on Mac M1 32GB for models ≥7B. Always unload before loading.
- **No single "switch" endpoint**. Switch = unload(all) + load(target) sequentially.
- **Multiple instance_ids**: Some models have multiple instances (e.g. `mistralai/ministral-3-3b` and `mistralai/ministral-3-3b:2`). Unload each one.
- **Model names are case-sensitive**. Must match exactly what `/api/v1/models` returns.
- **Load time varies**: 3B ~36s, 8B ~60s, 30B ~2min on M1. Set timeouts accordingly.
- **No health endpoint**: Use `/v1/models` as liveness probe instead.

## References

- `references/lm-studio-api.md` — Full API reference with request/response examples
- `references/model-capabilities.md` — Model comparison table and task mapping
