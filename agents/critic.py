"""Critic role: flag weak evidence before writing the final brief."""

from __future__ import annotations

from schemas import Critique, PlanStep, SourceNote


def critique_research(plan: list[PlanStep], notes: list[SourceNote]) -> Critique:
    critique = Critique()

    if not notes:
        critique.missing_citations.append("No readable sources were collected.")
        critique.hallucination_risks.append("Any factual answer would be unsupported without source notes.")
        return critique

    if len(notes) < 2:
        critique.weak_claims.append("Only one readable source was collected; compare with more sources before trusting broad claims.")

    covered_text = " ".join(note.snippet.lower() for note in notes)
    for step in plan:
        tokens = [token.lower() for token in step.search_query.split() if len(token) > 4]
        if tokens and not any(token in covered_text for token in tokens):
            critique.weak_claims.append(f"Limited evidence found for plan step {step.id}: {step.question}")

    for note in notes:
        if not note.key_claims:
            critique.missing_citations.append(f"{note.source_id} was readable but did not yield clear claims.")

    return critique
