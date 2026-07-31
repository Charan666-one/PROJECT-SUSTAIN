from app.services.surveillance import (
    analyze_recovery, Point,
    ON_TRACK, AGGRAVATION, PLATEAU, NON_RESPONSE, RELAPSE, WORSENING,
    INFO, WATCH, URGENT,
)


def test_pending_when_no_scores():
    a = analyze_recovery([Point(day=0, score=None)])
    assert a.trend == "pending" and not a.recovered
    assert a.next_check_days == 3


def test_recovered_closes_surveillance():
    a = analyze_recovery([Point(3, 6, "improved"), Point(7, 9, "improved")])
    assert a.recovered is True
    assert a.trend == "recovered"
    assert a.next_check_days is None          # stop checking in
    assert a.suggest_re_evaluation is False


def test_improving_on_track_schedules_relaxed_check():
    a = analyze_recovery([Point(3, 4, "improved"), Point(7, 6, "improved")])
    assert a.trend == "improving" and a.anomaly == ON_TRACK
    assert a.severity == INFO
    assert a.next_check_days == 5


def test_worsening_is_urgent_and_fast_recheck():
    a = analyze_recovery([Point(3, 5), Point(5, 2, "worsened")])
    assert a.anomaly == WORSENING
    assert a.severity == URGENT
    assert a.next_check_days == 1
    assert a.suggest_re_evaluation is True     # offer a remedy re-suggestion


def test_relapse_after_improvement():
    a = analyze_recovery([Point(3, 5), Point(7, 8, "improved"), Point(14, 5, "worsened")])
    # worsened outcome triggers the worsening branch first — still flagged, urgent, re-eval.
    assert a.anomaly in (RELAPSE, WORSENING)
    assert a.suggest_re_evaluation is True


def test_pure_relapse_without_worsened_flag():
    a = analyze_recovery([Point(3, 5, "improved"), Point(7, 8, "improved"), Point(20, 6, "no_change")])
    assert a.anomaly == RELAPSE
    assert a.severity == WATCH
    assert a.suggest_re_evaluation is True


def test_homeopathic_aggravation_is_recognised_and_reassured():
    # baseline 6 -> dips to 4 early -> climbs back to 6: classic aggravation, not alarming.
    a = analyze_recovery([Point(1, 6), Point(3, 4), Point(7, 6, "improved")])
    assert a.anomaly == AGGRAVATION
    assert a.severity == INFO
    assert a.suggest_re_evaluation is False


def test_plateau_flags_re_evaluation():
    a = analyze_recovery([Point(3, 5, "no_change"), Point(9, 5, "no_change")])
    assert a.anomaly in (PLATEAU, NON_RESPONSE)
    assert a.suggest_re_evaluation is True
    assert a.severity == WATCH


def test_non_response_by_expected_day():
    a = analyze_recovery([Point(3, 4, "no_change"), Point(8, 4, "no_change")])
    assert a.anomaly == NON_RESPONSE
    assert a.suggest_re_evaluation is True


def test_doctor_always_in_loop():
    for pts in ([Point(3, 9, "improved")], [Point(3, 2, "worsened")], [Point(3, 5, "no_change")]):
        assert analyze_recovery(pts).doctor_in_loop is True
