"""Formatting helpers shared by the CLI tests and Streamlit app."""

from __future__ import annotations

from schemas import AgentState, FinalBrief


EXAMPLE_PROMPTS = [
    "What are the best ways to evaluate RAG systems?",
    "How should a beginner build their first AI agent?",
    "What are common failure modes in multi-agent systems?",
]


def final_brief_markdown(brief: FinalBrief) -> str:
    lines = [brief.answer.strip(), "", "## Citations"]
    if brief.citations:
        for citation in brief.citations:
            lines.append(f"- [{citation.source_id}] [{citation.title}]({citation.url})")
    else:
        lines.append("- No citations available.")

    lines.extend(["", "## Limitations"])
    for limitation in brief.limitations:
        lines.append(f"- {limitation}")

    lines.extend(["", "## Follow-up Questions"])
    for question in brief.follow_up_questions:
        lines.append(f"- {question}")
    return "\n".join(lines)


def run_status_message(state: AgentState) -> tuple[str, str]:
    if not state.notes:
        return (
            "No readable sources collected",
            "The agent refused to invent citations. Add URLs or try again with network access for stronger evidence.",
        )
    if state.critique.weak_claims or state.critique.missing_citations:
        return (
            "Brief generated with evidence cautions",
            "The critic found caveats. Review the warnings before treating the output as reliable.",
        )
    return ("Brief generated", "The agent collected source notes and produced a cited answer.")
