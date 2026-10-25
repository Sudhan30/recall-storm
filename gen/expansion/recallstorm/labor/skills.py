"""Associate skill certifications for recall actions (PULL, HOLD_VERIFY, PLACE_SUB, TAG_FLASH)."""
from __future__ import annotations

from dataclasses import dataclass, field
from contract import Action, Associate


@dataclass
class SkillBook:
    """Registry of certified skills per associate_id."""

    certifications: dict[str, set[str]] = field(default_factory=dict)


def skill_for_task(action: Action | str) -> str:
    """Return the required skill code for a task Action."""
    act = action.value if isinstance(action, Action) else str(action).strip().upper()
    mapping = {
        Action.PULL.value: "SHELF_PULL",
        Action.HOLD_VERIFY.value: "COMPLIANCE_VERIFY",
        Action.PLACE_SUB.value: "MODULAR_RESTOCK",
        Action.TAG_FLASH.value: "SIGNAGE_TAG",
    }
    if act not in mapping:
        raise ValueError(f"Unknown action: {action}")
    return mapping[act]


def associate_skills(assoc: Associate) -> tuple[str, ...]:
    """Return the default certified skills for an Associate."""
    if not isinstance(assoc, Associate):
        raise TypeError("assoc must be an Associate")
    return ("SHELF_PULL", "COMPLIANCE_VERIFY", "MODULAR_RESTOCK", "SIGNAGE_TAG")


def can_handle_action(assoc: Associate, action: Action | str) -> bool:
    """Return True if assoc is certified to perform action."""
    req = skill_for_task(action)
    return req in associate_skills(assoc)


def certify_associate(skill_book: SkillBook, associate_id: str, skill: str) -> None:
    """Grant a skill certification to associate_id in skill_book."""
    if not isinstance(skill_book, SkillBook):
        raise TypeError("skill_book must be a SkillBook")
    if not associate_id.strip() or not skill.strip():
        raise ValueError("associate_id and skill must be non-empty")
    skill_book.certifications.setdefault(associate_id.strip(), set()).add(skill.strip())


def skill_gaps(associates: list[Associate], required_actions: list[Action | str]) -> list[str]:
    """Return any required skills not covered by the given associates."""
    available: set[str] = set()
    for a in associates:
        available.update(associate_skills(a))
    needed = {skill_for_task(act) for act in required_actions}
    return sorted(needed - available)


def skill_matrix(associates: list[Associate]) -> dict[str, list[str]]:
    """Map each associate_id to their sorted list of skills."""
    return {a.associate_id: sorted(associate_skills(a)) for a in associates}


def train_plan(gaps: list[str]) -> list[dict]:
    """Build training module recommendations for any identified skill gaps."""
    return [{"skill": g, "duration_mins": 15} for g in gaps]


def skills_summary(associates: list[Associate]) -> dict:
    """Summarize skill coverage across associates."""
    return {"associate_count": len(associates), "full_coverage": len(associates) > 0}
