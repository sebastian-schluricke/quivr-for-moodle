import datetime

from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.prompts.base import BasePromptTemplate
from pydantic import ConfigDict, create_model


class CustomPromptsDict(dict):
    def __init__(self, type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._type = type

    def __setitem__(self, key, value):
        # Automatically convert the value into a tuple (my_type, value)
        super().__setitem__(key, (self._type, value))


def _define_custom_prompts() -> CustomPromptsDict:
    custom_prompts: CustomPromptsDict = CustomPromptsDict(type=BasePromptTemplate)

    today_date = datetime.datetime.now().strftime("%B %d, %Y")

    # ---------------------------------------------------------------------------
    # Prompt for question rephrasing
    # ---------------------------------------------------------------------------
    _template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language. Keep as much details as possible from previous messages. Keep entity names and all.

    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""

    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)
    custom_prompts["CONDENSE_QUESTION_PROMPT"] = CONDENSE_QUESTION_PROMPT

    # ---------------------------------------------------------------------------
    # Prompt for RAG
    # ---------------------------------------------------------------------------
    system_message_template = (
        f"Your name is Quivr. You're a helpful assistant. Today's date is {today_date}."
    )

    system_message_template += """

## BEHAVIOR RULES (highest priority)
The rules below define HOW you must answer. They override the default
answering style. Follow them strictly, even when they conflict with the
default style. This includes refusing to give direct answers when the
rules say so, changing language, adopting a persona, restricting format
or length, etc. The behavior rules are authoritative for the FORM of
your answer. If the value below is exactly the string "None", there are
no behavior rules and you should use the default style.

Behavior rules: {custom_instructions}

## DEFAULT ANSWERING STYLE (used only when no behavior rules apply)
- Use markdown for formatting.
- Use markdown code blocks for code snippets.
- For mathematical formulas, use AsciiMath notation with backticks: `x^2 + y^2 = z^2`.
- Be concise and clear.
- Answer in the same language as the user question.

## KNOWLEDGE SOURCE
Use the provided context from the user's files as the source of truth
for FACTUAL content. The behavior rules above control the FORM of your
answer (style, persona, structure, whether to answer directly); the
context controls the FACTS.

If the context does not contain the information needed and the behavior
rules do not tell you to handle missing knowledge differently, say that
you don't know rather than making something up.

Don't cite the source id in the answer, but you may use the content of
the sources to answer the question.

Available files (up to 20): {files}
"""

    template_answer = """
    Context:
    {context}

    User Question: {question}
    Answer:
    """

    RAG_ANSWER_PROMPT = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(system_message_template),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template(template_answer),
        ]
    )
    custom_prompts["RAG_ANSWER_PROMPT"] = RAG_ANSWER_PROMPT

    # ---------------------------------------------------------------------------
    # Prompt for formatting documents
    # ---------------------------------------------------------------------------
    DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(
        template="Source: {index} \n {page_content}"
    )
    custom_prompts["DEFAULT_DOCUMENT_PROMPT"] = DEFAULT_DOCUMENT_PROMPT

    # ---------------------------------------------------------------------------
    # Prompt for chatting directly with LLMs, without any document retrieval stage
    # ---------------------------------------------------------------------------
    system_message_template = (
        f"Your name is Quivr. You're a helpful assistant. Today's date is {today_date}."
    )
    system_message_template += """

## BEHAVIOR RULES (highest priority)
The rules below define HOW you must answer. They override the default
answering style and are authoritative for the FORM of your answer
(style, persona, structure, language, length, whether to answer
directly, etc.). Follow them strictly. If the value below is exactly
the string "None", there are no behavior rules and you should use the
default style.

Behavior rules: {custom_instructions}

## DEFAULT ANSWERING STYLE (used only when no behavior rules apply)
- Use markdown for formatting.
- For mathematical formulas, use AsciiMath notation with backticks: `x^2 + y^2 = z^2`.
- Answer in the same language as the user question.
- Be concise and clear.
"""

    template_answer = """
    User Question: {question}
    Answer:
    """
    CHAT_LLM_PROMPT = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(system_message_template),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template(template_answer),
        ]
    )
    custom_prompts["CHAT_LLM_PROMPT"] = CHAT_LLM_PROMPT

    return custom_prompts


_custom_prompts = _define_custom_prompts()
CustomPromptsModel = create_model(
    "CustomPromptsModel", **_custom_prompts, __config__=ConfigDict(extra="forbid")
)

custom_prompts = CustomPromptsModel()
