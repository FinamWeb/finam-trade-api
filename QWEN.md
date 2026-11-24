# QWEN.md

This file provides guidance to Qwen Code when working with code in this repository.

## Project Purpose

This repository contains skills for the Finam Trade API — a broker API for trading Russian and US equities, futures, and other instruments on Moscow Exchange and other markets.

This repository also serves as the Claude, Codex, and Cursor marketplace `finam-trade-api` (plugin `finam`). GitHub source: `FinamWeb/finam-trade-api`.

## Language

Official language: **Russian**. User-facing content, usage examples, and skill prompts are in Russian. Code identifiers and API terms remain in English.

## Structure

- `qwen-extension.json` — Qwen Code extension manifest
- `.claude-plugin/plugin.json` — Claude Code plugin manifest
- `.claude-plugin/marketplace.json` — Claude Code marketplace registry
- `.codex-plugin/plugin.json` — Codex plugin manifest
- `.agents/plugins/marketplace.json` — Codex marketplace registry
- `.cursor-plugin/plugin.json` — Cursor plugin manifest
- `.cursor-plugin/marketplace.json` — Cursor marketplace registry
- `.ai/skills/README.md` — skills index
- `.ai/skills/{skill-name}/SKILL.md` — skill definitions (currently `.ai/skills/trade-api/SKILL.md`)
- `.ai/skills/{skill-name}/scripts/` — runnable Python scripts bundled with the skill
- Each skill = one directory with a `SKILL.md` file

## Namespace

Extension name: `finam`. Skills appear as `finam:{skill-name}`.

GitHub source: `FinamWeb/finam-trade-api`.

## Adding New Skills

1. Create `.ai/skills/{skill-name}/SKILL.md`
2. Include YAML frontmatter: `name`, `description`
3. Update the skills table in `.ai/skills/README.md`
4. Bump version in `qwen-extension.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.cursor-plugin/marketplace.json`, and `.claude-plugin/marketplace.json` (both top-level and plugin entry)
5. Update marketplace plugin entry in `.claude-plugin/marketplace.json` if skill name or description changed

## Updating Skills

1. Edit `.ai/skills/{skill-name}/SKILL.md`
2. Preserve YAML frontmatter structure
3. Bump patch version in `qwen-extension.json`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.cursor-plugin/marketplace.json`, and `.claude-plugin/marketplace.json` (both top-level and plugin entry)
4. If skill name or description changed — update the skills table in `.ai/skills/README.md` and marketplace plugin entry in `.claude-plugin/marketplace.json`

## Key Conventions

**Symbol format:** `ticker@mic` (e.g. `SBER@MISX`). All API calls and scripts use this format.

**Authentication:** Scripts use `finam-sdk` (`from finam_trade_api import FinamClient`) which handles JWT automatically from `TRADE_API_SECRET`. Required env var: `TRADE_API_SECRET` (`ACCOUNT_ID` is an optional override; the account is otherwise resolved from the token).

**REST vs gRPC:** REST (`curl`) for one-off queries. gRPC (`finam-sdk`) for all scripted access — bars, asset search, real-time subscriptions.

**Order confirmation rule:** Before placing or cancelling any order, explicitly confirm all parameters with the user and wait for approval.

**REST API base URL:** `https://api.finam.ru/v1`

**Python SDK:** `pip install finam-sdk` (installs as `finam_trade_api`)

## Skill Description Quality

The `description` field in SKILL.md frontmatter is the PRIMARY auto-activation signal. Always include: all name variants, technology keywords, task verbs, "Use when..." trigger, and scope markers.
