from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field, ConfigDict, SkipValidation
from typing_extensions import TypedDict


class cited_answer(BaseModel):
    """Answer the user question based only on the given sources, and cite the sources used."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    answer: str = Field(
        ...,
        description="The answer to the user question, which is based only on the given sources.",
    )
    citations: list[int] = Field(
        ...,
        description="The integer IDs of the SPECIFIC sources which justify the answer.",
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
