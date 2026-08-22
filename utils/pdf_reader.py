import fitz


def extract_pages(pdf_path: str) -> list[str]:
    """
    Extract text page by page using PyMuPDF.
    """

    document = fitz.open(pdf_path)

    pages = []

    for page in document:
        pages.append(page.get_text())

    document.close()

    return pages