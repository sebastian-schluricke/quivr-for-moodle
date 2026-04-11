"""
Tests for per-request custom_instructions handling in RAGService.

These tests verify the single-source-of-truth prompt resolution in
`RAGService._get_retrieval_config()`, which governs how custom_instructions
(coming from the Moodle activity per-request) interact with brain-level
prompts and externally-provided retrieval configs.

Priority contract (see `_get_retrieval_config`):
    1. custom_instructions (per-request) — highest
    2. brain prompt (linked via brain.prompt_id) — fallback
    3. existing retrieval_config.prompt (if nothing above) — lowest
"""

from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from quivr_core.config import LLMEndpointConfig, RetrievalConfig

from quivr_api.modules.prompt.entity.prompt import Prompt
from quivr_api.modules.rag_service.rag_service import RAGService


def _make_rag_service(
    *,
    custom_instructions: str | None = None,
    brain_prompt: Prompt | None = None,
    external_retrieval_config: RetrievalConfig | None = None,
) -> RAGService:
    """
    Build a RAGService bypassing __init__ so no real services/DB are needed.

    We only exercise `_get_retrieval_config`, which touches:
      - self.retrieval_config (external override)
      - self.prompt (brain-level prompt)
      - self.custom_instructions (per-request)
      - self._build_retrieval_config() (only when no external config)
    """
    service = RAGService.__new__(RAGService)
    service.retrieval_config = external_retrieval_config
    service.prompt = brain_prompt
    service.custom_instructions = custom_instructions
    return service


def _make_retrieval_config(prompt: str | None = None) -> RetrievalConfig:
    return RetrievalConfig(llm_config=LLMEndpointConfig(), prompt=prompt)


def _make_brain_prompt(content: str) -> Prompt:
    return Prompt(id=uuid4(), title="brain_prompt", content=content, status="private")


# ---------------------------------------------------------------------------
# Tests with an externally-provided retrieval_config (Moodle/per-request path)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_custom_instructions_override_brain_prompt():
    """Per-request custom_instructions must win over brain-level prompt."""
    service = _make_rag_service(
        custom_instructions="Act as a strict math tutor.",
        brain_prompt=_make_brain_prompt("You are a generic helpful assistant."),
        external_retrieval_config=_make_retrieval_config(),
    )

    config = await service._get_retrieval_config()

    assert config.prompt == "Act as a strict math tutor."


@pytest.mark.asyncio
async def test_custom_instructions_override_existing_config_prompt():
    """
    Even if the external retrieval_config already has a prompt set,
    per-request custom_instructions must override it.
    """
    service = _make_rag_service(
        custom_instructions="Quiz mode: ask one question at a time.",
        brain_prompt=None,
        external_retrieval_config=_make_retrieval_config(
            prompt="Previous prompt that should be overridden"
        ),
    )

    config = await service._get_retrieval_config()

    assert config.prompt == "Quiz mode: ask one question at a time."


@pytest.mark.asyncio
async def test_brain_prompt_used_when_no_custom_instructions():
    """Without custom_instructions, fall back to brain-level prompt."""
    service = _make_rag_service(
        custom_instructions=None,
        brain_prompt=_make_brain_prompt("You are a generic helpful assistant."),
        external_retrieval_config=_make_retrieval_config(),
    )

    config = await service._get_retrieval_config()

    assert config.prompt == "You are a generic helpful assistant."


@pytest.mark.asyncio
async def test_brain_prompt_overrides_existing_config_prompt():
    """
    If no custom_instructions, brain prompt is authoritative and overrides
    any prompt that was already sitting in the external retrieval_config.
    """
    service = _make_rag_service(
        custom_instructions=None,
        brain_prompt=_make_brain_prompt("Brain prompt wins."),
        external_retrieval_config=_make_retrieval_config(
            prompt="Stale prompt from elsewhere"
        ),
    )

    config = await service._get_retrieval_config()

    assert config.prompt == "Brain prompt wins."


@pytest.mark.asyncio
async def test_existing_config_prompt_kept_when_nothing_else_set():
    """
    When neither custom_instructions nor a brain prompt is available,
    the existing retrieval_config.prompt must be preserved as-is.
    """
    service = _make_rag_service(
        custom_instructions=None,
        brain_prompt=None,
        external_retrieval_config=_make_retrieval_config(
            prompt="Keep me — I'm the only prompt around."
        ),
    )

    config = await service._get_retrieval_config()

    assert config.prompt == "Keep me — I'm the only prompt around."


@pytest.mark.asyncio
async def test_no_prompt_at_all_remains_none():
    """With nothing configured anywhere, prompt stays None."""
    service = _make_rag_service(
        custom_instructions=None,
        brain_prompt=None,
        external_retrieval_config=_make_retrieval_config(),
    )

    config = await service._get_retrieval_config()

    assert config.prompt is None


@pytest.mark.asyncio
async def test_empty_string_custom_instructions_is_ignored():
    """
    An empty custom_instructions string must not shadow the brain prompt.
    The Moodle form can submit an empty textarea — that should mean
    "fall back to brain prompt", not "use empty instructions".
    """
    service = _make_rag_service(
        custom_instructions="",
        brain_prompt=_make_brain_prompt("Brain prompt should still apply."),
        external_retrieval_config=_make_retrieval_config(),
    )

    config = await service._get_retrieval_config()

    assert config.prompt == "Brain prompt should still apply."


# ---------------------------------------------------------------------------
# Test the path where retrieval_config is built internally
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_custom_instructions_applied_when_config_built_internally():
    """
    When no external retrieval_config is passed, _build_retrieval_config()
    is called. The prompt resolution must still happen afterwards — so the
    built config ends up with custom_instructions as its prompt.
    """
    service = _make_rag_service(
        custom_instructions="Role: Socratic tutor. Never give direct answers.",
        brain_prompt=_make_brain_prompt("generic brain prompt"),
        external_retrieval_config=None,
    )

    # Stub _build_retrieval_config so we don't need ModelService / DB.
    built_config = _make_retrieval_config(prompt=None)

    async def _fake_build() -> RetrievalConfig:
        return built_config

    service._build_retrieval_config = _fake_build  # type: ignore[method-assign]

    config = await service._get_retrieval_config()

    assert config is built_config
    assert config.prompt == "Role: Socratic tutor. Never give direct answers."


@pytest.mark.asyncio
async def test_build_retrieval_config_does_not_set_prompt():
    """
    Regression guard: the build step should stay prompt-agnostic.
    Prompt resolution lives in _get_retrieval_config — not here — so that
    there is exactly one place that decides which prompt wins.
    """
    from quivr_api.modules.models.entity.model import Model

    service = RAGService.__new__(RAGService)
    service.model_to_use = "gpt-4o"
    service.model_service = MagicMock()
    service.model_service.get_model = MagicMock(
        return_value=_async_return(
            Model(
                name="gpt-4o",
                price=1,
                max_input=1000,
                max_output=1000,
                description="test",
                image_url="",
                display_name="gpt-4o",
                endpoint_url="https://api.openai.com/v1",
                env_variable_name="OPENAI_API_KEY",
                default=True,
            )
        )
    )

    config = await service._build_retrieval_config()

    assert config.prompt is None


def _async_return(value):
    """Helper: return an awaitable that resolves to `value`."""

    async def _inner():
        return value

    return _inner()
