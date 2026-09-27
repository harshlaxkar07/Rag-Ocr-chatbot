from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router


BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIR = BASE_DIR / "frontend"


app = FastAPI(
    title="RAG Chatbot",
    version="1.0.0",
    description=(
        "Retrieval-augmented question answering over an ingested document "
        "set, with OCR for scanned pages. The chat interface is served at /ui."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    """
    Liveness probe for the API.
    """

    return {"status": "healthy"}


if FRONTEND_DIR.is_dir():

    app.mount(
        "/ui",
        StaticFiles(directory=FRONTEND_DIR, html=True),
        name="ui",
    )

    @app.get("/", include_in_schema=False)
    def console() -> RedirectResponse:
        """
        Send the application root to the chat interface.
        """

        return RedirectResponse(url="/ui/")
