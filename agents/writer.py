"""Writer role: produce a cited final brief from notes and critique."""

from __future__ import annotations

from schemas import Citation, Critique, FinalBrief, ResearchTask, SourceNote


def write_brief(task: ResearchTask, notes: list[SourceNote], critique: Critique) -> FinalBrief:
    citations = [Citation(note.source_id, note.title, note.url) for note in notes]
    limitations = []
    limitations.extend(critique.hallucination_risks)
    limitations.extend(critique.weak_claims[:3])

    if not notes:
        answer = (
            "I could not collect readable sources for this question in the current environment, "
            "so I should not present factual claims as researched conclusions. Try rerunning with "
            "network access or pass explicit source URLs with --url."
        )
        return FinalBrief(
            question=task.question,
            answer=answer,
            citations=[],
            limitations=limitations or ["No source evidence was available."],
            follow_up_questions=["Which authoritative sources should be used as starting points?"],
        )

    paragraphs = [f"Research question: {task.question}", ""]
    paragraphs.append("Key findings:")
    for note in notes:
        if note.key_claims:
            paragraphs.append(f"- {note.key_claims[0]} [{note.source_id}]")
        else:
            paragraphs.append(f"- {note.title} provided context but no concise claim was extracted. [{note.source_id}]")

    if critique.weak_claims or critique.missing_citations:
        paragraphs.append("")
        paragraphs.append("Evidence cautions:")
        for issue in (critique.weak_claims + critique.missing_citations)[:4]:
            paragraphs.append(f"- {issue}")

    follow_ups = [
        "What source would be considered authoritative for this topic?",
        "What would change if the scope were narrowed to one industry or year?",
    ]

    return FinalBrief(
        question=task.question,
        answer="\n".join(paragraphs),
        citations=citations,
        limitations=limitations or ["Source extraction is lightweight; verify important claims manually."],
        follow_up_questions=follow_ups,
    )
