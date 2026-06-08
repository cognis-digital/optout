"""OPTOUT — automated data-broker opt-out engine.

Generates CCPA / GDPR opt-out (data deletion) requests for the top
data brokers, tracks request status, and renders ready-to-send letters.
Standard library only, zero install, no network required.
"""
from .core import (
    Broker,
    OptOutRequest,
    OptOutEngine,
    BROKERS,
    load_profile,
    render_letter,
)

TOOL_NAME = "optout"
TOOL_VERSION = "1.0.0"

__all__ = [
    "Broker",
    "OptOutRequest",
    "OptOutEngine",
    "BROKERS",
    "load_profile",
    "render_letter",
    "TOOL_NAME",
    "TOOL_VERSION",
]
