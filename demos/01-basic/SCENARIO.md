# Demo 01 — Basic opt-out run

A California resident, **Jordan A. Rivera**, wants to be removed from the major
people-search and data-broker databases under CCPA.

## Input

`profile.json` — the consumer's identifying details (name, email, address,
phone, prior addresses) used to fill out each broker's request.

## Walkthrough

List the brokers that accept CCPA requests:

```sh
python -m optout brokers --regime CCPA
```

Build the full opt-out plan from the profile (one request per broker, each with
a deterministic request ID you can track):

```sh
python -m optout plan demos/01-basic/profile.json --regime CCPA
```

Get the same plan as machine-readable JSON for a pipeline:

```sh
python -m optout --format json plan demos/01-basic/profile.json --regime CCPA
```

Render a ready-to-send letter for a single broker (e.g. Spokeo):

```sh
python -m optout letter spokeo demos/01-basic/profile.json --regime CCPA
```

You can also target just a few brokers:

```sh
python -m optout plan demos/01-basic/profile.json --only spokeo whitepages radaris
```

## Expected result

- `brokers` prints the broker registry filtered to CCPA.
- `plan` prints one `OPT-XXXXXXXXXX` request per applicable broker plus a status
  summary (`pending` until you send each letter).
- `letter` prints a complete CCPA deletion letter addressed to the broker's
  privacy team, with the consumer's identifiers filled in.
