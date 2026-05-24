# Hermes Credential Flow — Bitwarden as Secret Source

Replace `.env`-stored API keys with Bitwarden-managed secrets.

## Architecture

```
Bitwarden (source of truth)
    ↓  bw get password <item-id>
hermes-load-vault-keys       ← exports OPENCODE_GO_API_KEY (and future keys)
    ↓  eval "$(...)"
~/.local/bin/env              ← sourced from .bashrc loads BW_SESSION + runs loader
    ↓  exec
Hermes CLI / ACP / Gateway    ← reads env vars normally
```

## Components

### 1. Bitwarden Item — API Key Pattern

API keys are stored as login items (type 1):

| Field | Value |
|---|---|
| `name` | Human-readable (e.g. "OpenCode Go API") |
| `username` | `apikey` (convention) |
| `password` | The actual API key value |
| `uri` | API base URL (optional) |
| `notes` | Description of usage |

Retrieval: `bw get password <item-id>` returns just the value.

### 2. Loader Script (`~/.local/bin/hermes-load-vault-keys`)

```bash
#!/usr/bin/env bash
set -euo pipefail
BW_ITEM_ID="<bitwarden-item-uuid>"

# Use BW_SESSION from env or .hermes/.env
BW_SESSION_VAL="${BW_SESSION:-}"
if [ -z "$BW_SESSION_VAL" ] && [ -f "$HOME/.hermes/.env" ]; then
    BW_SESSION_VAL=$(grep '^BW_SESSION=' "$HOME/.hermes/.env" | head -1 | cut -d= -f2-)
fi
[ -z "$BW_SESSION_VAL" ] && { echo "# BW_SESSION not set" >&2; exit 1; }
export BW_SESSION="$BW_SESSION_VAL"

bw unlock --check >/dev/null 2>&1 || { echo "# Vault locked — run 'bw unlock' first" >&2; exit 1; }

PASS=$(bw get password "$BW_ITEM_ID" 2>/dev/null)
[ -z "$PASS" ] && { echo "# Failed to retrieve key from Bitwarden" >&2; exit 1; }

echo "export OPENCODE_GO_API_KEY='${PASS}'"
```

### 3. Shell Integration (`~/.local/bin/env`)

Sourced from `.bashrc`. Exports BW_SESSION then runs the loader:

```bash
# Export BW_SESSION from .hermes/.env if not already set
if [ -z "${BW_SESSION:-}" ] && [ -f "$HOME/.hermes/.env" ]; then
    BW_SESSION_VAL=$(grep '^BW_SESSION=' "$HOME/.hermes/.env" | head -1 | cut -d= -f2-)
    [ -n "$BW_SESSION_VAL" ] && export BW_SESSION="$BW_SESSION_VAL"
fi

# Load API keys from Bitwarden
eval "$(hermes-load-vault-keys 2>/dev/null || echo true)"
```

### 4. Gateway Service Integration (`~/.config/systemd/user/hermes-gateway.service`)

The service uses a wrapper script `~/.local/bin/hermes-gateway-start`:

```bash
#!/usr/bin/env bash
# Export BW_SESSION
BW_SESSION_VAL="${BW_SESSION:-}"
if [ -z "$BW_SESSION_VAL" ] && [ -f "$HOME/.hermes/.env" ]; then
    BW_SESSION_VAL=$(grep '^BW_SESSION=' "$HOME/.hermes/.env" | head -1 | cut -d= -f2-)
fi
[ -n "$BW_SESSION_VAL" ] && export BW_SESSION="$BW_SESSION_VAL"

# Load API keys from Bitwarden
eval "$(/home/fabian/.local/bin/hermes-load-vault-keys 2>/dev/null)"

# Start gateway
exec /home/fabian/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
```

The systemd service `ExecStart` points to this wrapper instead of the python command directly.

## Setup Checklist

1. [ ] Create Bitwarden item (login type) with API key in password field
2. [ ] Create `hermes-load-vault-keys` script with the item ID
3. [ ] Add BW_SESSION export to `~/.local/bin/env`
4. [ ] Add `eval "$(hermes-load-vault-keys ...)"` to `~/.local/bin/env`
5. [ ] Update gateway service to use wrapper script
6. [ ] Remove key from all `.env` files (comment out or set to `<from vault>`)
7. [ ] Verify: open new shell → `echo ${OPENCODE_GO_API_KEY:+present}` → "present"

## Pitfalls

- **BW_SESSION must be set before loader runs.** The .env script handles this, but terminal sessions started without .bashrc sourcing will need manual export.
- **Systemd user services need DBUS session** to reload (`systemctl --user daemon-reload`). If running in a non-interactive context (e.g. Agent terminal), this will fail — that's OK, the file change takes effect on next graphical login.
- **`sk-` prefixed values are redacted** in Agent tool output. Always verify via hexdump or length check, not by reading the value back.
- **Loader script is idempotent** — running it multiple times just re-exports the same value.
