"""Multilingual additive alias translations and language detection."""
from __future__ import annotations

import re
import unicodedata

TRANSLATIONS: dict[str, dict[str, list[str]]] = {
    "RED3": {
        "en": ["FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127", "CI 45430"],
        "es": ["Rojo 3", "Rojo No. 3", "Rojo #3", "eritrosina"],
        "fr": ["Rouge 3", "Rouge no 3", "érythrosine", "erythrosine"],
        "de": ["Erythrosin", "E 127"],
    },
    "BVO": {
        "en": ["brominated vegetable oil", "BVO", "E443"],
        "es": ["aceite vegetal bromado"],
        "fr": ["huile végétale bromée", "huile vegetale bromee"],
    },
    "POTASSIUM_BROMATE": {
        "en": ["potassium bromate", "bromated flour", "E924", "E924a"],
        "es": ["bromato de potasio"],
        "fr": ["bromate de potassium"],
    },
    "PROPYLPARABEN": {
        "en": ["propylparaben", "propyl paraben", "propyl p-hydroxybenzoate", "E216", "E217"],
        "es": ["propilparabeno"],
        "fr": ["propylparabène", "propylparabene"],
    },
}


def accent_fold(text: str) -> str:
    """Strip diacritics/accents from Unicode text while preserving length."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def detect_language(text: str) -> str:
    """Detect whether an ingredient string is English ('en'), Spanish ('es'), or French ('fr')."""
    if not isinstance(text, str):
        return "en"
    low = accent_fold(text.lower())
    if any(w in low for w in ("azucar", "rojo ", "eritrosina", "agua", "harina", "aceite")):
        return "es"
    if any(w in low for w in ("sucre", "rouge ", "eau", "farine", "huile")):
        return "fr"
    return "en"


def alias_in_language(additive: str, lang: str) -> list[str]:
    """Return known aliases for additive in language lang."""
    add_key = additive.upper().strip()
    lang_key = lang.lower().strip()
    return list(TRANSLATIONS.get(add_key, {}).get(lang_key, []))


def translate_alias(alias: str, target_lang: str = "en") -> str:
    """Translate a known additive alias into the primary term in target_lang."""
    if not isinstance(alias, str) or not alias.strip():
        raise ValueError("alias must be a non-empty string")
    folded = accent_fold(alias.lower().strip())
    for add_key, lang_map in TRANSLATIONS.items():
        for terms in lang_map.values():
            if any(accent_fold(t.lower()) == folded for t in terms):
                target_terms = lang_map.get(target_lang.lower(), lang_map.get("en", [alias]))
                return target_terms[0] if target_terms else alias
    return alias


def multilingual_patterns(additive: str) -> list[str]:
    """Return all multilingual alias strings for an additive across all languages."""
    add_key = additive.upper().strip()
    lang_map = TRANSLATIONS.get(add_key, {})
    out: list[str] = []
    for terms in lang_map.values():
        for t in terms:
            if t not in out:
                out.append(t)
    return out


def translated_match(text: str, additive: str) -> tuple[str, int, int] | None:
    """Find the first multilingual alias match in text and return (matched_text, start, end)."""
    if not isinstance(text, str) or not text:
        return None
    folded_text = accent_fold(text)
    for term in multilingual_patterns(additive):
        folded_term = accent_fold(term)
        pat = re.compile(r"(?<![A-Za-z0-9])" + re.escape(folded_term) + r"(?![A-Za-z0-9])", re.IGNORECASE)
        m = pat.search(folded_text)
        if m:
            return (text[m.start() : m.end()], m.start(), m.end())
    return None


def language_report(text: str) -> dict:
    """Return a language detection and translation match summary for text."""
    lang = detect_language(text)
    matches = {add: translated_match(text, add) for add in TRANSLATIONS}
    return {"language": lang, "matches": {k: v[0] for k, v in matches.items() if v is not None}}


def add_translation(additive: str, lang: str, term: str) -> None:
    """Register a new translation term for an additive."""
    if not term or not isinstance(term, str):
        raise ValueError("term must be a non-empty string")
     bucket = TRANSLATIONS.setdefault(additive.upper().strip(), {}).setdefault(lang.lower().strip(), [])
    if term not in bucket:
        bucket.append(term)
