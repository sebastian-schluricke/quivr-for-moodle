"""
Regression tests for the prompt-template structure around custom_instructions.

These tests guard the contract between `rag_service.py` / `quivr_rag_langgraph.py`
(which set `retrieval_config.prompt` and inject it as `custom_instructions`) and
`prompts.py` (which must render it so that LLMs actually follow it).

The critical property: `custom_instructions` must appear BEFORE the default
answering style in the rendered system prompt, with language strong enough
that the LLM treats it as authoritative over defaults and over the RAG
"answer from context" directive. The old template had it at the bottom
introduced with "If not None, ..." — weak enough that LLMs ignored it when
it conflicted with "answer from the context", producing the bug where a
Socratic-tutor instruction was silently ignored while the model gave
direct answers from the RAG context.
"""

from quivr_core.prompts import custom_prompts


def _render_rag_system(custom_instructions: str, files: str = "file1.pdf") -> str:
    """Render only the system message of RAG_ANSWER_PROMPT."""
    messages = custom_prompts.RAG_ANSWER_PROMPT.format_messages(
        custom_instructions=custom_instructions,
        files=files,
        context="some context",
        question="some question",
        chat_history=[],
    )
    return messages[0].content


def _render_chat_llm_system(custom_instructions: str) -> str:
    """Render only the system message of CHAT_LLM_PROMPT."""
    messages = custom_prompts.CHAT_LLM_PROMPT.format_messages(
        custom_instructions=custom_instructions,
        question="some question",
        chat_history=[],
    )
    return messages[0].content


# ---------------------------------------------------------------------------
# RAG_ANSWER_PROMPT
# ---------------------------------------------------------------------------


def test_rag_custom_instructions_appear_before_default_style():
    """
    `custom_instructions` must be positioned BEFORE the default style block
    in the rendered system prompt — LLMs weight earlier system-prompt
    content more heavily, and the old "If not None ..." at the end of the
    template caused instructions to be ignored in RAG mode.
    """
    system = _render_rag_system("Always answer in French.")

    idx_rules = system.find("Always answer in French.")
    idx_default = system.find("DEFAULT ANSWERING STYLE")

    assert idx_rules != -1, "custom_instructions not rendered into system prompt"
    assert idx_default != -1, "default style block missing from system prompt"
    assert idx_rules < idx_default, (
        "custom_instructions must appear BEFORE default style — otherwise "
        "the LLM treats defaults as primary and instructions as optional."
    )


def test_rag_custom_instructions_marked_as_highest_priority():
    """The rendered prompt must explicitly mark custom_instructions as authoritative."""
    system = _render_rag_system("Be terse.")

    assert "BEHAVIOR RULES" in system
    assert "highest priority" in system.lower()
    assert "override" in system.lower()


def test_rag_separates_form_from_facts():
    """
    The template must explicitly distinguish FORM (controlled by behavior
    rules) from FACTS (controlled by the RAG context). Without this
    separation, the Socratic-tutor case breaks: the LLM treats "answer
    from context" as overriding "never give direct answers".
    """
    system = _render_rag_system("Never give direct answers.")

    assert "FORM" in system
    assert "FACTS" in system


def test_rag_none_string_renders_cleanly():
    """
    When no custom_instructions are provided, `quivr_rag_langgraph.py`
    passes the literal string "None" (see `final_inputs["custom_instructions"]
    = prompt if prompt else "None"`). The template must render this without
    breaking, and must instruct the LLM to fall back to default style.
    """
    system = _render_rag_system("None")

    assert "Behavior rules: None" in system
    assert 'exactly the string "None"' in system
    assert "default style" in system


def test_rag_files_placeholder_still_rendered():
    """Regression guard: the files list must still be injected (we restructured,
    not removed, the knowledge-source section)."""
    system = _render_rag_system("None", files="doc_a.pdf, doc_b.pdf")
    assert "doc_a.pdf, doc_b.pdf" in system


# ---------------------------------------------------------------------------
# CHAT_LLM_PROMPT (no RAG stage)
# ---------------------------------------------------------------------------


def test_chat_llm_custom_instructions_appear_before_default_style():
    """Same ordering contract as RAG, for the non-RAG chat path."""
    system = _render_chat_llm_system("Only respond with haikus.")

    idx_rules = system.find("Only respond with haikus.")
    idx_default = system.find("DEFAULT ANSWERING STYLE")

    assert idx_rules != -1
    assert idx_default != -1
    assert idx_rules < idx_default


def test_chat_llm_custom_instructions_marked_as_highest_priority():
    system = _render_chat_llm_system("Be terse.")

    assert "BEHAVIOR RULES" in system
    assert "highest priority" in system.lower()
    assert "override" in system.lower()


def test_chat_llm_none_string_renders_cleanly():
    system = _render_chat_llm_system("None")
    assert "Behavior rules: None" in system
    assert "default style" in system
