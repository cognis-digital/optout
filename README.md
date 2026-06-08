# OPTOUT — Automated data-broker opt-out engine — top 50 brokers, CCPA/GDPR letters

> Part of the **[Cognis Neural Suite](https://github.com/cognis-digital)** by [Cognis Digital](https://cognis.digital)
> Cognis Open Collaboration License (COCL) v1.0 · domain: `privacy`

[![PyPI](https://img.shields.io/pypi/v/cognis-optout.svg)](https://pypi.org/project/cognis-optout/)
[![CI](https://github.com/cognis-digital/optout/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/optout/actions)
[![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE)
[![Suite](https://img.shields.io/badge/Cognis-Neural%20Suite-6b46c1.svg)](https://github.com/cognis-digital)

**Automated data-broker opt-out engine — top 50 brokers, CCPA/GDPR letters.**

*Privacy / Personal — put individuals back in control of their data.*

## Why

Security and intelligence teams need automated data-broker opt-out engine — top 50 brokers, CCPA/GDPR letters without standing up heavyweight infrastructure. `optout` is single-purpose, scriptable, CI-friendly, and self-hostable: point it at a target, get prioritized findings in the format your workflow already speaks (table, JSON, SARIF, HTML), and wire it into agents over MCP when you want it autonomous.

## Install

```bash
pip install cognis-optout
# or, from this repo:
pip install -e ".[dev]"
```

## Quick start

```bash
optout --version
optout scan demos/                      # run against the bundled demo
optout scan demos/ --format sarif --out r.sarif --fail-on high
optout scan demos/ --format html --out report.html
optout mcp                              # expose as an MCP server (Cognis.Studio / Claude Desktop / Cursor)
```

## Built-in demo scenarios

Each scenario folder includes a `SCENARIO.md` describing the situation and the findings to expect.

- [`demos/01-executive-protection/`](demos/01-executive-protection/SCENARIO.md)
- [`demos/02-clean-campaign/`](demos/02-clean-campaign/SCENARIO.md)
- [`demos/03-mass-stalking-response/`](demos/03-mass-stalking-response/SCENARIO.md)

## Output formats

- **Table** (default) — human-readable terminal summary
- **JSON** — machine-readable findings for pipelines
- **SARIF** — drops into GitHub code-scanning / IDE problem panes
- **HTML** — shareable report with severity rollups

## Credits / Built on

Cognis composes and credits the best of open source. This tool builds on / interoperates with:

- [`AnalogJ/justvanish`](https://github.com/AnalogJ/justvanish) — fork base
- [`yaelwrites/Big-Ass-Data-Broker-Opt-Out-List`](https://github.com/yaelwrites/Big-Ass-Data-Broker-Opt-Out-List) — broker list

Missing a credit? Open a PR — see [CONTRIBUTING.md](CONTRIBUTING.md).

## How it fits the Cognis Neural Suite

`optout` is one of **52 tools** in the [Cognis Neural Suite](https://github.com/cognis-digital). Every tool ships an MCP server, so [Cognis.Studio](https://cognis.studio) agents can call them as scoped capabilities.

**Sibling tools in `privacy`:** [`recall`](https://github.com/cognis-digital/recall), [`vaultmap`](https://github.com/cognis-digital/vaultmap), [`breachwatch`](https://github.com/cognis-digital/breachwatch), [`piicomb`](https://github.com/cognis-digital/piicomb), [`trackblock`](https://github.com/cognis-digital/trackblock), [`privacyshell`](https://github.com/cognis-digital/privacyshell)

## Architecture & roadmap

- Design notes: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Planned work: [`ROADMAP.md`](ROADMAP.md)

## Contributing

PRs, new detections, and demo scenarios are welcome under the collaboration-pull model. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

Source-available under the **Cognis Open Collaboration License (COCL) v1.0** — free for personal, internal-evaluation, research, and educational use; **commercial / production use requires a license** (licensing@cognis.digital). See [LICENSE](LICENSE).

## Responsible use

This is dual-use security software. Use it only against systems, data, and identities you own or are explicitly authorized in writing to test, and in compliance with applicable law.

## About

**[Cognis Digital](https://cognis.digital)** — Wyoming, USA · *Making Tomorrow Better Today: Advanced Cybersecurity, AI Innovation, and Blockchain Expertise.*
