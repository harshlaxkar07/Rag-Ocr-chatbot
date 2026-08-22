import fitz
import numpy as np
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
)


def ocr_page(page) -> str:
    """
    OCR a single PyMuPDF page.
    """

    pix = page.get_pixmap(dpi=300)

    image = np.array(pix.pil_image())

    result = ocr.predict(image)

    lines = []

    if result:

        for block in result:

            lines.extend(block.get("rec_texts", []))

    return "\n".join(lines)