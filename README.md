# OPTOUT — Automated data-broker opt-out engine — top 50 brokers, CCPA/GDPR letters

> Part of the **[Cognis Neural Suite](https://github.com/cognis-digital)** by [Cognis Digital](https://cognis.digital)
> MIT License · domain: `privacy`

[![PyPI](https://img.shields.io/pypi/v/cognis-optout.svg)](https://pypi.org/project/cognis-optout/)
[![CI](https://github.com/cognis-digital/optout/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/optout/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Automated data-broker opt-out engine — top 50 brokers, CCPA/GDPR letters.

## Install

```bash
pip install cognis-optout
```

For local development from this repo:

```bash
pip install -e .
```

## Quick start

```bash
optout --version
optout scan demos/                          # run against bundled demo
optout scan demos/ --format sarif --out r.sarif --fail-on high
optout mcp                                   # start as MCP server (Cognis.Studio / Claude Desktop / Cursor)
```

## Built-in demo scenarios

Every scenario folder includes a `SCENARIO.md` describing what it represents and what findings to expect.

- `demos/01-executive-protection/` — see [`SCENARIO.md`](demos/01-executive-protection/SCENARIO.md)
- `demos/02-clean-campaign/` — see [`SCENARIO.md`](demos/02-clean-campaign/SCENARIO.md)
- `demos/03-mass-stalking-response/` — see [`SCENARIO.md`](demos/03-mass-stalking-response/SCENARIO.md)

## How it fits the Cognis Neural Suite

This tool is one of 52 in the [Cognis Neural Suite](https://github.com/cognis-digital). The full suite + launcher lives at:

- Suite landing: https://cognis.digital
- All 52 repos: https://github.com/cognis-digital
- Cognis.Studio (Enterprise AI Workforce, MCP host): https://cognis.studio

Every Suite tool ships an MCP server, so Cognis.Studio agents can call them as scoped capabilities.

## License

MIT. See [LICENSE](LICENSE).

## About

**[Cognis Digital](https://cognis.digital)** — Wyoming, USA · *Making Tomorrow Better Today: Advanced Cybersecurity, AI Innovation, and Blockchain Expertise.*
