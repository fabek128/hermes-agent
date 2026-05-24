---
name: vaultwarden-cli
description: Manage Vaultwarden through the Bitwarden CLI.
version: 1.0.0
author: Fabian Figueredo + Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [vaultwarden, secrets, devops, cli]
    category: devops
---

# Vaultwarden CLI Skill

Use this skill to operate a self-hosted Vaultwarden vault with the Bitwarden CLI (`bw`) through the Hermes `terminal` tool. It covers setup, login, unlock, inspection, item/folder management, and safe maintenance workflows; it does not cover Bitwarden Secrets Manager (`bws`) or direct database administration.

Treat all vault contents, session tokens, master passwords, item fields, notes, attachments, and exported data as secrets. Never print secret values unless the user explicitly asks for the value and the request scope is clear.

## When to Use

Use this skill when the user asks to:

- configure `bw` for a Vaultwarden server;
- log in, unlock, lock, sync, or inspect CLI status;
- list folders, organizations, collections, or item metadata;
- create, update, move, or delete vault items;
- migrate secrets into Vaultwarden after explicit approval;
- troubleshoot `bw` session, server, or JSON encoding issues.

Do not use this skill for:

- runtime read-only secret injection for agents;
- Bitwarden Secrets Manager machine-account workflows (`bws`);
- reading secrets from local `.env`, shell history, source code, browser stores, or SSH files without explicit user approval;
- direct Vaultwarden database changes.

## Prerequisites

- The Bitwarden CLI `bw` is installed and available to the Hermes process.
- The target Vaultwarden server URL is known.
- The user has authorized the environment, account, and operation scope.
- Any credential required for login or unlock is supplied interactively by the user or through an approved secret wrapper; do not read local secret files by default.

Before using credentials in automated or non-interactive flows, follow the local agent secret-management policy and prefer `/Users/fabian/.agent-secrets/with-secrets.sh -- <command>` when the user has explicitly authorized that path.

## How to Run

Run Vaultwarden operations with the Hermes `terminal` tool from the current project or a neutral working directory. Keep commands small and inspect results before mutating state.

Recommended initial checks:

```bash
bw --version
bw status
```

Configure the server only after confirming the target URL with the user:

```bash
bw config server "https://VAULTWARDEN_HOST"
bw status
```

Login and unlock are sensitive. Prefer interactive prompts. If a command returns a session token, do not paste it in chat or documentation.

```bash
bw login USER_EMAIL
bw unlock
bw sync
```

For one command that requires an existing session, pass the session through the command environment without printing it.

## Quick Reference

| Goal | Command pattern |
|---|---|
| Check CLI state | `bw status` |
| Set server | `bw config server "https://VAULTWARDEN_HOST"` |
| Login interactively | `bw login USER_EMAIL` |
| Unlock interactively | `bw unlock` |
| Sync local cache | `bw sync` |
| List folders | `bw list folders` |
| Search items | `bw list items --search "QUERY"` |
| Get item JSON | `bw get item ITEM_ID` |
| Encode JSON | `bw encode < payload.json` |
| Create item | `bw create item ENCODED_JSON` |
| Edit item | `bw edit item ITEM_ID ENCODED_JSON` |
| Delete item | `bw delete item ITEM_ID` |
| Lock session | `bw lock` |
| Logout | `bw logout` |

## Procedure

### 1. Confirm scope

For any operation that may expose or mutate secrets, confirm:

1. target server;
2. account or organization;
3. read-only vs mutation;
4. exact item/folder/search scope;
5. whether output may include secret values.

Do not proceed with destructive operations until the user explicitly approves the exact action.

### 2. Check local CLI state

Use `terminal` to run:

```bash
bw --version
bw status
```

If the server is not configured or points to a different host, stop and ask before changing it.

### 3. Sync before reads or writes

Run:

```bash
bw sync
```

If sync fails because the vault is locked or unauthenticated, ask the user to unlock/login interactively. Do not look for saved sessions in files or environment variables unless explicitly requested.

### 4. Read metadata safely

Prefer metadata-oriented reads first:

```bash
bw list folders
bw list items --search "QUERY"
```

If item JSON may contain passwords, notes, TOTP seeds, or custom secret fields, summarize only non-secret metadata by default: item id, name, folder id/name, type, username label, and timestamps.

### 5. Create or update items

For item creation or edits:

1. Build JSON in a temporary file or through a short script to avoid shell quoting issues.
2. Encode it with `bw encode`.
3. Use `bw create item` or `bw edit item`.
4. Re-read the item metadata and verify the expected folder/name/type changed.
5. Remove any temporary plaintext payload file immediately.

Never commit payload files, exports, or command transcripts containing secrets.

### 6. Delete items only with explicit approval

Before deletion:

1. show non-secret metadata for the candidate item;
2. ask for explicit confirmation including item id or exact name;
3. prefer a dry run when processing multiple items;
4. run a single deletion batch only after approval.

Use:

```bash
bw delete item ITEM_ID
```

### 7. Export and migration are high risk

Vault exports and migrations can expose the entire vault. Only do them when the user explicitly asks and confirms destination, retention, and cleanup.

Default rules:

- avoid exports when targeted `bw get item` / `bw list items` is enough;
- write exports only to user-approved encrypted storage;
- never place exports in a repository;
- delete temporary plaintext files after verification;
- recommend rotating any secret that was accidentally exposed.

## Pitfalls

- `bw` and `bws` are different tools. Vaultwarden vault operations use `bw`; Bitwarden Secrets Manager uses `bws` and is out of scope.
- `bw get item` can return secret fields. Do not paste raw JSON unless the user explicitly requested raw content.
- Session tokens are bearer secrets. Do not print `BW_SESSION`, store it in docs, or include it in commits.
- Shell quoting complex JSON is fragile. Prefer temporary files or small scripts and remove plaintext artifacts immediately.
- Folder ids are UUIDs, not display names. Resolve folder ids with `bw list folders` before creating or moving items.
- Server configuration is global to the CLI profile. Changing it can affect other Hermes runs using the same home/profile.
- A locked vault is not an error to bypass. Ask the user to unlock or provide an approved secret path.

## Verification

After changes, verify without exposing secrets:

```bash
bw status
bw sync
bw list items --search "EXPECTED_ITEM_NAME"
```

For create/edit/delete work, report:

- what operation was performed;
- item ids or names affected;
- folder or organization affected;
- whether verification succeeded;
- any cleanup performed;
- any remaining user action, such as lock/logout.
