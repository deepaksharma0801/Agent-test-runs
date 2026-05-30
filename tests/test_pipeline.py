from agents.critic import critique_research
from agents.pipeline import run_research_agent
from agents.writer import write_brief
from schemas import PlanStep, ResearchTask, SourceNote


def test_pipeline_refuses_to_guess_without_sources(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    state = run_research_agent("What is a deliberately obscure impossible question?", save_memory=False)

    assert state.plan
    assert state.final_brief is not None
    assert "could not collect readable sources" in state.final_brief.answer
    assert state.eval_log is not None
    assert state.eval_log.sources_found == 0


def test_critic_flags_missing_sources():
    plan = [PlanStep(1, "What is X?", "x evidence", "Need evidence")]
    critique = critique_research(plan, [])

    assert critique.missing_citations
    assert critique.hallucination_risks


def test_writer_includes_source_citations():
    task = ResearchTask("What is useful?")
    note = SourceNote(
        url="https://example.com",
        title="Example",
        snippet="A useful system should expose clear evidence.",
        key_claims=["A useful system should expose clear evidence."],
        source_id="S1",
    )
    brief = write_brief(task, [note], critique_research([], [note]))

    assert "[S1]" in brief.answer
    assert brief.citations[0].source_id == "S1"
