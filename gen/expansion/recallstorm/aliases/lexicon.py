"""Canonical additive lexicon with aliases, E-numbers, CI numbers, and rule extraction."""
from __future__ import annotations

from dataclasses import dataclass
from contract import Rule
from recallstorm.aliases.translations import TRANSLATIONS, multilingual_patterns

_DEFAULT_ALIASES: dict[str, tuple[str, ...]] = {
    "RED3": (
        "FD&C Red No. 3",
        "FD&C Red #3",
        "FD&C Red 3",
        "Red No. 3",
        "Red #3",
        "Red 3",
        "Red Dye 3",
        "Red Dye #3",
        "Red Dye No. 3",
        "erythrosine",
        "erythrosin",
        "eritrosina",
        "E127",
        "E-127",
        "E 127",
        "CI 45430",
        "C.I. 45430",
        "INS 127",
    ),
    "BVO": (
        "brominated vegetable oil",
        "BVO",
        "E443",
        "aceite vegetal bromado",
        "huile vegetale bromee",
    ),
    "POTASSIUM_BROMATE": (
        "potassium bromate",
        "bromated flour",
        "E924",
        "E924a",
        "bromato de potasio",
    ),
    "PROPYLPARABEN": (
        "propylparaben",
        "propyl paraben",
        "propyl p-hydroxybenzoate",
        "E216",
        "E217",
        "propilparabeno",
    ),
    "PFAS": (
        "PTFE",
        "polytetrafluoroethylene",
        "PFOA",
        "PFOS",
        "fluoroalkyl",
        "perfluoro",
        "teflon coating",
    ),
}

_E_NUMBERS = {
    "RED3": "E127",
    "BVO": "E443",
    "POTASSIUM_BROMATE": "E924",
    "PROPYLPARABEN": "E216",
}

_CI_NUMBERS = {
    "RED3": "CI 45430",
}


@dataclass(frozen=True)
class Lexicon:
    """Immutable mapping of additive code to tuple of aliases."""

    entries: dict[str, tuple[str, ...]]


def load_lexicon() -> Lexicon:
    """Load the default built-in additive lexicon."""
    return Lexicon(entries=dict(_DEFAULT_ALIASES))


def aliases_for(additive: str, lex: Lexicon | None = None) -> tuple[str, ...]:
    """Return all known aliases for an additive."""
    if not isinstance(additive, str) or not additive.strip():
        raise ValueError("additive must be a non-empty string")
    lx = lex or load_lexicon()
    return lx.entries.get(additive.strip().upper(), ())


def additive_for_alias(alias: str, lex: Lexicon | None = None) -> str | None:
    """Look up the canonical additive code for a given alias string."""
    if not isinstance(alias, str) or not alias.strip():
        return None
    lx = lex or load_lexicon()
    q = alias.strip().lower()
    for add, terms in lx.entries.items():
        if any(t.lower() == q for t in terms):
            return add
    return None


def add_alias(lex: Lexicon, additive: str, alias: str) -> Lexicon:
    """Return a new Lexicon with alias added under additive."""
    if not isinstance(lex, Lexicon):
        raise TypeError("lex must be a Lexicon")
    if not additive.strip() or not alias.strip():
        raise ValueError("additive and alias must be non-empty")
    key = additive.strip().upper()
    existing = list(lex.entries.get(key, ()))
    if alias.strip() not in existing:
        existing.append(alias.strip())
    new_entries = dict(lex.entries)
    new_entries[key] = tuple(existing)
    return Lexicon(entries=new_entries)


def e_number_for(additive: str) -> str | None:
    """Return the European E-number for an additive if known."""
    return _E_NUMBERS.get(additive.strip().upper())


def ci_number_for(additive: str) -> str | None:
    """Return the Colour Index (CI) number for an additive if known."""
    return _CI_NUMBERS.get(additive.strip().upper())


def translations_for(additive: str) -> list[str]:
    """Return multilingual translations for an additive."""
    add = additive.strip().upper()
    if add in TRANSLATIONS:
        return multilingual_patterns(add)
    return list(aliases_for(add))


def lexicon_from_rules(rules: list[Rule]) -> Lexicon:
    """Build a Lexicon combining built-in aliases with aliases declared in Rule objects."""
    lex = load_lexicon()
    for r in rules:
        for a in r.aliases:
            lex = add_alias(lex, r.additive, a)
    return lex
