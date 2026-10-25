"""Multilingual translations (Spanish, French, German) and accent folding for food additives."""
from __future__ import annotations

import re
import unicodedata

TRANSLATIONS: dict[str, dict[str, list[str]]] = {
    "RED3": {
        "en": ["FD&C Red No. 3", "Red No. 3", "Red 3", "Red Dye 3", "erythrosine", "E127", "CI 45430"],
        "es": ["eritrosina", "rojo 3", "rojo no. 3", "colorante rojo 3"],
        "fr": ["érythrosine", "erythrosine", "rouge 3"],
        "de": ["erythrosin", "E 127"],
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
    """Strip diacritics/accents from Unicode text while preserving character length."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def detect_language(text: str) -> str:
    """Detect whether an ingredient statement is primarily English, Spanish, or French."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    low = accent_fold(text).lower()
    if any(w in low for w in ("azucar", "harina", "eritrosina", "jarabe", "colorante", "agua")):
        return "es"
    if any(w in low for w in ("sucre", "farine", "eau", "colorant", "sirop", "erythrosine")):
        if "sucre" in low or "farine" in low or "colorant" in low:
            return "fr"
    return "en"


def alias_in_language(additive: str, lang: str = "en") -> list[str]:
    """Return known aliases for an additive in the given 2-letter language."""
    add = additive.strip().upper()
    lg = lang.strip().lower()
    return list(TRANSLATIONS.get(add, {}).get(lg, []))


def translate_alias(alias: str, lang: str = "es") -> str:
    """Translate a canonical English additive alias to the target language's primary alias."""
    if not isinstance(alias, str) or not alias.strip():
        raise ValueError("alias must be a non-empty string")
    q = accent_fold(alias).strip().lower()
    for add, lang_map in TRANSLATIONS.items():
        for terms in lang_map.values():
            if any(accent_fold(t).lower() == q for t in terms):
                target_terms = lang_map.get(lang.lower()) or lang_map.get("en", [alias])
                return target_terms[0]
    return alias


def multilingual_patterns(additive: str) -> list[str]:
    """Return all unique aliases across all languages for an additive."""
    add = additive.strip().upper()
    lang_map = TRANSLATIONS.get(add, {})
    out: list[str] = []
    for terms in lang_map.values():
        for t in terms:
            if t not in out:
                out.append(t)
    return out


def translated_match(text: str, additive: str) -> tuple[str, int, int] | None:
    """Search text for any multilingual alias of additive, returning (matched_text, start, end)."""
    if not isinstance(text, str) or not text:
        return None
    folded_text = accent_fold(text)
    for pat in multilingual_patterns(additive):
        folded_pat = accent_fold(pat)
        m = re.search(r"(?<![A-Za-z0-9])" + re.escape(folded_pat) + r"(?![A-Za-z0-9])", folded_text, re.IGNORECASE)
        if m:
            return text[m.start():m.end()], m.start(), m.end()
    return None


def language_report(texts: list[str]) -> dict[str, int]:
    """Count detected languages across a collection of ingredient texts."""
    counts: dict[str, int] = {"en": 0, "es": 0, "fr": 0}
    for t in texts:
        lang = detect_language(t)
        counts[lang] = counts.get(lang, 0) + 1
    return counts


def add_translation(additive: str, lang: str, alias: str) -> None:
    """Register an additional translated alias for an additive."""
    if not additive.strip() or not lang.strip() or not alias.strip():
        raise ValueError("additive, lang, and alias must be non-empty")
    add = additive.strip().upper()
    lg = lang.strip().lower()
    TRANSLATIONS.setdefault(add, {}).setdefault(lg, [])
    if alias.strip() not in TRANSLATIONS[add][lg]:
        TRANSLATIONS[add][lg].append(alias.strip())
