from app.services.clarify import generate_clarifying_questions


def test_asks_about_missing_modalities_and_mentals():
    qs = generate_clarifying_questions({"chief_complaint": "headache"})
    assert 1 <= len(qs) <= 5
    assert any("better or worse" in q for q in qs)


def test_fewer_questions_when_more_is_provided():
    full = generate_clarifying_questions({
        "chief_complaint": "headache that started after grief",
        "modalities": {"worse": "evening", "better": "rest"},
        "mental_emotional": "weepy and sad",
        "physical_generals": "thirstless, chilly",
    })
    sparse = generate_clarifying_questions({"chief_complaint": "headache"})
    assert len(full) <= len(sparse)
