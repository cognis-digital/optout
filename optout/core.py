"""Core engine for OPTOUT: broker registry, profile loading, letter rendering,
and request-status tracking. Pure standard library, no network."""
from __future__ import annotations

import json
import hashlib
import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


# --------------------------------------------------------------------------- #
# Broker registry
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Broker:
    """A single data broker and the channel used to reach its privacy team."""
    slug: str
    name: str
    privacy_email: str
    opt_out_url: str
    # Jurisdictions the broker is reachable under. Drives which legal basis
    # we cite in the generated letter.
    regimes: tuple[str, ...] = ("CCPA", "GDPR")

    def supports(self, regime: str) -> bool:
        return regime.upper() in {r.upper() for r in self.regimes}


def _b(slug, name, email, url, regimes=("CCPA", "GDPR")) -> Broker:
    return Broker(slug, name, email, url, regimes)


# Curated registry of major US/EU consumer-data brokers. (Trimmed sample of the
# top-50 list; emails/urls are the publicly documented privacy contacts.)
BROKERS: tuple[Broker, ...] = (
    _b("acxiom", "Acxiom", "privacy@acxiom.com", "https://www.acxiom.com/optout/"),
    _b("oracle-data", "Oracle Data Cloud", "privacy_ww@oracle.com", "https://www.oracle.com/legal/privacy/"),
    _b("epsilon", "Epsilon", "privacy@epsilon.com", "https://www.epsilon.com/us/privacy-policy"),
    _b("experian", "Experian", "privacy@experian.com", "https://www.experian.com/privacy/opting_out"),
    _b("equifax", "Equifax", "privacy@equifax.com", "https://www.equifax.com/personal/privacy/"),
    _b("transunion", "TransUnion", "privacy@transunion.com", "https://www.transunion.com/optout"),
    _b("corelogic", "CoreLogic", "privacy@corelogic.com", "https://www.corelogic.com/privacy/"),
    _b("lexisnexis", "LexisNexis", "privacy.policy@lexisnexis.com", "https://optout.lexisnexis.com/"),
    _b("spokeo", "Spokeo", "privacy@spokeo.com", "https://www.spokeo.com/optout"),
    _b("whitepages", "Whitepages", "support@whitepages.com", "https://www.whitepages.com/suppression-requests"),
    _b("beenverified", "BeenVerified", "privacy@beenverified.com", "https://www.beenverified.com/app/optout/search"),
    _b("intelius", "Intelius", "privacy@intelius.com", "https://www.intelius.com/opt-out/"),
    _b("peoplefinders", "PeopleFinders", "privacy@peoplefinders.com", "https://www.peoplefinders.com/opt-out"),
    _b("radaris", "Radaris", "privacy@radaris.com", "https://radaris.com/control/privacy"),
    _b("mylife", "MyLife", "privacy@mylife.com", "https://www.mylife.com/ccpa/index.pubview"),
    _b("peoplelookup", "PeopleLookup", "privacy@peoplelookup.com", "https://www.peoplelookup.com/optout"),
    _b("truthfinder", "TruthFinder", "privacy@truthfinder.com", "https://www.truthfinder.com/opt-out/"),
    _b("instantcheckmate", "Instant Checkmate", "privacy@instantcheckmate.com", "https://www.instantcheckmate.com/opt-out/"),
    _b("usphonebook", "USPhoneBook", "privacy@usphonebook.com", "https://www.usphonebook.com/opt-out"),
    _b("fastpeoplesearch", "FastPeopleSearch", "privacy@fastpeoplesearch.com", "https://www.fastpeoplesearch.com/removal"),
)


def get_broker(slug: str) -> Broker | None:
    s = slug.lower()
    for b in BROKERS:
        if b.slug == s:
            return b
    return None


