from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split documents into smaller chunks for embedding.

    Args:
        documents: List of LangChain Document objects.

    Returns:
        List of chunked Document objects.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
    )

    chunks = splitter.split_documents(documents)

    return chunks