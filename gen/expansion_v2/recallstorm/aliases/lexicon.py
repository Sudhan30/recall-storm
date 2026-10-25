"""Additive alias lexicon, E-numbers, CI numbers, and rule extraction."""
from __future__ import annotations

from dataclasses import dataclass, field

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
        "Red Dye No. 3",
        "Red Dye #3",
        "erythrosine",
        "erythrosin",
        "E127",
        "E-127",
        "E 127",
        "CI 45430",
        "C.I. 45430",
        "Acid Red 51",
        "Rojo 3",
        "Rojo No. 3",
        "Rojo #3",
        "eritrosina",
        "Rouge 3",
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
        "propyl 4-hydroxybenzoate",
        "E216",
        "E217",
        "propilparabeno",
    ),
    "PFAS": (
        "PFAS",
        "PTFE",
        "polytetrafluoroethylene",
        "perfluoroalkyl",
        "polyfluoroalkyl",
        "PFOA",
        "PFOS",
        "fluoro-treated",
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


@dataclass
class Lexicon:
    """Canonical additive-to-aliases dictionary."""

    by_additive: dict[str, tuple[str, ...]] = field(default_factory=lambda: dict(_DEFAULT_ALIASES))


def load_lexicon() -> Lexicon:
    """Load the default additive alias lexicon."""
    return Lexicon()


def aliases_for(additive: str, lexicon: Lexicon | None = None) -> tuple[str, ...]:
    """Return tuple of aliases for additive."""
    lex = lexicon or load_lexicon()
    return lex.by_additive.get(additive.upper().strip(), ())


def additive_for_alias(alias: str, lexicon: Lexicon | None = None) -> str | None:
    """Resolve an alias string back to its canonical additive code."""
    if not isinstance(alias, str) or not alias.strip():
        return None
    lex = lexicon or load_lexicon()
    target = alias.lower().strip()
    for add, terms in lex.by_additive.items():
        if any(t.lower() == target for t in terms):
            return add
    return None


def add_alias(lexicon: Lexicon, additive: str, alias: str) -> Lexicon:
    """Add a new alias to lexicon for additive."""
    if not isinstance(alias, str) or not alias.strip():
        raise ValueError("alias must be a non-empty string")
    key = additive.upper().strip()
    cur = list(lexicon.by_additive.get(key, ()))
    if alias not in cur:
        cur.append(alias)
    lexicon.by_additive[key] = tuple(cur)
    return lexicon


def e_number_for(additive: str) -> str | None:
    """Return the European E-number for additive, if any."""
    return _E_NUMBERS.get(additive.upper().strip())


def ci_number_for(additive: str) -> str | None:
    """Return the Colour Index (CI) number for additive, if any."""
    return _CI_NUMBERS.get(additive.upper().strip())


def translations_for(additive: str) -> list[str]:
    """Return all multilingual terms for additive."""
    key = additive.upper().strip()
    return multilingual_patterns(key) if key in TRANSLATIONS else list(aliases_for(key))


def lexicon_from_rules(rules: list[Rule]) -> Lexicon:
    """Build an enriched Lexicon merging default aliases with Rule.aliases."""
    lex = load_lexicon()
    for r in rules:
        for al in r.aliases:
            add_alias(lex, r.additive, al)
    return lex
