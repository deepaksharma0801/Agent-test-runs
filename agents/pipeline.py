"""End-to-end multi-agent research pipeline."""

from __future__ import annotations

from agents.critic import critique_research
from agents.planner import create_plan
from agents.researcher import gather_notes
from agents.writer import write_brief
from evals.evaluate import build_eval_log
from memory.store import JsonMemoryStore
from schemas import AgentState, ResearchTask
from tools.ollama_client import OllamaClient


def run_research_agent(
    question: str,
    urls: list[str] | None = None,
    max_sources: int = 5,
    model: str = "llama3.2:3b",
    save_memory: bool = True,
) -> AgentState:
    task = ResearchTask(
        question=question,
        constraints=[
            "Cite every important claim.",
            f"Stop after at most {max_sources} readable sources.",
            "Say when evidence is missing instead of guessing.",
        ],
    )
    state = AgentState(task=task)
    client = OllamaClient(model=model)

    state.plan = create_plan(task, client=client)
    state.notes = gather_notes(state.plan, urls=urls, max_sources=max_sources)
    state.critique = critique_research(state.plan, state.notes)
    state.final_brief = write_brief(task, state.notes, state.critique)
    state.eval_log = build_eval_log(state.notes, state.critique, max_sources)

    if save_memory:
        JsonMemoryStore().append(state.to_dict())
    return state
