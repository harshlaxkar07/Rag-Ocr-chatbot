from utils.loader import load_documents
from utils.splitter import split_documents
from utils.vector_store import (
    create_vector_store,
    save_vector_store,
    load_vector_store,
)

docs = load_documents()
chunks = split_documents(docs)

vector_store = create_vector_store(chunks)

save_vector_store(vector_store)

loaded_store = load_vector_store()

print("Vector store created successfully!")
print(type(loaded_store))