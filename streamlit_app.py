"""Public portfolio UI for the local-first research agent."""

from __future__ import annotations

import json

import streamlit as st

from agents.pipeline import run_research_agent
from tools.search import extract_urls
from ui_format import EXAMPLE_PROMPTS, final_brief_markdown, run_status_message


st.set_page_config(
    page_title="Local Research Agent",
    layout="wide",
)


def parse_url_lines(raw_urls: str) -> list[str]:
    return extract_urls(line for line in raw_urls.splitlines() if line.strip())


def render_plan(state) -> None:
    st.subheader("Planner")
    for step in state.plan:
        with st.container(border=True):
            st.markdown(f"**Step {step.id}:** {step.question}")
            st.caption(f"Search query: `{step.search_query}`")
            st.write(step.rationale)


def render_research(state) -> None:
    st.subheader("Researcher")
    if not state.notes:
        st.info("No readable source notes were collected. The final brief will avoid unsupported factual claims.")
        return
    for note in state.notes:
        with st.expander(f"{note.source_id}: {note.title}", expanded=True):
            st.write(note.url)
            st.write(note.snippet)
            if note.key_claims:
                st.markdown("**Extracted claims**")
                for claim in note.key_claims:
                    st.markdown(f"- {claim}")


def render_critic(state) -> None:
    st.subheader("Critic")
    critique = state.critique
    warnings = critique.missing_citations + critique.weak_claims + critique.contradictions + critique.hallucination_risks
    if not warnings:
        st.success("No major evidence warnings found.")
        return
    for warning in warnings:
        st.warning(warning)


def render_writer(state) -> None:
    st.subheader("Writer")
    if state.final_brief is None:
        st.error("No final brief was generated.")
        return
    markdown = final_brief_markdown(state.final_brief)
    st.markdown(markdown)
    st.text_area("Copy-friendly final brief", markdown, height=320)


def render_evaluation(state) -> None:
    st.subheader("Evaluation")
    if state.eval_log is None:
        st.info("No evaluation log was generated.")
        return
    col1, col2, col3 = st.columns(3)
    col1.metric("Sources found", state.eval_log.sources_found)
    col2.metric("Claims with citations", state.eval_log.claims_with_citations)
    col3.metric("Source budget", state.eval_log.max_sources)
    with st.expander("Evaluation details", expanded=True):
        st.json(state.eval_log.__dict__)


st.title("Local Research Agent")
st.caption("A free, local-first research assistant that shows its planner, researcher, critic, and writer steps.")

with st.sidebar:
    st.header("Run Settings")
    st.write("Hosted demo mode works without Ollama or API keys. Local Ollama improves planning when available.")
    max_sources = st.slider("Max readable sources", min_value=1, max_value=8, value=5)
    model = st.text_input("Local Ollama model", value="llama3.2:3b")
    save_memory = st.checkbox("Save run to local memory", value=False)

if "question" not in st.session_state:
    st.session_state.question = EXAMPLE_PROMPTS[0]

prompt_cols = st.columns(len(EXAMPLE_PROMPTS))
for index, prompt in enumerate(EXAMPLE_PROMPTS):
    if prompt_cols[index].button(prompt, use_container_width=True):
        st.session_state.question = prompt

question = st.text_input("Research question", key="question")

raw_urls = st.text_area(
    "Optional source URLs",
    placeholder="https://docs.python.org/3/library/argparse.html\nhttps://example.com/article",
    help="One URL per line. Explicit URLs make hosted demos more repeatable.",
)

run_clicked = st.button("Run agent", type="primary")

if run_clicked:
    urls = parse_url_lines(raw_urls)
    if not question.strip():
        st.error("Enter a research question first.")
    else:
        with st.spinner("Running planner, researcher, critic, and writer..."):
            state = run_research_agent(
                question=question.strip(),
                urls=urls,
                max_sources=max_sources,
                model=model.strip() or "llama3.2:3b",
                save_memory=save_memory,
            )
        title, body = run_status_message(state)
        if state.notes:
            st.success(f"{title}. {body}")
        else:
            st.warning(f"{title}. {body}")

        tabs = st.tabs(["Planner", "Researcher", "Critic", "Writer", "Evaluation", "Raw State"])
        with tabs[0]:
            render_plan(state)
        with tabs[1]:
            render_research(state)
        with tabs[2]:
            render_critic(state)
        with tabs[3]:
            render_writer(state)
        with tabs[4]:
            render_evaluation(state)
        with tabs[5]:
            st.json(state.to_dict())
            st.download_button(
                "Download run JSON",
                data=json.dumps(state.to_dict(), indent=2, ensure_ascii=False),
                file_name="research-agent-run.json",
                mime="application/json",
            )
else:
    st.info("Enter a question and run the agent. Use URLs for the most reliable portfolio demo.")
