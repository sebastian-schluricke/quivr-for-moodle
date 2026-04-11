from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field, ConfigDict, SkipValidation
from typing_extensions import TypedDict


class cited_answer(BaseModel):
    """Respond to the user, citing any sources you used.

    The response style (direct answer, counter-question, refusal to give
    the solution, persona, length, format, language, etc.) MUST follow
    the BEHAVIOR RULES from the system prompt. When the behavior rules
    say to ask counter-questions instead of answering, put the
    counter-question into the `answer` field. When they say to refuse
    direct answers, put the refusal or redirect into the `answer` field.
    The `answer` field is the response to the user, whatever form the
    behavior rules prescribe — it is NOT always a direct factual answer.

    Factual content in the response must come from the given sources;
    style and form come from the behavior rules. If no behavior rules
    apply, default to answering the question directly from the sources.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    answer: str = Field(
        ...,
        description=(
            "The response shown to the user. Its FORM (direct answer, "
            "counter-question, refusal, persona, length, language, "
            "format) is dictated by the BEHAVIOR RULES in the system "
            "prompt; its FACTUAL content comes from the given sources. "
            "If the behavior rules tell you not to give a direct answer, "
            "put a counter-question or redirect here instead — do NOT "
            "put a direct factual answer just because the sources contain "
            "one. If no behavior rules apply, this is a direct answer to "
            "the user question based on the given sources."
        ),
    )
    citations: list[int] = Field(
        ...,
        description=(
            "The integer IDs of the specific sources that justify any "
            "factual claims in the answer. Empty list is acceptable when "
            "the answer does not contain factual claims (e.g. when "
            "behavior rules redirect to a counter-question)."
        ),
    )

    followup_questions: list[str] = Field(
        ...,
        description="Generate up to 3 follow-up questions that could be asked based on the answer given or context provided.",
    )


class ChatMessage(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    chat_id: UUID
    message_id: UUID
    brain_id: UUID | None
    msg: SkipValidation[AIMessage | HumanMessage]
    message_time: datetime
    metadata: dict[str, Any]


class KnowledgeStatus(str, Enum):
    PROCESSING = "PROCESSING"
    UPLOADED = "UPLOADED"
    ERROR = "ERROR"
    RESERVED = "RESERVED"


class Source(BaseModel):
    name: str
    source_url: str
    type: str
    original_file_name: str
    citation: str


class RawRAGChunkResponse(TypedDict):
    answer: dict[str, Any]
    docs: dict[str, Any]


class RawRAGResponse(TypedDict):
    answer: dict[str, Any]
    docs: dict[str, Any]


class ChatLLMMetadata(BaseModel):
    name: str
    display_name: str | None = None
    description: str | None = None
    image_url: str | None = None
    brain_id: str | None = None
    brain_name: str | None = None


class RAGResponseMetadata(BaseModel):
    citations: list[int] | None = None
    followup_questions: list[str] | None = None
    sources: list[Any] | None = None
    metadata_model: ChatLLMMetadata | None = None


class ParsedRAGResponse(BaseModel):
    answer: str
    metadata: RAGResponseMetadata | None = None


class ParsedRAGChunkResponse(BaseModel):
    answer: str
    metadata: RAGResponseMetadata
    last_chunk: bool = False


class QuivrKnowledge(BaseModel):
    id: UUID
    file_name: str
    brain_ids: list[UUID] | None = None
    url: Optional[str] = None
    extension: str = ".txt"
    mime_type: str = "txt"
    status: KnowledgeStatus = KnowledgeStatus.PROCESSING
    source: Optional[str] = None
    source_link: str | None = None
    file_size: int | None = None  # FIXME: Should not be optional @chloedia
    file_sha1: Optional[str] = None  # FIXME: Should not be optional @chloedia
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None


# NOTE: Updated for LangChain 1.x with pydantic v2
class SearchResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    chunk: Document
    distance: float
