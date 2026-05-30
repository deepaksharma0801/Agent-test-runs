"""Researcher role: collect source notes from URLs or web search."""

from __future__ import annotations

from schemas import PlanStep, SourceNote
from tools.search import read_url, search_web


def _claims_from_text(text: str, max_claims: int = 3) -> list[str]:
    sentences = [sentence.strip() for sentence in text.replace("\n", " ").split(".") if len(sentence.strip()) > 60]
    return [f"{sentence}." for sentence in sentences[:max_claims]]


def gather_notes(
    plan: list[PlanStep],
    urls: list[str] | None = None,
    max_sources: int = 5,
) -> list[SourceNote]:
    candidates: list[dict[str, str]] = []
    for url in urls or []:
        candidates.append({"title": url, "url": url, "snippet": ""})

    if not candidates:
        for step in plan:
            candidates.extend(search_web(step.search_query, max_results=2))
            if len(candidates) >= max_sources:
                break

    notes: list[SourceNote] = []
    seen: set[str] = set()
    for candidate in candidates:
        url = candidate["url"]
        if url in seen:
            continue
        seen.add(url)
        page = read_url(url)
        if page is None:
            continue
        source_id = f"S{len(notes) + 1}"
        text = page["text"]
        notes.append(
            SourceNote(
                url=url,
                title=page["title"] or candidate.get("title", url),
                snippet=text[:500],
                key_claims=_claims_from_text(text),
                source_id=source_id,
            )
        )
        if len(notes) >= max_sources:
            break
    return notes
