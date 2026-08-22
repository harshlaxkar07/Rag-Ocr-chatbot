from langchain_core.documents import Document

from config import SYSTEM_PROMPT_FILE


def load_system_prompt() -> str:
    """
    Load the system prompt from the prompt file.
    """

    if not SYSTEM_PROMPT_FILE.exists():
        raise FileNotFoundError(
            f"System prompt not found: {SYSTEM_PROMPT_FILE}"
        )

    return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()


def build_prompt(
    question: str,
    documents: list[Document],
) -> str:
    """
    Build the final prompt for the LLM.

    Args:
        question: User question.
        documents: Retrieved documents.

    Returns:
        Complete prompt string.
    """

    system_prompt = load_system_prompt()

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    prompt = f"""{system_prompt}

======================
Context
======================

{context}

======================
Question
======================

{question}

======================
Answer
======================
"""

    return prompt