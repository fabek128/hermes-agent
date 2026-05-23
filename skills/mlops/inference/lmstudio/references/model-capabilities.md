# Model Capabilities — LM Studio Server Actual

Modelos detectados en `10.125.115.109:1234` (Mac M1 32GB).

## Tabla Completa

| # | Modelo | Params | Formato | Quant | Contexto | Visión | Tools | Razonamiento | Cargado |
|---|--------|--------|---------|-------|----------|:-----:|:-----:|:------------:|:-------:|
| 1 | mistralai/ministral-3-3b | 3B | GGUF | Q4_K_M | 262k | ✅ | ✅ | ❌ | 🟢 |
| 2 | carnice-9b | 9.0B | GGUF | Q4_K_M | 262k | ❌ | ✅ | ❌ | 🟢 |
| 3 | text-embedding-qwen3-embedding-8b | 8B | GGUF | Q4_K_M | 40k | ❌ | ❌ | ❌ | ⚪ |
| 4 | text-embedding-mxbai-embed-large-v1 | 335M | GGUF | F16 | 512 | ❌ | ❌ | ❌ | ⚪ |
| 5 | qwen/qwen3-coder-30b | 30B | MLX | 4bit | 262k | ❌ | ✅ | ❌ | ⚪ |
| 6 | qwen/qwen2.5-coder-14b | 14B | MLX | 4bit | 32k | ❌ | ❌ | ❌ | ⚪ |
| 7 | nvidia/nemotron-3-nano-4b | 4.0B | GGUF | Q4_K_M | 1M | ❌ | ✅ | ✅ | ⚪ |
| 8 | google/gemma-4-e4b | 7.5B | GGUF | Q4_K_M | 131k | ✅ | ✅ | ✅ | ⚪ |
| 9 | deepseek/deepseek-r1-0528-qwen3-8b | 8B | MLX | 4bit | 131k | ❌ | ❌ | ✅ | 🟢 |
| 10 | text-embedding-nomic-embed-text-v1.5 | 335M | GGUF | Q4_K_M | 2k | ❌ | ❌ | ❌ | ⚪ |

## Por Capacidad

### Visión
- mistralai/ministral-3-3b (3B, rápido)
- google/gemma-4-e4b (7.5B, mejor calidad)

### Tool Use (function calling)
- mistralai/ministral-3-3b (3B)
- carnice-9b (9B)
- qwen/qwen3-coder-30b (30B, el mejor para código)
- nvidia/nemotron-3-nano-4b (4B)
- google/gemma-4-e4b (7.5B)

### Razonamiento
- nvidia/nemotron-3-nano-4b (4B, 1M contexto)
- google/gemma-4-e4b (7.5B)
- deepseek/deepseek-r1-0528-qwen3-8b (8B, nativo reasoning)

### Embebidos
- text-embedding-nomic-embed-text-v1.5 (335M, 768d, rápido)
- text-embedding-qwen3-embedding-8b (8B, 4096d, alta calidad)

## Task → Best Model Recommendation

| Task | Recommended | Reasoning |
|------|------------|-----------|
| Coding (agentic) | qwen/qwen3-coder-30b | Best code model, tool use |
| Coding (light) | carnice-9b | Tool use, faster load |
| Complex reasoning | deepseek/deepseek-r1-0528-qwen3-8b | Native reasoning chain |
| General chat | carnice-9b or mistralai/ministral-3-3b | Fast, capable |
| Vision analysis | google/gemma-4-e4b | Vision + reasoning |
| RAG embeddings | text-embedding-qwen3-embedding-8b | 4096d, 40k ctx |
| Long context (>200k) | nvidia/nemotron-3-nano-4b | 1M ctx |
| Quick prototyping | mistralai/ministral-3-3b | 3B, fast load |
| Agent with vision | google/gemma-4-e4b | Vision + tool use + reasoning |

## Model Size vs Load Time (estimated on M1)

| Size | Format | Load Time |
|------|--------|-----------|
| 3B GGUF | Q4_K_M | ~30-40s |
| 8B GGUF | Q4_K_M | ~45-60s |
| 8B MLX | 4bit | ~5-10s |
| 9B GGUF | Q4_K_M | ~60-90s |
| 30B MLX | 4bit | ~60-120s |

Los modelos MLX cargan mucho más rápido en Apple Silicon porque aprovechan el神经引擎 y memoria unificada.
