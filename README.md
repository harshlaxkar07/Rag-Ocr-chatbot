# RAG + OCR Chatbot

Ask questions about your own documents and get answers grounded in what they actually say — including pages that are scans rather than text.

PDFs are read (with OCR for pages that have no text layer), split into overlapping chunks, embedded, and indexed in **FAISS**. At question time the closest chunks are retrieved and handed to a local **Ollama** model as context. Everything runs on your machine.

Ships with **Document Chat**, a full chat interface served by the API itself.

---

## Highlights

| | |
|---|---|
| **Runs entirely locally** | Ollama for generation, sentence-transformers for embeddings, FAISS for the index |
| **OCR built in** | PaddleOCR reads scanned pages so image-only PDFs work like any other |
| **Grounded answers** | The system prompt keeps the model to the retrieved context |
| **Fast retrieval** | FAISS similarity search over 384-dimension embeddings |
| **Document Chat** | A complete chat interface at `/`, with threads kept in the browser |
| **Tested** | A test module for every stage of the pipeline |

---

## Document Chat

The API serves its own interface — start the server and open the root URL.

- **Multiple conversations**, listed in the sidebar and kept in your browser between visits
- **Markdown rendering** for bold text, bullet and numbered lists, inline code and code blocks
- **Suggested prompts** on a fresh thread to get you started
- **Copy any message**, or re-ask a question with one click
- **Download a conversation** as a Markdown file
- **Light and dark themes**, and a layout that works down to phone width

---

## How it works

### Ingestion

```
PDF in data/
   │
   ├─ 1. Load      PyMuPDF reads the text layer page by page
   ├─ 2. OCR       pages without a text layer go through PaddleOCR
   ├─ 3. Clean     whitespace and layout artefacts are normalised
   ├─ 4. Split     500-character chunks with 100 characters of overlap
   ├─ 5. Embed     all-MiniLM-L6-v2 produces a 384-dimension vector per chunk
   └─ 6. Index     vectors are written to a FAISS index in vectorstore/
```

### Answering

```
Question
   │
   ├─ 1. Embed     the question is embedded with the same model
   ├─ 2. Retrieve  FAISS returns the top 4 most similar chunks
   ├─ 3. Prompt    the chunks become context under the system prompt
   └─ 4. Generate  Ollama writes the answer from that context
```

---

## Tech stack

**API** FastAPI · Uvicorn · Pydantic
**Retrieval** FAISS · sentence-transformers · LangChain text splitters
**Generation** Ollama via langchain-ollama
**Documents** PyMuPDF · pypdf · PaddleOCR · Pillow · OpenCV
**Front end** Vanilla HTML, CSS and JavaScript — no build step

---

## Getting started

### Prerequisites

- Python 3.12 or newer
- [Ollama](https://ollama.com) installed and running

```bash
ollama pull llama3.2
```

### 1. Install

```bash
git clone https://github.com/harshlaxkar07/Rag-Ocr-chatbot.git
cd Rag-Ocr-chatbot

# with uv (recommended)
uv sync

# or with pip
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 2. Configure

Create a `.env` file in the project root:

```ini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

Both have sensible defaults, so the file is optional if you run Ollama locally with `llama3.2`.

### 3. Index your documents

Put your PDFs in `data/`, then build the index:

```bash
python ingest.py
```

### 4. Run

```bash
uvicorn app:app --reload
```

| URL | What it is |
|---|---|
| `http://localhost:8000/` | Document Chat |
| `http://localhost:8000/docs` | Interactive OpenAPI documentation |
| `http://localhost:8000/health` | Health probe |

You can also talk to it straight from the terminal:

```bash
python main.py
```

---

## API reference

### `POST /chat/`

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the document say about the retrieval step?"}'
```

```json
{ "answer": "The retrieval step embeds the question with the same model used at ingestion time, then ..." }
```

---

## Configuration

Everything tunable lives in `config.py`:

| Setting | Default | What it controls |
|---|---|---|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | The sentence-transformer used on both sides |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between neighbouring chunks |
| `TOP_K` | `4` | How many chunks are retrieved per question |
| `FAISS_INDEX_NAME` | `rag_index` | The index file name |
| `OLLAMA_MODEL` | `llama3.2` | The generation model |

The system prompt lives in `prompts/system_prompt.txt` and can be edited without touching any code.

---

## Project structure

```
Rag-Ocr-chatbot/
├── app.py                    FastAPI application, CORS and the static mount
├── main.py                   Terminal chat loop
├── ingest.py                 Builds the FAISS index from data/
├── config.py                 Paths, models and chunking settings
├── api/
│   ├── routes.py             The chat endpoint
│   └── schemas.py            Request and response models
├── utils/
│   ├── loader.py             Document loading
│   ├── pdf_reader.py         Text-layer extraction
│   ├── pdf_ocr.py            OCR for scanned pages
│   ├── text_cleaner.py       Normalisation
│   ├── splitter.py           Chunking
│   ├── embeddings.py         Embedding model wrapper
│   ├── vector_store.py       FAISS index creation and loading
│   ├── retriever.py          Similarity search
│   ├── prompt.py             Prompt assembly
│   └── chat.py               The ChatBot class
├── prompts/system_prompt.txt The grounding instructions
├── frontend/                 Document Chat
└── test/                     A test module per pipeline stage
```

---

## Running the tests

```bash
pytest test/
```
