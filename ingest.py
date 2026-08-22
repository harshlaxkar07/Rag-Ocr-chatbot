from utils.loader import load_documents
from utils.splitter import split_documents
from utils.vector_store import (
    create_vector_store,
    save_vector_store,
)


def ingest() -> None:
    """
    Run the document ingestion pipeline.
    """

    print("=" * 60)
    print("Starting document ingestion...")
    print("=" * 60)

    # Step 1: Load documents
    documents = load_documents()
    print(f"Loaded {len(documents)} document pages.")

    # Step 2: Split documents
    chunks = split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    # Step 3: Build FAISS index
    vector_store = create_vector_store(chunks)
    print("Vector store created.")

    # Step 4: Save index
    save_vector_store(vector_store)
    print("Vector store saved successfully.")

    print("=" * 60)
    print("Ingestion completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    ingest()