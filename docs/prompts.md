# Quivr Prompt System Documentation

This document explains how prompts are created and used in Quivr, with a focus on how user instructions are stored in the database and how they are incorporated into the prompts sent to language models like ChatGPT.

## Table of Contents
- [Overview of Prompt System](#overview-of-prompt-system)
- [Prompt Templates](#prompt-templates)
- [User Instructions in Database](#user-instructions-in-database)
- [How User Instructions Are Incorporated](#how-user-instructions-are-incorporated)
- [Data Flow: From User Input to LLM Response](#data-flow-from-user-input-to-llm-response)
- [Potential Issues](#potential-issues)
- [Recommendations](#recommendations)

## Overview of Prompt System

Quivr uses a sophisticated prompt system to interact with language models (LLMs) like ChatGPT. The system is built around several key components:

1. **Prompt Templates**: Predefined templates that structure how questions and context are sent to the LLM
2. **User Instructions**: Custom instructions that users can store in the database
3. **RAG Pipeline**: The Retrieval-Augmented Generation pipeline that combines retrieved documents with prompts
4. **LLM Endpoint**: The interface that sends the formatted prompts to the language model

## Prompt Templates

Prompt templates are defined in `backend/core/quivr_core/prompts.py`. There are four main templates:

1. **CONDENSE_QUESTION_PROMPT**: Used to rephrase follow-up questions as standalone questions
2. **RAG_ANSWER_PROMPT**: Used for generating answers with Retrieval-Augmented Generation (RAG)
3. **DEFAULT_DOCUMENT_PROMPT**: Used for formatting documents
4. **CHAT_LLM_PROMPT**: Used for chatting directly with LLMs without document retrieval

Here's an example of the RAG_ANSWER_PROMPT:

```python
system_message_template = (
    f"Your name is Quivr. You're a helpful assistant. Today's date is {today_date}."
)

system_message_template += """
When answering use markdown.
Use markdown code blocks for code snippets.
Answer in a concise and clear manner.
Use the following pieces of context from files provided by the user to answer the users.
Answer in the same language as the user question.
If you don't know the answer with the context provided from the files, just say that you don't know, don't try to make up an answer.
Don't cite the source id in the answer objects, but you can use the source to answer the question.
You have access to the files to answer the user question (limited to first 20 files):
{files}

If not None, User instruction to follow to answer: {custom_instructions}
Don't cite the source id in the answer objects, but you can use the source to answer the question.
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
        HumanMessagePromptTemplate.from_template(template_answer),
    ]
)
```

## User Instructions in Database

User instructions are stored in the database and are associated with a brain. The `Prompt` entity is used to store these instructions.

In the `rag_service.py` file, we can see how the prompt is retrieved:

```python
def get_brain_prompt(self, brain: BrainEntity) -> Prompt | None:
    if not self.prompt_service:
        raise ValueError("PromptService not provided")

    return (
        self.prompt_service.get_prompt_by_id(brain.prompt_id)
        if brain.prompt_id
        else None
    )
```

The `brain.prompt_id` is used to retrieve the prompt from the database using the `prompt_service`.

## How User Instructions Are Incorporated

User instructions are incorporated into the prompts in several places:

1. In `rag_service.py`, when building the retrieval configuration:

```python
retrieval_config = RetrievalConfig(
    llm_config=LLMEndpointConfig(
        model=self.model_to_use,
        llm_base_url=model.endpoint_url,
        llm_api_key=api_key,
        temperature=(LLMEndpointConfig.model_fields["temperature"].default),
        max_input_tokens=model.max_input,
        max_output_tokens=model.max_output,
    ),
    prompt=self.prompt.content if self.prompt else None,
)
```

2. In `quivr_rag_langgraph.py`, when generating a RAG answer:

```python
final_inputs = {}
final_inputs["context"] = combine_documents(docs) if docs else "None"
final_inputs["question"] = user_question
final_inputs["custom_instructions"] = prompt if prompt else "None"
final_inputs["files"] = files if files else "None"
```

The user instructions are passed as `custom_instructions` to the prompt template.

3. In the prompt templates themselves:

```python
# In RAG_ANSWER_PROMPT
If not None, User instruction to follow to answer: {custom_instructions}

# In CHAT_LLM_PROMPT
If not None, also follow these user instructions when answering: {custom_instructions}
```

## Data Flow: From User Input to LLM Response

The flow of data from user input to LLM response is as follows:

1. User sends a question to a brain
2. The `RAGService` retrieves the brain's prompt from the database
3. The service builds a retrieval configuration that includes the prompt
4. The service creates a `Brain` object and calls its `ask` or `ask_streaming` method
5. The `Brain` object creates a `QuivrQARAGLangGraph` object with the retrieval configuration
6. The `QuivrQARAGLangGraph` object:
   - Rewrites the question if needed
   - Retrieves relevant documents
   - Formats the prompt with the question, documents, and user instructions
   - Sends the formatted prompt to the LLM
   - Receives and processes the response
7. The response is returned to the user

## Potential Issues

There are several potential issues with how user instructions are incorporated:

1. **Conditional Inclusion**: The user instructions are included with a conditional statement "If not None", which might lead to them being ignored if the LLM doesn't properly process this condition.

2. **Placement in Prompt**: The user instructions are placed at the end of the system message, which might reduce their importance compared to the default instructions.

3. **No Validation**: There doesn't appear to be validation to ensure that user instructions are properly formatted or don't conflict with the default instructions.

4. **Default Value**: If no prompt is found, the value "None" is used, which might be confusing for the LLM.

## Recommendations

To ensure that user instructions are properly considered:

1. **Remove Conditional Statement**: Instead of "If not None, User instruction to follow to answer: {custom_instructions}", consider using a more direct approach like "User instructions: {custom_instructions or 'No specific instructions provided.'}".

2. **Prioritize User Instructions**: Place user instructions at the beginning of the system message to emphasize their importance.

3. **Validate Instructions**: Implement validation to ensure that user instructions are properly formatted and don't conflict with the default instructions.

4. **Improve Default Value**: Use a more meaningful default value than "None" when no prompt is found.

5. **Add Logging**: Add logging to track how user instructions are being incorporated and whether they're having the expected effect.

6. **Test with Different Instructions**: Test the system with a variety of user instructions to ensure they're being properly incorporated.