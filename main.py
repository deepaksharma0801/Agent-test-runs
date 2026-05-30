"""CLI entrypoint for the local research agent."""

from __future__ import annotations

import argparse
import json

from agents.pipeline import run_research_agent
from tools.search import extract_urls


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a local-first multi-agent research assistant.")
    parser.add_argument("question", help="Research question to investigate.")
    parser.add_argument("--url", action="append", default=[], help="Optional source URL. Can be repeated.")
    parser.add_argument("--max-sources", type=int, default=5, help="Maximum readable sources to collect.")
    parser.add_argument("--model", default="llama3.2:3b", help="Ollama model name.")
    parser.add_argument("--json", action="store_true", help="Print the full agent state as JSON.")
    parser.add_argument("--no-memory", action="store_true", help="Do not append this run to memory/runs.jsonl.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    state = run_research_agent(
        question=args.question,
        urls=extract_urls(args.url),
        max_sources=args.max_sources,
        model=args.model,
        save_memory=not args.no_memory,
    )

    if args.json:
        print(json.dumps(state.to_dict(), indent=2, ensure_ascii=False))
        return 0

    brief = state.final_brief
    if brief is None:
        print("No brief was generated.")
        return 1

    print(brief.answer)
    print("\nCitations:")
    if brief.citations:
        for citation in brief.citations:
            print(f"- [{citation.source_id}] {citation.title}: {citation.url}")
    else:
        print("- No citations available.")

    print("\nLimitations:")
    for limitation in brief.limitations:
        print(f"- {limitation}")

    print("\nEvaluation:")
    if state.eval_log:
        print(json.dumps(state.eval_log.__dict__, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
