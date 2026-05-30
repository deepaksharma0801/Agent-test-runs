from schemas import AgentState, Citation, Critique, FinalBrief, ResearchTask, SourceNote
from ui_format import final_brief_markdown, run_status_message


def test_final_brief_markdown_is_copy_friendly():
    brief = FinalBrief(
        question="What is useful?",
        answer="Useful systems expose evidence. [S1]",
        citations=[Citation("S1", "Example", "https://example.com")],
        limitations=["Verify important claims manually."],
        follow_up_questions=["What source is authoritative?"],
    )

    markdown = final_brief_markdown(brief)

    assert "## Citations" in markdown
    assert "[S1] [Example](https://example.com)" in markdown
    assert "## Follow-up Questions" in markdown


def test_run_status_message_praises_refusal_without_sources():
    state = AgentState(task=ResearchTask("Question"))

    title, body = run_status_message(state)

    assert title == "No readable sources collected"
    assert "refused to invent citations" in body


def test_run_status_message_surfaces_critic_warnings():
    state = AgentState(
        task=ResearchTask("Question"),
        notes=[
            SourceNote(
                url="https://example.com",
                title="Example",
                snippet="Evidence text",
                key_claims=["Evidence text"],
                source_id="S1",
            )
        ],
        critique=Critique(weak_claims=["Only one source."]),
    )

    title, body = run_status_message(state)

    assert title == "Brief generated with evidence cautions"
    assert "critic found caveats" in body
