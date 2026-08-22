from utils.loader import load_documents
from utils.splitter import split_documents

docs = load_documents()
chunks = split_documents(docs)

print(f"Original pages : {len(docs)}")
print(f"Total chunks   : {len(chunks)}")

print("\nFirst Chunk:\n")
print(chunks[0].page_content)
print("\nMetadata:")
print(chunks[0].metadata)