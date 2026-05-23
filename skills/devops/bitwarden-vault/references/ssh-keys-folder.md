# SSH Keys in Bitwarden

## Folder

**SSH Keys** — ID: `472f896e-2ea9-41f8-b97f-b42229143a7d`

Created to store all SSH key pairs, SSH config, and known_hosts as Secure Notes (type: 2).

## Items added

| Item | Type | Content |
|------|------|---------|
| id_ed25519 - GitHub personal | Secure Note | Private key + public key + notes |
| id_ed25519_fabek128 - GitHub fabek128 | Secure Note | Private key + public key + notes |
| id_fabian_gitlab_rsa - GitLab | Secure Note | Private key + public key + notes |
| id_rsa - RSA general | Secure Note | Private key + public key + notes |
| walter_id_rsa - Walter server | Secure Note | Private key + public key + notes |
| SSH Config | Secure Note | Full ~/.ssh/config file |
| SSH Known Hosts (part 1-3) | Secure Note | ~/.ssh/known_hosts split into 3 parts (max 10K encrypted chars) |

## Pattern

Each SSH key item includes in the `notes` field:
1. A description of what the key is for
2. The full private key content
3. The full public key content

The public key is also stored as a **field** (`public_key`, type: 1 = hidden) for easy retrieval without exposing the private key.

## Field types

- `type: 0` = visible text field (use for labels like "ssh-key", "ssh-config")
- `type: 1` = hidden text field (use for public keys, tokens — value is masked in UI)

## Known Hosts split

The `known_hosts` file exceeds the Bitwarden 10,000-character encrypted value limit when stored as Notes. Split strategy: chunk by size (~3,500 raw chars per chunk keeps encrypted value under limit), not by line count.

## Notes limit

Bitwarden CLI enforces an encrypted value limit of ~10,000 characters for the `notes` field. For SSH private keys (which are typically small, ~400 chars for ed25519 or ~3,400 chars for RSA), they fit easily. For larger data like known_hosts, split into multiple items.
