from utils.loader import load_documents

docs = load_documents()

print(f"Documents: {len(docs)}")

for i, doc in enumerate(docs[:3]):
    print(f"\nDocument {i}")
    print("Metadata:", doc.metadata)
    print("Length:", len(doc.page_content))
    print("Preview:")
    print(repr(doc.page_content[:300]))