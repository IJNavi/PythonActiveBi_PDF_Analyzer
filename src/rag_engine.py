"""Motor RAG local para extração inteligente de contexto"""

import os
import shutil
from pathlib import Path
from typing import List, Tuple
import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from .pdf_extractor import PDFExtractor

class RAGEngine:
    def __init__(self, cache_dir: str = "./rag_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
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
    
    def get_pdf_hash(self, pdf_path: str) -> str:
        with open(pdf_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def process_pdf(self, pdf_path: str, force_reprocess: bool = False) -> Chroma:
        pdf_hash = self.get_pdf_hash(pdf_path)
        persist_dir = self.cache_dir / pdf_hash
        
        if force_reprocess and persist_dir.exists():
            shutil.rmtree(persist_dir)
        
        if persist_dir.exists() and not force_reprocess:
            print(f"✅ Usando cache do PDF: {pdf_path}")
            return Chroma(
                persist_directory=str(persist_dir),
                embedding_function=self.embeddings
            )
        
        print(f"🔄 Processando PDF: {pdf_path}")
        text, metadata = self.pdf_extractor.extract(pdf_path)
        
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
                    'source': pdf_path,
                    'filename': metadata['filename'],
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'pages': metadata.get('pages', 0)
                }
            )
            documents.append(doc)
        
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(persist_dir)
        )
        
        print(f"✅ PDF processado e indexado com sucesso!")
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