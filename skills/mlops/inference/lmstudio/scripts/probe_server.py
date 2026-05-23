#!/usr/bin/env python3
"""
LM Studio Server Probe — detecta versión, conectividad, modelos cargados.
"""
import json, sys, os, urllib.request, urllib.error, socket
from urllib.parse import urljoin

DEFAULT_HOST = os.environ.get("LMSTUDIO_HOST", "http://10.125.115.109:1234")

def req(method, path, data=None, timeout=10, base_url=None):
    url = urljoin((base_url or DEFAULT_HOST).rstrip("/") + "/", path.lstrip("/"))
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    r.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(r, timeout=timeout)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode()) if e.headers.get("Content-Type","").startswith("application/json") else str(e)
    except (urllib.error.URLError, socket.timeout) as e:
        return 0, f"Connection error: {e}"

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Probe LM Studio server")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Server URL (default: {DEFAULT_HOST})")
    args = parser.parse_args()

    host = args.host.rstrip("/")

    print(f"Server: {host}")
    print()

    # 1. Basic connectivity via /v1/models
    status, data = req("GET", "/v1/models", base_url=host)
    if status == 200:
        models = data.get("data", [])
        print(f"✅ Reachable (OpenAI-compatible API)")
        print(f"   Models (OpenAI): {len(models)}")
    else:
        print(f"❌ Unreachable: {data}")
        sys.exit(1)

    print()

    # 2. Check management API
    status, data = req("GET", "/api/v1/models", base_url=host)
    if status == 200 and "models" in data:
        models = data["models"]
        loaded = [m for m in models if m.get("loaded_instances")]
        print(f"✅ Management API available (Go backend ≥0.3.x)")
        print(f"   Total models: {len(models)}")
        print(f"   Loaded: {len(loaded)}")
        for m in loaded:
            caps = m.get("capabilities", {})
            tags = []
            if caps.get("vision"): tags.append("vision")
            if caps.get("trained_for_tool_use"): tags.append("tool-use")
            if caps.get("reasoning"): tags.append("reasoning")
            tag_str = f" [{', '.join(tags)}]" if tags else ""
            print(f"     🟢 {m['key']} ({m['params_string']}){tag_str}")
    else:
        print(f"⚠️  Management API unavailable (Express build ≤0.2.x)")
        print(f"   Use GUI for model management")

    print()

    # 3. Check /v1/chat/completions
    status, data = req("POST", "/v1/chat/completions", {
        "model": "", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1
    }, timeout=5, base_url=host)
    if status == 200:
        print(f"✅ Chat endpoint responds")
    else:
        print(f"ℹ️  Chat endpoint: {data}")

    print()
    print("---")
    print("Probe complete.")

if __name__ == "__main__":
    main()
