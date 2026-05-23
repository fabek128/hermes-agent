#!/usr/bin/env python3
"""
LM Studio Model Switcher — descarga modelos actuales y carga uno nuevo.
"""
import json, sys, os, urllib.request, urllib.error, socket, time
from urllib.parse import urljoin

DEFAULT_HOST = os.environ.get("LMSTUDIO_HOST", "http://10.125.115.109:1234")

def req(method, path, data=None, timeout=30, base_url=None):
    url = urljoin((base_url or DEFAULT_HOST).rstrip("/") + "/", path.lstrip("/"))
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    r.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(r, timeout=timeout)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        try:
            return e.code, json.loads(err_body)
        except:
            return e.code, err_body
    except (urllib.error.URLError, socket.timeout) as e:
        return 0, {"error": str(e)}

def get_loaded_models(host):
    """Devuelve lista de instance_ids cargados."""
    status, data = req("GET", "/api/v1/models", timeout=10, base_url=host)
    if status != 200 or "models" not in data:
        return None
    loaded = []
    for m in data["models"]:
        for inst in m.get("loaded_instances", []):
            loaded.append(inst["id"])
    return loaded

def unload_model(host, instance_id):
    """Descarga un modelo por instance_id."""
    print(f"  Descargando {instance_id}...", end=" ")
    sys.stdout.flush()
    status, data = req("POST", "/api/v1/models/unload",
                       {"instance_id": instance_id}, timeout=15, base_url=host)
    if status == 200 and "error" not in data:
        print(f"✅")
        return True
    else:
        err = data.get("error", {}).get("message", data)
        print(f"❌ {err}")
        return False

def load_model(host, model_id):
    """Carga un modelo por ID."""
    print(f"  Cargando {model_id}...", end=" ")
    sys.stdout.flush()
    status, data = req("POST", "/api/v1/models/load",
                       {"model": model_id}, timeout=180, base_url=host)
    if status == 200 and "error" not in data:
        t = data.get("load_time_seconds", "?")
        print(f"✅ ({t}s)")
        return True
    else:
        err = data.get("error", {}).get("message", data)
        print(f"❌ {err}")
        return False

def list_models(host):
    """Lista todos los modelos disponibles."""
    status, data = req("GET", "/api/v1/models", timeout=10, base_url=host)
    if status != 200 or "models" not in data:
        print("⚠️  No management API — use /v1/models instead")
        status2, data2 = req("GET", "/v1/models", timeout=10, base_url=host)
        if status2 == 200:
            for m in data2.get("data", []):
                print(f"  {m['id']}")
        return
    print(f"Modelos disponibles ({len(data['models'])}):")
    for m in data["models"]:
        li = m.get("loaded_instances", [])
        marker = "🟢" if li else "⚪"
        caps = m.get("capabilities", {})
        tags = []
        if caps.get("vision"): tags.append("vision")
        if caps.get("trained_for_tool_use"): tags.append("tools")
        if caps.get("reasoning"): tags.append("reasoning")
        tag_str = f" [{', '.join(tags)}]" if tags else ""
        print(f"  {marker} {m['key']} ({m['params_string']}){tag_str}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Switch LM Studio model")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Server URL (default: {DEFAULT_HOST})")
    parser.add_argument("--target", "-t", help="Model ID to load")
    parser.add_argument("--list", "-l", action="store_true", help="List available models and exit")
    parser.add_argument("--force", "-f", action="store_true", help="Skip unload confirmation")
    args = parser.parse_args()

    if not args.target and not args.list:
        parser.error("either --target or --list is required")

    host = args.host.rstrip("/")

    # Test connectivity
    status, _ = req("GET", "/v1/models", timeout=10, base_url=host)
    if status != 200:
        print(f"❌ Server unreachable at {host}")
        sys.exit(1)

    if args.list:
        list_models(host)
        return

    target = args.target

    print(f"🎯 Switching to: {target}")
    print()

    # Step 1: detect and unload current models
    loaded = get_loaded_models(host)
    if loaded is None:
        print("⚠️  Cannot detect loaded models (Express build). Assume fresh state.")
    elif loaded:
        print(f"📤 Unloading {len(loaded)} current model(s):")
        for instance_id in loaded:
            unload_model(host, instance_id)
            time.sleep(0.5)
    else:
        print("📤 No models currently loaded.")

    print()

    # Step 2: load target
    print(f"📥 Loading {target}...")
    ok = load_model(host, target)

    print()
    if ok:
        print(f"✅ Switch complete — {target} is now active")
    else:
        print(f"❌ Switch failed — see error above")
        sys.exit(1)

if __name__ == "__main__":
    main()
