<div align="center">

# finam-skill — Claude Code, Qwen Code, Codex & Cursor Plugin

Finam Trade API skills for Claude Code, Qwen Code, Codex and Cursor.

This repository also serves as the Claude, Codex, and Cursor marketplace (`finam-trade-api`).

</div>

## Available Skills

| Skill | Command | Description |
|-------|---------|-------------|
| trade-api | `/finam:trade-api` | Real-time quotes, order book, OHLCV candles, portfolio and orders via REST, gRPC, and WebSocket; instrument search and volatility scanning; place and cancel orders; develop algorithmic trading scripts |

## Installation

### Claude Code

```bash
claude plugin marketplace add FinamWeb/finam-trade-api
claude plugin install finam@finam-trade-api --scope user
```

### Qwen Code

```bash
qwen extensions install FinamWeb/finam-trade-api
```

### Codex

```bash
codex plugin marketplace add FinamWeb/finam-trade-api
codex plugin add finam@finam-trade-api
```

### Cursor

In Cursor, open an Agent chat and run:

```
/add-plugin https://github.com/FinamWeb/finam-trade-api
```

## Setup

After installation, configure two environment variables:

- `FINAM_API_KEY` — API token from [api.finam.ru/docs/tokens](https://api.finam.ru/docs/tokens)
- `FINAM_ACCOUNT_ID` — account number from [lk.finam.ru](https://lk.finam.ru/) (digits only, without the `КлФ-` prefix)

**Claude Code** — add to `.claude/settings.local.json`:
```json
{ "env": { "FINAM_API_KEY": "...", "FINAM_ACCOUNT_ID": "..." } }
```

**Qwen Code** — prompted automatically during installation, or set manually:
```bash
qwen extensions settings set finam "Finam API Key"
qwen extensions settings set finam "Finam Account ID"
```

**Codex / Cursor** — set in the dashboard under **Plugins → Configure** after installation.

A **demo account** can be opened at the [tokens page](https://api.finam.ru/docs/tokens). Valid for 2 weeks and works identically to a real account.

## Usage Examples

**Portfolio analysis:**
```
Проведи глубокий анализ моего портфеля. Покажи структуру, динамику и предложи балансировку.
```

**Market scanner:**
```
Найди все акции на Мосбирже из финансового сектора, которые выросли более чем на 5%
за неделю при объёме торгов выше 500 млн рублей.
```

**Momentum strategy:**
```
Реализуй моментум-стратегию: покупаем 10 акций с наибольшей инерцией за месяц,
ребалансировка раз в неделю.
```

**Volatility scan:**
```
Выбери 10 самых волатильных бумаг на Мосбирже и раздели портфель поровну между ними.
```

**Order management:**
```
Покажи мои открытые заявки и отмени все лимитные ордера по SBER@MISX.
```

**Algo script:**
```
Напиши скрипт на Python: если акция за последние 30 дней выросла — покупаем,
иначе продаём. Использовать Finam gRPC API.
```

## Project Structure

```
finam-trade-api/
├── .agents/plugins/marketplace.json   # Codex marketplace registry
├── .claude-plugin/
│   ├── marketplace.json               # Claude Code marketplace registry
│   └── plugin.json                    # Claude Code manifest (sync source of truth)
├── .codex-plugin/plugin.json          # Codex manifest
├── .cursor-plugin/
│   ├── marketplace.json               # Cursor marketplace registry
│   └── plugin.json                    # Cursor manifest
├── qwen-extension.json                # Qwen Code manifest
├── CLAUDE.md                          # Claude Code context
├── QWEN.md                            # Qwen Code context
└── .ai/skills/
    ├── README.md                      # This file
    └── trade-api/
        ├── SKILL.md                   # Skill definition
        ├── assets/                    # Exchanges and top-100 equity lists
        ├── references/docs/           # Official API docs (REST, gRPC, WebSocket)
        └── scripts/
            ├── asset_search.py        # Search instruments by ticker glob / name
            └── scanner.py             # Scan top-100 stocks by volatility, growth, or volume
```

## License

MIT
