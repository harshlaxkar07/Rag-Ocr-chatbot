from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = BASE_DIR / "vectorstore"
PROMPTS_DIR = BASE_DIR / "prompts"
LOGS_DIR = BASE_DIR / "logs"

# ==========================================================
# Embedding Model
# ==========================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ==========================================================
# Ollama Configuration
# ==========================================================

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# ==========================================================
# Text Splitting
# ==========================================================

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# ==========================================================
# Retriever
# ==========================================================

TOP_K = 4

# ==========================================================
# Supported Files
# ==========================================================

SUPPORTED_EXTENSIONS = [".pdf"]

# ==========================================================
# FAISS
# ==========================================================

FAISS_INDEX_NAME = "rag_index"

# ==========================================================
# Prompt
# ==========================================================

SYSTEM_PROMPT_FILE = PROMPTS_DIR / "system_prompt.txt"