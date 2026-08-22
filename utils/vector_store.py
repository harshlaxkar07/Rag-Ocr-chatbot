from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from config import FAISS_INDEX_NAME, VECTOR_STORE_DIR
from utils.embeddings import get_embedding_model


def create_vector_store(documents: list[Document]) -> FAISS:
    """
    Create a FAISS vector store from documents.

    Args:
        documents: Chunked documents.

    Returns:
        FAISS vector store.
    """

    embedding_model = get_embedding_model()

    vector_store = FAISS.from_documents(
        documents=documents,
        embedding=embedding_model,
    )

    return vector_store


def save_vector_store(vector_store: FAISS) -> None:
    """
    Save the FAISS vector store to disk.
    """

    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    vector_store.save_local(
        folder_path=str(VECTOR_STORE_DIR),
        index_name=FAISS_INDEX_NAME,
    )


def load_vector_store() -> FAISS:
    """
    Load the FAISS vector store from disk.

    Returns:
        Loaded FAISS vector store.
    """

    index_file = VECTOR_STORE_DIR / f"{FAISS_INDEX_NAME}.faiss"

    if not index_file.exists():
        raise FileNotFoundError(
            "Vector store not found. Run ingest.py first."
        )

    embedding_model = get_embedding_model()

    return FAISS.load_local(
        folder_path=str(VECTOR_STORE_DIR),
        embeddings=embedding_model,
        index_name=FAISS_INDEX_NAME,
        allow_dangerous_deserialization=True,
    )