# --------------------------------------------------------------------------- #
# Consumer profile
# --------------------------------------------------------------------------- #
def load_profile(path: str | Path) -> dict:
    """Load and validate a consumer profile JSON used to fill out letters."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = ("full_name", "email")
    missing = [k for k in required if not data.get(k)]
    if missing:
        raise ValueError(f"profile missing required field(s): {', '.join(missing)}")
    return data


# --------------------------------------------------------------------------- #
# Request model
# --------------------------------------------------------------------------- #
VALID_STATUSES = ("pending", "sent", "acknowledged", "completed", "rejected")


@dataclass
class OptOutRequest:
    broker_slug: str
    regime: str
    status: str = "pending"
    request_id: str = ""
    created: str = ""
    channel: str = ""  # email address or opt-out URL

    def to_dict(self) -> dict:
        return asdict(self)


def _make_request_id(profile: dict, broker: Broker, regime: str) -> str:
    seed = f"{profile.get('email','')}|{broker.slug}|{regime}".lower()
    return "OPT-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10].upper()


# --------------------------------------------------------------------------- #
# Letter rendering
# --------------------------------------------------------------------------- #
_CCPA_BODY = (
    "I am a California resident exercising my rights under the California "
    "Consumer Privacy Act (CCPA), Cal. Civ. Code 1798.100 et seq. I request "
    "that you (1) disclose the personal information you have collected about "
    "me, and (2) delete that information and stop selling or sharing it. "
    "This is a verifiable consumer request."
)
_GDPR_BODY = (
    "I am a data subject exercising my rights under the EU General Data "
    "Protection Regulation (GDPR). Under Article 17 (right to erasure) I "
    "request deletion of all personal data you hold about me, and under "
    "Article 21 I object to any processing for direct-marketing purposes. "
    "Please confirm completion within one month per Article 12(3)."
)


def render_letter(profile: dict, broker: Broker, regime: str) -> str:
    """Produce a complete, send-ready opt-out letter for one broker."""
    regime = regime.upper()
    if regime not in ("CCPA", "GDPR"):
        raise ValueError(f"unsupported regime: {regime}")
    if not broker.supports(regime):
        raise ValueError(f"{broker.name} does not accept {regime} requests")

    body = _CCPA_BODY if regime == "CCPA" else _GDPR_BODY
    today = datetime.date.today().isoformat()
    ident_lines = [f"Full name: {profile['full_name']}", f"Email: {profile['email']}"]
    for key, label in (("address", "Address"), ("phone", "Phone"),
                        ("prior_addresses", "Prior addresses")):
        val = profile.get(key)
        if val:
            if isinstance(val, list):
                val = "; ".join(val)
            ident_lines.append(f"{label}: {val}")

    return "\n".join([
        f"Date: {today}",
        f"To: {broker.name} Privacy Team <{broker.privacy_email}>",
        f"Subject: {regime} Data Deletion / Opt-Out Request",
        "",
        "To whom it may concern,",
        "",
        body,
        "",
        "Identifying information to locate my records:",
        *("  " + line for line in ident_lines),
        "",
        "Please confirm receipt and the actions taken. Do not require me to "
        "create an account to exercise these rights.",
        "",
        "Sincerely,",
        profile["full_name"],
    ])


# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #
class OptOutEngine:
    """Builds and tracks opt-out requests against the broker registry."""

    def __init__(self, brokers: Iterable[Broker] = BROKERS):
        self.brokers = tuple(brokers)

    def list_brokers(self, regime: str | None = None) -> list[Broker]:
        if regime is None:
            return list(self.brokers)
        return [b for b in self.brokers if b.supports(regime)]

    def build_requests(self, profile: dict, regime: str = "CCPA",
                       only: list[str] | None = None) -> list[OptOutRequest]:
        """Create one request per applicable broker. Raises if a named broker
        is unknown or none apply."""
        regime = regime.upper()
        if only:
            unknown = [s for s in only if get_broker(s) is None]
            if unknown:
                raise ValueError(f"unknown broker(s): {', '.join(unknown)}")
            targets = [get_broker(s) for s in only]
        else:
            targets = self.brokers

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        reqs: list[OptOutRequest] = []
        for b in targets:
            if not b.supports(regime):
                continue
            reqs.append(OptOutRequest(
                broker_slug=b.slug,
                regime=regime,
                status="pending",
                request_id=_make_request_id(profile, b, regime),
                created=now,
                channel=b.privacy_email or b.opt_out_url,
            ))
        if not reqs:
            raise ValueError(f"no brokers support regime {regime} for this run")
        return reqs

    def render_all(self, profile: dict, regime: str = "CCPA",
                   only: list[str] | None = None) -> dict[str, str]:
        """Map of broker slug -> rendered letter."""
        out: dict[str, str] = {}
        for req in self.build_requests(profile, regime, only):
            broker = get_broker(req.broker_slug)
            out[req.broker_slug] = render_letter(profile, broker, regime)
        return out

    @staticmethod
    def summarize(reqs: list[OptOutRequest]) -> dict:
        counts: dict[str, int] = {s: 0 for s in VALID_STATUSES}
        for r in reqs:
            counts[r.status] = counts.get(r.status, 0) + 1
        return {"total": len(reqs), "by_status": counts}
