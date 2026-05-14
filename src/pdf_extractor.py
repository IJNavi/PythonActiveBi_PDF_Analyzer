"""Extração de texto de PDFs"""

import os
from pathlib import Path
from typing import Tuple, Dict
import pdfplumber
from PyPDF2 import PdfReader

class PDFExtractor:
    def extract(self, pdf_path: str) -> Tuple[str, Dict]:
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
        
        text = ""
        metadata = {
            'filename': pdf_path.name,
            'pages': 0,
            'size_kb': round(pdf_path.stat().st_size / 1024, 2)
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                metadata['pages'] = len(pdf.pages)
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PdfReader(file)
                    metadata['pages'] = len(reader.pages)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e2:
                raise Exception(f"Falha ao extrair texto do PDF: {e2}")
        
        import re
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip(), metadata