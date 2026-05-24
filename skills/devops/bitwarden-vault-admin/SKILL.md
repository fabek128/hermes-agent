---
name: bitwarden-vault-admin
description: Administer a self-hosted Vaultwarden/Bitwarden vault through the Bitwarden CLI. Use only for setup, migration, maintenance, item creation, deletion, login, troubleshooting, and vault administration. Do not load this skill in readonly secret retrieval agents.
---

# Bitwarden Vault Admin

This is an admin and maintenance skill.

Use this skill only for explicit vault administration tasks such as:

* configuring the Bitwarden CLI server
* logging in
* unlocking the vault
* checking Bitwarden CLI installation
* creating items
* creating folders
* deleting duplicate items
* migrating secrets from local files into Bitwarden
* troubleshooting Bitwarden CLI/session issues

## Critical separation

Do not use this skill in a runtime readonly secret retrieval agent.

For readonly secret retrieval, use the separate skill:

bitwarden-secret-readonly

The readonly agent must not load this admin skill.

## Allowed admin operations

This skill may use the Bitwarden CLI directly for administrative tasks.

Examples:

bw config server https://vault.ingenio.uno
bw login EMAIL_ADDRESS
bw unlock
bw list items
bw list folders
bw get item ITEM_ID
bw create item ENCODED_JSON
bw create folder ENCODED_JSON
bw delete item ITEM_ID

## Admin safety rules

Before creating, editing, or deleting items:

1. Confirm the user explicitly asked for an admin mutation.
2. Prefer dry-run output before destructive changes.
3. Never delete items unless the user explicitly asks.
4. Never print secrets unless the user explicitly asks.
5. Never migrate from local files unless the user explicitly asks for migration.

## Runtime warning

This skill is intentionally broad.

It may mention local files, environment variables, shell configuration, login flows, and troubleshooting commands.

Because of that, it must not be available to the readonly bitwarden-agent.

For runtime secret retrieval, use only the readonly skill:

bitwarden-secret-readonly

and the wrapper:

~/.hermes/profiles/bitwarden-agent/bin/bw-secret "QUERY_TEXT"
