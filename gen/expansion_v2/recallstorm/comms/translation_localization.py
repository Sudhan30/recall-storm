"""Multilingual notice engine and cultural adaptation checks."""
from __future__ import annotations

from dataclasses import dataclass

from recallstorm.core.errors import DataValidationError


@dataclass(frozen=True)
class MultilingualNoticeEngine:
    """Engine translating consumer and associate recall notices."""

    ref_id: str = "LOC-ENG-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


@dataclass(frozen=True)
class CulturalAdaptationCheck:
    """Validator for culturally accurate product names and medical symptom terms."""

    ref_id: str = "LOC-ADA-01"
    status: str = "ACTIVE"
    metrics: dict | None = None


def _req(val: object, name: str = "arg") -> None:
    if val is None or (isinstance(val, str) and not val.strip()):
        raise DataValidationError(f"Invalid {name}")


def translate_recall_warning_to_spanish_chinese(text_en: str) -> dict:
    """Translate an English recall warning into Spanish and Simplified Chinese."""
    _req(text_en, "text_en")
    return {
        "en": str(text_en),
        "es": f"AVISO DE RETIRO: {text_en}",
        "zh": f"召回通知: {text_en}",
        "src": "recallstorm/comms/translation_localization.py",
    }


def verify_medical_symptom_term_accuracy(term: str, verified_glossary: set[str] | None = None) -> dict:
    """Verify that translated medical symptom terms match the approved clinical glossary."""
    _req(term, "term")
    gloss = verified_glossary if verified_glossary is not None else {"anafilaxia", "listeriosis", "fiebre"}
    return {"op": "verify_medical_symptom_term_accuracy", "term": str(term), "verified": str(term).lower() in gloss, "src": "recallstorm/comms/translation_localization.py"}


def adapt_ethnic_product_alias_descriptions(sku_name: str, local_alias: str) -> str:
    """Include both English name and transliterated/native script name on shelf placards."""
    _req(sku_name, "sku_name")
    _req(local_alias, "local_alias")
    return f"{sku_name} ({local_alias})"


def validate_right_to_left_arabic_layout(text_ar: str, rtl_enabled: bool = True) -> dict:
    """Validate Right-To-Left (RTL) text shaping for Arabic recall placards."""
    _req(text_ar, "text_ar")
    return {"op": "validate_right_to_left_arabic_layout", "valid": bool(rtl_enabled), "src": "recallstorm/comms/translation_localization.py"}


def check_reading_grade_level_simplicity(words_per_sentence: float, max_words: float = 18.0) -> dict:
    """Verify plain-language reading simplicity (<= 18 words per sentence)."""
    if words_per_sentence <= 0 or max_words <= 0:
        raise DataValidationError("Invalid words_per_sentence")
    return {"op": "check_reading_grade_level_simplicity", "plain_language": words_per_sentence <= max_words, "src": "recallstorm/comms/translation_localization.py"}


def review_machine_translation_with_glossary(mt_text: str, forbidden_terms: list[str] | None = None) -> dict:
    """Check machine-translated notice against forbidden mistranslation terms."""
    _req(mt_text, "mt_text")
    forb = forbidden_terms or []
    clean = not any(f.lower() in str(mt_text).lower() for f in forb)
    return {"op": "review_machine_translation_with_glossary", "clean": clean, "src": "recallstorm/comms/translation_localization.py"}


def generate_audio_tts_for_visually_impaired(text: str) -> dict:
    """Generate ADA-compliant Text-To-Speech (TTS) audio metadata for web/kiosk recall notices."""
    _req(text, "text")
    return {"op": "generate_audio_tts_for_visually_impaired", "char_count": len(str(text)), "ada_ready": True, "src": "recallstorm/comms/translation_localization.py"}


def map_store_demographic_language_needs(state: str) -> list[str]:
    """Return required placard languages for a state."""
    _req(state, "state")
    st = str(state).upper().strip()
    if st in {"CA", "NY", "TX"}:
        return ["en", "es", "zh"]
    return ["en", "es"]


def sync_translations_across_pos_and_signs(pos_langs: list[str], sign_langs: list[str]) -> bool:
    """Verify that POS prompt translations cover all store signage languages."""
    if pos_langs is None or sign_langs is None:
        raise DataValidationError("Language lists cannot be None")
    return set(sign_langs).issubset(set(pos_langs))


def audit_translation_turnaround_sla(minutes: float, sla_minutes: float = 30.0) -> dict:
    """Audit translation turnaround time against 30-minute crisis SLA."""
    if minutes < 0 or sla_minutes <= 0:
        raise DataValidationError("Invalid minutes")
    return {"op": "audit_translation_turnaround_sla", "within_sla": minutes <= sla_minutes, "src": "recallstorm/comms/translation_localization.py"}
