"""Simple reliability checks for a research run."""

from __future__ import annotations

from schemas import Critique, EvaluationLog, SourceNote


def build_eval_log(notes: list[SourceNote], critique: Critique, max_sources: int) -> EvaluationLog:
    claims_with_citations = sum(1 for note in notes if note.key_claims)
    unanswered = []
    if not notes:
        unanswered.append("No readable source evidence was found.")
    if notes and len(notes) < max_sources:
        unanswered.append("Fewer sources were collected than the configured budget allowed.")

    return EvaluationLog(
        sources_found=len(notes),
        claims_with_citations=claims_with_citations,
        unanswered_questions=unanswered,
        hallucination_risk_notes=critique.hallucination_risks,
        max_sources=max_sources,
    )
