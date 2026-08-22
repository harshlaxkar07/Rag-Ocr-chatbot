from langchain_ollama import ChatOllama

from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from utils.prompt import build_prompt
from utils.retriever import Retriever


class ChatBot:
    """
    RAG chatbot powered by Ollama and FAISS.
    """

    def __init__(self) -> None:

        self.retriever = Retriever()

        self.llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0,
        )

    def ask(self, question: str) -> str:
        """
        Ask a question to the chatbot.

        Args:
            question: User input.

        Returns:
            LLM response.
        """

        documents = self.retriever.retrieve(question)

        prompt = build_prompt(
            question=question,
            documents=documents,
        )

        response = self.llm.invoke(prompt)

        return response.content