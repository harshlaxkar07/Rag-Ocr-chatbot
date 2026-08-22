from utils.retriever import Retriever
from utils.prompt import build_prompt

retriever = Retriever()

docs = retriever.retrieve(
    "What is Python?"
)

prompt = build_prompt(
    question="What is Python?",
    documents=docs,
)

print(prompt)