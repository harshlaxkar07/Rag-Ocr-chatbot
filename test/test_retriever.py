from utils.retriever import Retriever

retriever = Retriever()

results = retriever.retrieve(
    "What is machine learning?"
)

print(f"Retrieved {len(results)} documents\n")

for i, doc in enumerate(results, start=1):
    print(f"Result {i}")
    print("-" * 50)
    print(doc.metadata)
    print(doc.page_content[:300])
    print()