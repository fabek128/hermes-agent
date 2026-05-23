# Infrastructure Folder Layout (Bitwarden)

Organization pattern used for infrastructure credentials in Vaultwarden.

## Folders

| Folder | ID (full UUID) | Purpose |
|---|---|---|
| **Servers** | `b1f8e80b-55fd-4ad2-b0fa-1bd374cb45e1` | SSH hosts, VPS connections |
| **Local Network** | `f5fef130-c235-49d9-ba19-104e18c5b557` | LAN servers, local devices, VPN |
| **Supabase** | `2d0e0d96-603c-4adc-bcb0-db2dc4cf44b9` | Supabase instances (Oberdata) |
| **Services & Apps** | `b7f5ccef-18f1-4f47-8894-73ad1f4c265e` | NPM, Dokploy, RustFS, Grafana |
| **ZeroTier & Domains** | `7e4d07ff-9d12-49d4-b20f-5e2aaf8e49b7` | VPN network, domain lists |

## Items per Folder

### Servers
- **VPS2 - Server**: root@144.31.38.52:22, ZT: 10.125.115.57
- **VPS1 - Old Fallback**: root@138.36.238.249:5608, ZT: 10.125.115.71

### Local Network
- **LocalServer**: fabian@192.168.1.15, password: Mortadela37, ZT: 10.125.115.1
- **ZeroTier Network**: ID: 88c5b1f339a28f82, name: my-first-network, MAC ZT: 10.125.115.109

### Supabase
- **Supabase Oberdata**: obsb.ingenio.uno — includes Postgres pass, JWT secret, Anon/Service role keys, Dashboard creds, Secret Key Base, Vault Enc Key, Logflare keys, port numbers

### Services & Apps
- **Nginx Proxy Manager**: fabianfigueredo@gmail.com @ http://10.125.115.57:81
- **Dokploy**: fabianfigueredo@gmail.com / OL6uCLNpHoTh0zB0 @ dokploy.ingenio.uno
- **RustFS**: s3admin / loioji3235423590_i352inc89234593lkfdsaiu @ rustfs.ingenio.uno
- **Grafana**: admin / mortadela37 @ grafana.ingenio.uno
- **OpenCode Go API**: apikey / sk-FTA... @ https://opencode.ai/zen/go/v1 — API key for opencode-go provider (deepseek-v4-flash)

### ZeroTier & Domains
- **Public Domains**: list of all subdomains (npm, supabase, archivos, dokploy, obsb, grafana, rustfs, rustfsweb)

### SSH Keys
- **SSH Keys**: folder `472f896e-2ea9-41f8-b97f-b42229143a7d` — stores all SSH private/public key pairs, SSH config, and known_hosts as Secure Notes (type: 2). See `references/ssh-keys-folder.md` for item list and pattern.
