"""Motor RAG local para extração inteligente de contexto"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Tuple
import hashlib
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from .pdf_extractor import PDFExtractor

class RAGEngine:
    def __init__(self, cache_dir: str = "./rag_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._create_readme()  # cria o arquivo explicativo

        print("📦 Carregando modelo de embeddings (all-MiniLM-L6-v2)...")
        print("   Isso pode levar alguns segundos na primeira execução...")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True},
            cache_folder="./model_cache"
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.pdf_extractor = PDFExtractor()
        print("✅ Modelo de embeddings carregado com sucesso!")

    def _create_readme(self):
        """Cria um arquivo LEIA_ME.txt na raiz do cache, se não existir."""
        readme_path = self.cache_dir / "LEIA_ME.txt"
        if not readme_path.exists():
            content = """ESTRUTURA DA PASTA DE CACHE

Esta pasta armazena índices criados pelo Analisador de Documentos com IA para acelerar consultas futuras.

Organização:
- Cada PDF analisado gera uma subpasta com seu nome (caracteres especiais substituídos por _ ).
- Dentro dessa subpasta, existe uma ou mais subpastas com códigos hash (ex: e91d42ea...).
- Cada hash representa uma versão específica do conteúdo do PDF. Se o arquivo for alterado, um novo hash será criado.
- Dentro da pasta do hash, você encontrará:
   - chroma_db/ : índices internos (não modifique)
   - metadata.json : informações sobre o cache (data de criação, tamanho, páginas)

Você pode excluir pastas antigas de versões anteriores manualmente se desejar liberar espaço.
O programa sempre usará o cache correspondente ao hash do conteúdo atual do PDF.
"""
            with open(readme_path, "w", encoding="utf-8-sig") as f:
                f.write(content)
            print("📄 Arquivo LEIA_ME.txt criado em rag_cache/")

    def _sanitize_filename(self, filename: str) -> str:
        """Remove caracteres inválidos para nomes de pastas no Windows."""
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = ''.join('_' if c in invalid_chars else c for c in filename)
        # Evitar nomes reservados (CON, PRN, AUX, etc.)
        reserved = {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}
        name, ext = os.path.splitext(sanitized)
        if name.upper() in reserved:
            sanitized = f"_{sanitized}"
        return sanitized

    def get_pdf_hash(self, pdf_path: str) -> str:
        with open(pdf_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def process_pdf(self, pdf_path: str, force_reprocess: bool = False) -> Chroma:
        """Processa PDF e salva cache em rag_cache/nome_sanitizado/hash/"""
        pdf_path = Path(pdf_path)
        file_hash = self.get_pdf_hash(str(pdf_path))
        sanitized_name = self._sanitize_filename(pdf_path.name)
        cache_path = self.cache_dir / sanitized_name / file_hash

        # Se force_reprocess, remove a pasta inteira (incluindo chroma_db)
        if force_reprocess and cache_path.exists():
            shutil.rmtree(cache_path)

        if cache_path.exists() and not force_reprocess:
            print(f"✅ Usando cache do PDF: {pdf_path}")
            # Exibe data de criação se disponível
            metadata_file = cache_path / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
                print(f"   Cache criado em: {meta.get('created_at', 'desconhecido')}")
            return Chroma(
                persist_directory=str(cache_path / "chroma_db"),
                embedding_function=self.embeddings
            )

        # Se não existe ou force_reprocess, criar novo
        print(f"🔄 Processando PDF: {pdf_path}")
        text, metadata = self.pdf_extractor.extract(str(pdf_path))
        if not text:
            raise ValueError("Não foi possível extrair texto do PDF")
        
        print(f"📄 Texto extraído: {len(text)} caracteres")
        chunks = self.text_splitter.split_text(text)
        print(f"✂️ Dividido em {len(chunks)} chunks")
        
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    'source': str(pdf_path),
                    'filename': metadata['filename'],
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'pages': metadata.get('pages', 0)
                }
            )
            documents.append(doc)
        
        # Cria a pasta de cache e o chroma_db dentro dela
        cache_path.mkdir(parents=True, exist_ok=True)
        persist_dir = cache_path / "chroma_db"
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(persist_dir)
        )
        
        # Salva metadados
        meta_info = {
            "filename": pdf_path.name,
            "hash": file_hash,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pdf_size_bytes": pdf_path.stat().st_size,
            "num_pages": metadata.get('pages', 0),
            "num_chunks": len(chunks)
        }
        with open(cache_path / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(meta_info, f, indent=2, ensure_ascii=False)
        
        print(f"✅ PDF processado e indexado com sucesso!")
        print(f"   Cache salvo em: {cache_path}")
        return vectorstore

    def retrieve_context(self, vectorstore: Chroma, question: str, k: int = 5) -> Tuple[str, List[dict]]:
        results = vectorstore.similarity_search_with_relevance_scores(question, k=k)
        context_parts = []
        metadata_list = []
        for doc, score in results:
            context_parts.append(doc.page_content)
            metadata_list.append({
                'score': score,
                'chunk_id': doc.metadata.get('chunk_id', 0),
                'source': doc.metadata.get('filename', 'N/A')
            })
        context = "\n\n...\n\n".join(context_parts)
        return context, metadata_list