"""Planner role: break a research question into focused subtasks."""

from __future__ import annotations

import json

from schemas import PlanStep, ResearchTask
from tools.ollama_client import OllamaClient


PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "search_query": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["question", "search_query", "rationale"],
            },
        }
    },
    "required": ["steps"],
}


def fallback_plan(task: ResearchTask) -> list[PlanStep]:
    base = task.question.strip()
    return [
        PlanStep(1, f"What are the core concepts behind: {base}?", base, "Establish definitions and context."),
        PlanStep(2, f"What evidence or examples answer: {base}?", f"{base} examples evidence", "Gather concrete support."),
        PlanStep(3, f"What are limitations or open questions for: {base}?", f"{base} limitations challenges", "Avoid overclaiming."),
    ]


def create_plan(task: ResearchTask, client: OllamaClient | None = None) -> list[PlanStep]:
    client = client or OllamaClient()
    prompt = (
        "Create 3 to 5 web research subtasks for this question. "
        "Each step needs a focused question, a web search query, and a rationale.\n\n"
        f"Question: {task.question}\nScope: {task.scope}\nConstraints: {task.constraints}"
    )
    response = client.generate(
        prompt,
        system="You are a careful research planner. Return only JSON matching the schema.",
        schema=PLAN_SCHEMA,
    )
    if not response:
        return fallback_plan(task)

    try:
        data = json.loads(response)
        steps = data.get("steps", [])[:5]
        return [
            PlanStep(
                id=index + 1,
                question=step["question"],
                search_query=step["search_query"],
                rationale=step["rationale"],
            )
            for index, step in enumerate(steps)
            if step.get("question") and step.get("search_query")
        ] or fallback_plan(task)
    except (json.JSONDecodeError, KeyError, TypeError):
        return fallback_plan(task)
