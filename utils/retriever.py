from langchain_core.documents import Document

from config import TOP_K
from utils.vector_store import load_vector_store


class Retriever:
    """
    Handles semantic retrieval from the FAISS vector store.
    """

    def __init__(self) -> None:
        self.vector_store = load_vector_store()

    def retrieve(
        self,
        query: str,
        k: int = TOP_K,
    ) -> list[Document]:
        """
        Retrieve the most relevant document chunks.

        Args:
            query: User question.
            k: Number of chunks to retrieve.

        Returns:
            List of relevant Document objects.
        """

        return self.vector_store.similarity_search(
            query=query,
            k=k,
        )