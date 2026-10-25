"""GS1 Digital Link URI parser and builder (https://id.gs1.org/01/<gtin>/10/<lot>?17=<yymmdd>)."""
from __future__ import annotations

from datetime import date
from urllib.parse import parse_qs, unquote, urlparse
from recallstorm.core.errors import DataValidationError
from recallstorm.gs1.ai import ai_17
from recallstorm.gs1.gtin import normalize_gtin


def is_digital_link(uri: str) -> bool:
    """Return True if uri is a valid HTTP(S) GS1 Digital Link containing /01/<gtin>."""
    if not isinstance(uri, str) or not uri.strip():
        return False
    parsed = urlparse(uri.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return False
    parts = [p for p in parsed.path.split("/") if p]
    return "01" in parts


def parse_digital_link(uri: str) -> dict[str, str]:
    """Parse a GS1 Digital Link URI into an Application Identifier dictionary."""
    if not is_digital_link(uri):
        raise DataValidationError(f"Not a valid GS1 Digital Link URI: {uri}")
    parsed = urlparse(uri.strip())
    parts = [unquote(p) for p in parsed.path.split("/") if p]
    idx = parts.index("01")
    ais: dict[str, str] = {}
    i = idx
    while i + 1 < len(parts):
        k, v = parts[i], parts[i + 1]
        ais[k] = normalize_gtin(v) if k == "01" else v
        i += 2
    for qk, qvals in parse_qs(parsed.query).items():
        if qvals:
            ais[qk] = qvals[0]
    if "01" not in ais:
        raise DataValidationError(f"Missing AI 01 in Digital Link: {uri}")
    return ais


def build_digital_link(
    gtin: str,
    lot: str | None = None,
    expiry: str | None = None,
    serial: str | None = None,
    domain: str = "https://id.gs1.org",
) -> str:
    """Build a canonical GS1 Digital Link URI."""
    norm = normalize_gtin(gtin)
    base = domain.rstrip("/") + f"/01/{norm}"
    if lot:
        base += f"/10/{lot}"
    if serial:
        base += f"/21/{serial}"
    if expiry:
        base += f"?17={expiry}"
    return base


def digital_link_gtin(uri: str) -> str:
    """Extract the 14-digit GTIN from a GS1 Digital Link URI."""
    return parse_digital_link(uri)["01"]


def digital_link_lot(uri: str) -> str | None:
    """Extract the lot/batch code (AI 10) from a GS1 Digital Link URI."""
    return parse_digital_link(uri).get("10")


def digital_link_expiry(uri: str) -> date | None:
    """Extract and parse the expiration date (AI 17) from a GS1 Digital Link URI."""
    ais = parse_digital_link(uri)
    return ai_17(ais)


def canonical_digital_link(uri: str) -> str:
    """Normalize a GS1 Digital Link URI onto https://id.gs1.org with 14-digit GTIN."""
    ais = parse_digital_link(uri)
    return ais_to_digital_link(ais, domain="https://id.gs1.org")


def digital_link_to_ais(uri: str) -> dict[str, str]:
    """Convert a GS1 Digital Link URI to an AI dictionary."""
    return parse_digital_link(uri)


def ais_to_digital_link(ais: dict[str, str], domain: str = "https://id.gs1.org") -> str:
    """Convert an AI dictionary into a GS1 Digital Link URI."""
    if not isinstance(ais, dict) or "01" not in ais:
        raise DataValidationError("ais dict must include '01'")
    return build_digital_link(
        gtin=ais["01"],
        lot=ais.get("10"),
        expiry=ais.get("17"),
        serial=ais.get("21"),
        domain=domain,
    )
