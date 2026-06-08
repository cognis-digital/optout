"""Command-line interface for OPTOUT."""
from __future__ import annotations

import argparse
import json
import sys

from . import TOOL_NAME, TOOL_VERSION
from .core import OptOutEngine, get_broker, load_profile, render_letter


def _print_table(rows: list[list[str]], headers: list[str]) -> None:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(line)
    print("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in rows:
        print("  ".join(str(c).ljust(widths[i]) for i, c in enumerate(row)))


def _emit(fmt: str, payload, table_fn) -> None:
    if fmt == "json":
        print(json.dumps(payload, indent=2))
    else:
        table_fn()


def cmd_brokers(args) -> int:
    eng = OptOutEngine()
    brokers = eng.list_brokers(args.regime)
    payload = [
        {"slug": b.slug, "name": b.name, "email": b.privacy_email,
         "url": b.opt_out_url, "regimes": list(b.regimes)}
        for b in brokers
    ]

    def table():
        _print_table(
            [[b.slug, b.name, "|".join(b.regimes), b.privacy_email] for b in brokers],
            ["SLUG", "NAME", "REGIMES", "EMAIL"],
        )

    _emit(args.format, payload, table)
    return 0 if brokers else 1


def cmd_plan(args) -> int:
    profile = load_profile(args.profile)
    eng = OptOutEngine()
    reqs = eng.build_requests(profile, args.regime, args.only)
    payload = {
        "regime": args.regime.upper(),
        "consumer": profile.get("full_name"),
        "summary": eng.summarize(reqs),
        "requests": [r.to_dict() for r in reqs],
    }

    def table():
        _print_table(
            [[r.request_id, r.broker_slug, r.status, r.channel] for r in reqs],
            ["REQUEST_ID", "BROKER", "STATUS", "CHANNEL"],
        )
        print(f"\n{len(reqs)} request(s) planned under {args.regime.upper()}.")

    _emit(args.format, payload, table)
    return 0


def cmd_letter(args) -> int:
    profile = load_profile(args.profile)
    broker = get_broker(args.broker)
    if broker is None:
        print(f"error: unknown broker '{args.broker}'", file=sys.stderr)
        return 2
    letter = render_letter(profile, broker, args.regime)
    if args.format == "json":
        print(json.dumps({"broker": broker.slug, "regime": args.regime.upper(),
                          "letter": letter}, indent=2))
    else:
        print(letter)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=TOOL_NAME, description="Automated data-broker opt-out engine.")
    p.add_argument("--version", action="version",
                   version=f"{TOOL_NAME} {TOOL_VERSION}")
    p.add_argument("--format", choices=("table", "json"), default="table",
                   help="output format (default: table)")
    sub = p.add_subparsers(dest="command", required=True)

    b = sub.add_parser("brokers", help="list known data brokers")
    b.add_argument("--regime", choices=("CCPA", "GDPR"), default=None,
                   help="filter to brokers that accept this regime")
    b.set_defaults(func=cmd_brokers)

    pl = sub.add_parser("plan", help="build opt-out requests from a profile")
    pl.add_argument("profile", help="path to consumer profile JSON")
    pl.add_argument("--regime", choices=("CCPA", "GDPR"), default="CCPA")
    pl.add_argument("--only", nargs="+", metavar="SLUG",
                    help="limit to specific broker slugs")
    pl.set_defaults(func=cmd_plan)

    lt = sub.add_parser("letter", help="render a send-ready letter for one broker")
    lt.add_argument("broker", help="broker slug")
    lt.add_argument("profile", help="path to consumer profile JSON")
    lt.add_argument("--regime", choices=("CCPA", "GDPR"), default="CCPA")
    lt.set_defaults(func=cmd_letter)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
