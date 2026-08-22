from pathlib import Path

import fitz
from langchain_core.documents import Document

from config import DATA_DIR, SUPPORTED_EXTENSIONS
from utils.pdf_ocr import ocr_page
from utils.text_cleaner import clean_text

MIN_TEXT_LENGTH = 30


def load_documents() -> list[Document]:

    documents = []

    for pdf_path in DATA_DIR.iterdir():

        if pdf_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        pdf = fitz.open(pdf_path)

        print(f"Loading {pdf_path.name}")

        for page_number, page in enumerate(pdf):

            text = page.get_text()

            if len(text.strip()) < MIN_TEXT_LENGTH:

                print(f" OCR Page {page_number + 1}")

                text = ocr_page(page)

            text = clean_text(text)

            if not text:
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": pdf_path.name,
                        "page": page_number + 1,
                    },
                )
            )

        pdf.close()

    return documents