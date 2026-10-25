"""Unit tests for recallstorm.comms.translation_localization."""
from recallstorm.comms.translation_localization import (
    CulturalAdaptationCheck,
    MultilingualNoticeEngine,
    adapt_ethnic_product_alias_descriptions,
    audit_translation_turnaround_sla,
    check_reading_grade_level_simplicity,
    generate_audio_tts_for_visually_impaired,
    map_store_demographic_language_needs,
    review_machine_translation_with_glossary,
    sync_translations_across_pos_and_signs,
    translate_recall_warning_to_spanish_chinese,
    validate_right_to_left_arabic_layout,
    verify_medical_symptom_term_accuracy,
)


def test_translation_localization():
    assert MultilingualNoticeEngine().status == "ACTIVE"
    assert CulturalAdaptationCheck().status == "ACTIVE"
    tr = translate_recall_warning_to_spanish_chinese("Do not consume")
    assert "AVISO" in tr["es"] and "召回" in tr["zh"]
    assert verify_medical_symptom_term_accuracy("anafilaxia")["verified"] is True
    assert adapt_ethnic_product_alias_descriptions("Turmeric", "Haldi") == "Turmeric (Haldi)"
    assert validate_right_to_left_arabic_layout("تحذير", True)["valid"] is True
    assert check_reading_grade_level_simplicity(12.0, 18.0)["plain_language"] is True
    assert review_machine_translation_with_glossary("Texto limpio", ["badword"])["clean"] is True
    assert generate_audio_tts_for_visually_impaired("Recall notice")["ada_ready"] is True
    assert "zh" in map_store_demographic_language_needs("CA")
    assert sync_translations_across_pos_and_signs(["en", "es", "zh"], ["en", "es"]) is True
    assert audit_translation_turnaround_sla(15.0, 30.0)["within_sla"] is True
