from utils.embeddings import get_embedding_model

model = get_embedding_model()

vector = model.embed_query("What is Python?")

print(f"Dimensions: {len(vector)}")
print(vector[:10])