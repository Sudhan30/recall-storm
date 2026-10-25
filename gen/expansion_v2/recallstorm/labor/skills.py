"""Associate skill matrix and task certification."""
from __future__ import annotations

from dataclasses import dataclass, field

from contract import Action, Associate


@dataclass
class SkillBook:
    """Registry of certified associate skills."""

    by_assoc: dict[str, set[str]] = field(default_factory=dict)


def skill_for_task(action: Action) -> str:
    """Return the required skill name for a contract Action."""
    mapping = {
        Action.PULL: "SHELF_PULL",
        Action.HOLD_VERIFY: "QA_VERIFY",
        Action.PLACE_SUB: "MERCH_STOCK",
        Action.TAG_FLASH: "SIGNAGE_TAG",
    }
    return mapping[action]


def associate_skills(assoc: Associate) -> tuple[str, ...]:
    """Return default certified skills for an Associate."""
    base = ["SHELF_PULL", "QA_VERIFY", "MERCH_STOCK", "SIGNAGE_TAG"]
    if assoc.is_floater:
        base.append("FLOATER_RAPID_RESPONSE")
    return tuple(base)


def can_handle_action(assoc: Associate, action: Action) -> bool:
    """Return True if assoc is certified to perform action."""
    req = skill_for_task(action)
    return req in associate_skills(assoc)


def certify_associate(assoc_id: str, skill: str, book: SkillBook | None = None) -> SkillBook:
    """Add skill certification for assoc_id in book."""
    sb = book or SkillBook()
    sb.by_assoc.setdefault(assoc_id, set()).add(skill)
    return sb


def skill_matrix(associates: list[Associate]) -> dict[str, tuple[str, ...]]:
    """Return mapping of associate_id -> certified skills tuple."""
    return {a.associate_id: associate_skills(a) for a in associates}


def skill_gaps(associates: list[Associate], actions: list[Action]) -> list[str]:
    """Return required skills for actions that no associate in associates possesses."""
    available: set[str] = set()
    for a in associates:
        available.update(associate_skills(a))
    needed = {skill_for_task(act) for act in actions}
    return sorted(needed - available)


def train_plan(gaps: list[str]) -> list[dict]:
    """Build training module assignments for any identified skill gaps."""
    return [{"skill": g, "duration_mins": 15} for g in gaps]


def skills_summary(associates: list[Associate]) -> dict:
    """Summarize associate skills across the roster."""
    return {
        "associate_count": len(associates),
        "floater_count": sum(1 for a in associates if a.is_floater),
    }
