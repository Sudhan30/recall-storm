"""GS1 Digital Link URI parsing and canonical construction."""
from __future__ import annotations

from datetime import date
from urllib.parse import parse_qs, unquote, urlparse

from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.ai import ai_17
from recallstorm.gs1.gtin import normalize_gtin


def is_digital_link(uri: str) -> bool:
    """Return True if uri is a valid HTTP(S) GS1 Digital Link containing '/01/<gtin>'."""
    if not isinstance(uri, str) or not uri.startswith(("http://", "https://")):
        return False
    return "/01/" in uri


def parse_digital_link(uri: str) -> dict[str, str]:
    """Parse a GS1 Digital Link URI into a dictionary of AI codes to values."""
    if not is_digital_link(uri):
        raise DataValidationError(f"Not a valid GS1 Digital Link URI: {uri!r}")
    parsed = urlparse(uri)
    segments = [unquote(seg) for seg in parsed.path.strip("/").split("/") if seg]
    try:
        idx = segments.index("01")
    except ValueError as exc:
        raise DataValidationError(f"Missing /01/ GTIN path in Digital Link: {uri!r}") from exc

    ais: dict[str, str] = {}
    i = idx
    while i + 1 < len(segments):
        key = segments[i]
        val = segments[i + 1]
        if key == "01":
            ais["01"] = normalize_gtin(val)
        else:
            ais[key] = val
        i += 2

    q_params = parse_qs(parsed.query)
    for k, vals in q_params.items():
        if vals:
            ais[k] = vals[0]
    return ais


def digital_link_to_ais(uri: str) -> dict[str, str]:
    """Alias for parse_digital_link returning AI dictionary."""
    return parse_digital_link(uri)


def build_digital_link(
    gtin: str,
    lot: str | None = None,
    expiry: str | None = None,
    serial: str | None = None,
    domain: str = "https://id.gs1.org",
) -> str:
    """Build a canonical GS1 Digital Link URI."""
    g14 = normalize_gtin(gtin)
    base = domain.rstrip("/") + f"/01/{g14}"
    if lot:
        base += f"/10/{lot}"
    if serial:
        base += f"/21/{serial}"
    if expiry:
        base += f"?17={expiry}"
    return base


def ais_to_digital_link(ais: dict[str, str], domain: str = "https://id.gs1.org") -> str:
    """Convert an AI dictionary into a GS1 Digital Link URI."""
    if "01" not in ais:
        raise DataValidationError("AI '01' (GTIN) is required to build a Digital Link")
    return build_digital_link(
        gtin=ais["01"],
        lot=ais.get("10"),
        expiry=ais.get("17"),
        serial=ais.get("21"),
        domain=domain,
    )


def canonical_digital_link(uri: str) -> str:
    """Normalize any GS1 Digital Link URI to the canonical https://id.gs1.org domain."""
    ais = parse_digital_link(uri)
    return ais_to_digital_link(ais, domain="https://id.gs1.org")


def digital_link_gtin(uri: str) -> str:
    """Extract the 14-digit GTIN from a GS1 Digital Link URI."""
    return parse_digital_link(uri)["01"]


def digital_link_lot(uri: str) -> str | None:
    """Extract the AI 10 lot code from a GS1 Digital Link URI."""
    return parse_digital_link(uri).get("10")


def digital_link_expiry(uri: str) -> date | None:
    """Extract the AI 17 expiration date from a GS1 Digital Link URI."""
    ais = parse_digital_link(uri)
    return ai_17(ais)
