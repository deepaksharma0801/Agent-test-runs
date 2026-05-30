"""Shared data structures for the local research agent."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class ResearchTask:
    question: str
    scope: str = "Create a concise, beginner-friendly research brief."
    constraints: list[str] = field(default_factory=list)


@dataclass
class PlanStep:
    id: int
    question: str
    search_query: str
    rationale: str


@dataclass
class SourceNote:
    url: str
    title: str
    snippet: str
    key_claims: list[str]
    source_id: str


@dataclass
class Critique:
    missing_citations: list[str] = field(default_factory=list)
    weak_claims: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    hallucination_risks: list[str] = field(default_factory=list)


@dataclass
class Citation:
    source_id: str
    title: str
    url: str


@dataclass
class FinalBrief:
    question: str
    answer: str
    citations: list[Citation]
    limitations: list[str]
    follow_up_questions: list[str]


@dataclass
class EvaluationLog:
    sources_found: int
    claims_with_citations: int
    unanswered_questions: list[str]
    hallucination_risk_notes: list[str]
    max_sources: int
    generated_at: str = field(default_factory=utc_now_iso)


@dataclass
class AgentState:
    task: ResearchTask
    plan: list[PlanStep] = field(default_factory=list)
    notes: list[SourceNote] = field(default_factory=list)
    critique: Critique = field(default_factory=Critique)
    final_brief: FinalBrief | None = None
    eval_log: EvaluationLog | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
