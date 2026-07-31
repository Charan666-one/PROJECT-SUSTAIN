"""
Recovery Surveillance engine — the product's differentiator.

Instead of a one-shot AI prescription, we track each patient's recovery
*trajectory* over the whole episode and keep checking in until they recover.
This module is pure, rule-based, and explainable (important for clinical trust
and testability): given the sequence of follow-up data points it classifies the
recovery trend, flags anomalies, recommends the doctor's next action, and picks
an adaptive interval for the next check-in.

Score convention: ``score`` is a 1-10 WELLNESS score where 10 = fully recovered
and 1 = very unwell (matches the follow-up UI). ``outcome`` is one of
improved / no_change / worsened / not_reported.

Everything here is DECISION SUPPORT. The doctor takes every action; the engine
only surfaces what to look at and suggests a next step.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

RECOVERED_SCORE = 8          # >= this wellness score counts as recovered
PLATEAU_MIN_DAYS = 6         # no meaningful gain over this many days = plateau
NON_RESPONSE_DAY = 7         # still no gain by this day = non-response
RELAPSE_DROP = 2             # drop of this much after a good score = relapse

# Anomaly taxonomy
ON_TRACK = "on_track"
AGGRAVATION = "aggravation"      # early worsening then improvement (expected in homeopathy)
PLATEAU = "plateau"              # stuck, no meaningful improvement
NON_RESPONSE = "non_response"    # never responded
RELAPSE = "relapse"             # improved, then slipped back
WORSENING = "worsening"          # actively getting worse

# Severity of the flag for triage colour-coding
INFO, WATCH, URGENT = "info", "watch", "urgent"


@dataclass
class Point:
    day: int                     # days since the prescription
    score: Optional[int]         # 1-10 wellness, or None if not reported
    outcome: str = "not_reported"


@dataclass
class RecoveryAssessment:
    trend: str                   # improving / plateau / worsening / recovered / pending
    anomaly: str                 # from the taxonomy above
    severity: str                # info / watch / urgent
    recovered: bool
    recommended_action: str      # decision support for the doctor
    suggest_re_evaluation: bool  # true -> offer a remedy re-suggestion (RAG)
    next_check_days: Optional[int]  # adaptive interval; None if recovered/closed
    days_under_surveillance: int
    latest_score: Optional[int]
    rationale: str
    doctor_in_loop: bool = True  # always — we never act autonomously

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        return d


def _scored(points: List[Point]) -> List[Point]:
    return [p for p in points if p.score is not None]


def analyze_recovery(points: List[Point]) -> RecoveryAssessment:
    points = sorted(points, key=lambda p: p.day)
    days = points[-1].day if points else 0
    scored = _scored(points)
    latest = scored[-1] if scored else None
    latest_score = latest.score if latest else None

    # No data yet — surveillance is pending the first check-in.
    if not scored:
        return RecoveryAssessment(
            trend="pending", anomaly=ON_TRACK, severity=INFO, recovered=False,
            recommended_action="Awaiting the first check-in.",
            suggest_re_evaluation=False, next_check_days=3,
            days_under_surveillance=days, latest_score=None,
            rationale="No patient-reported outcome recorded yet.",
        )

    first = scored[0]
    peak = max(p.score for p in scored)  # best wellness reached so far

    # --- Recovered ---
    if latest.score >= RECOVERED_SCORE and latest.outcome != "worsened":
        return RecoveryAssessment(
            trend="recovered", anomaly=ON_TRACK, severity=INFO, recovered=True,
            recommended_action="Recovered — you can close this surveillance episode.",
            suggest_re_evaluation=False, next_check_days=None,
            days_under_surveillance=days, latest_score=latest_score,
            rationale=f"Latest wellness score {latest.score}/10 meets the recovery threshold.",
        )

    # --- Worsening (active decline / worsened report / very low score) ---
    if latest.outcome == "worsened" or latest.score <= 3:
        return RecoveryAssessment(
            trend="worsening", anomaly=WORSENING, severity=URGENT, recovered=False,
            recommended_action="Re-evaluate now — consider changing the remedy, and rule out red flags / conventional referral.",
            suggest_re_evaluation=True, next_check_days=1,
            days_under_surveillance=days, latest_score=latest_score,
            rationale="Patient is actively worsening or reports a low wellness score.",
        )

    # --- Relapse (reached a good level, then dropped back) ---
    if peak >= RECOVERED_SCORE - 1 and latest.score <= peak - RELAPSE_DROP:
        return RecoveryAssessment(
            trend="worsening", anomaly=RELAPSE, severity=WATCH, recovered=False,
            recommended_action="Relapse after improvement — consider repeating the last effective remedy.",
            suggest_re_evaluation=True, next_check_days=2,
            days_under_surveillance=days, latest_score=latest_score,
            rationale=f"Wellness peaked at {peak}/10 then fell to {latest.score}/10.",
        )

    # --- Aggravation (early dip below baseline, now climbing back) — expected in homeopathy ---
    trough_idx = min(range(len(scored)), key=lambda i: scored[i].score)
    trough = scored[trough_idx].score
    dipped_early = (
        trough < first.score                 # went below baseline
        and trough_idx < len(scored) - 1     # trough isn't the latest point
        and trough_idx <= max(1, len(scored) // 2)  # dip happened early
    )
    if dipped_early and latest.score >= trough + 1 and latest.score >= first.score - 1:
        return RecoveryAssessment(
            trend="improving", anomaly=AGGRAVATION, severity=INFO, recovered=False,
            recommended_action="Likely a homeopathic aggravation — reassure the patient and continue watching.",
            suggest_re_evaluation=False, next_check_days=2,
            days_under_surveillance=days, latest_score=latest_score,
            rationale=f"Early dip to {trough}/10 followed by recovery toward {latest.score}/10.",
        )

    # --- Improving on track ---
    if latest.score >= first.score + 1 or latest.outcome == "improved":
        return RecoveryAssessment(
            trend="improving", anomaly=ON_TRACK, severity=INFO, recovered=False,
            recommended_action="On track — continue the current remedy and keep monitoring.",
            suggest_re_evaluation=False, next_check_days=5,
            days_under_surveillance=days, latest_score=latest_score,
            rationale=f"Wellness improved from {first.score}/10 to {latest.score}/10.",
        )

    # --- Non-response (no gain by the expected day) ---
    if days >= NON_RESPONSE_DAY and latest.score <= first.score:
        return RecoveryAssessment(
            trend="plateau", anomaly=NON_RESPONSE, severity=WATCH, recovered=False,
            recommended_action="No response by the expected point — consider a different remedy or re-taking the case.",
            suggest_re_evaluation=True, next_check_days=2,
            days_under_surveillance=days, latest_score=latest_score,
            rationale=f"No improvement over {days} days (still {latest.score}/10).",
        )

    # --- Plateau (stuck, meaningful days elapsed) ---
    if days >= PLATEAU_MIN_DAYS and abs(latest.score - first.score) < 1:
        return RecoveryAssessment(
            trend="plateau", anomaly=PLATEAU, severity=WATCH, recovered=False,
            recommended_action="Plateau — consider repeating the dose or re-evaluating the remedy.",
            suggest_re_evaluation=True, next_check_days=2,
            days_under_surveillance=days, latest_score=latest_score,
            rationale=f"Wellness flat around {latest.score}/10 for {days} days.",
        )

    # --- Default: early days, holding steady ---
    return RecoveryAssessment(
        trend="pending", anomaly=ON_TRACK, severity=INFO, recovered=False,
        recommended_action="Too early to judge — continue and reassess at the next check-in.",
        suggest_re_evaluation=False, next_check_days=3,
        days_under_surveillance=days, latest_score=latest_score,
        rationale="Not enough trend yet to classify.",
    )
