import os
import tempfile
from typing import Optional

import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader

from app.core.config import get_settings

settings = get_settings()


class OCRService:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    def is_scanned_pdf(self, pdf_path: str, sample_pages: int = 3) -> bool:
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            pages_to_check = min(total_pages, sample_pages)
            text_lengths = []
            for i in range(pages_to_check):
                text = reader.pages[i].extract_text() or ""
                text_lengths.append(len(text.strip()))
            avg_text_len = sum(text_lengths) / len(text_lengths) if text_lengths else 0
            return avg_text_len < 50
        except Exception:
            return True

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            reader = PdfReader(pdf_path)
            texts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    texts.append(text)
            extracted = "\n".join(texts).strip()
            if len(extracted) > 50:
                return extracted
        except Exception:
            pass
        return ""

    def ocr_pdf(self, pdf_path: str, dpi: int = 300) -> str:
        try:
            images = convert_from_path(pdf_path, dpi=dpi)
            texts = []
            for image in images:
                text = pytesseract.image_to_string(image)
                texts.append(text)
            return "\n".join(texts).strip()
        except Exception as e:
            return f"OCR failed: {str(e)}"

    def process_pdf(self, pdf_path: str) -> dict:
        is_scanned = self.is_scanned_pdf(pdf_path)
        if is_scanned:
            text = self.ocr_pdf(pdf_path)
            method = "ocr"
        else:
            text = self.extract_text_from_pdf(pdf_path)
            method = "text_extraction"
        return {
            "text": text,
            "method": method,
            "is_scanned": is_scanned,
            "page_count": len(PdfReader(pdf_path).pages)
        }


ocr_service = OCRService()
