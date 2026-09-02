from __future__ import annotations
import json, shutil
from pathlib import Path
from .matrix_parser import parse_matrix
from ..config import settings

class MatrixIndexer:
    def build(self, matrix_path: Path, target_dir: Path):
        parsed = parse_matrix(matrix_path)
        if target_dir.exists(): shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        try:
            import chromadb
            from llama_index.core import Document, StorageContext, VectorStoreIndex, Settings
            from llama_index.vector_stores.chroma import ChromaVectorStore
            from llama_index.embeddings.ollama import OllamaEmbedding
            Settings.embed_model = OllamaEmbedding(model_name=settings.ollama_embed_model, base_url=settings.ollama_base_url, request_timeout=90)
            client = chromadb.PersistentClient(path=str(target_dir / "chroma"))
            collection = client.get_or_create_collection("qa_matrix")
            store = ChromaVectorStore(chroma_collection=collection)
            storage = StorageContext.from_defaults(vector_store=store)
            docs=[]
            for r in parsed["records"]:
                text = r["raw_text"]
                docs.append(Document(text=text, metadata={k:r[k] for k in ["id","workbook","sheet","category","subcategory","source_row_start","source_row_end","cell_range","score","critical"]}))
            VectorStoreIndex.from_documents(docs, storage_context=storage, show_progress=False)
            (target_dir/"manifest.json").write_text(json.dumps({"ready":True,"record_count":len(docs),"embed_model":settings.ollama_embed_model},indent=2),encoding="utf-8")
            return parsed
        except Exception:
            shutil.rmtree(target_dir, ignore_errors=True)
            raise

    def semantic_search(self, query: str, limit: int=6) -> list[dict]:
        active = settings.index_dir / "active"
        manifest = active / "manifest.json"
        if not manifest.exists(): return []
        try:
            import chromadb
            from llama_index.core import VectorStoreIndex, Settings
            from llama_index.vector_stores.chroma import ChromaVectorStore
            from llama_index.embeddings.ollama import OllamaEmbedding
            Settings.embed_model = OllamaEmbedding(model_name=settings.ollama_embed_model, base_url=settings.ollama_base_url, request_timeout=90)
            client=chromadb.PersistentClient(path=str(active/"chroma")); collection=client.get_collection("qa_matrix")
            index=VectorStoreIndex.from_vector_store(ChromaVectorStore(chroma_collection=collection))
            nodes=index.as_retriever(similarity_top_k=limit).retrieve(query)
            return [{"text":n.node.get_content(),"metadata":n.node.metadata,"semantic_score":float(n.score or 0)} for n in nodes]
        except Exception:
            return []

indexer = MatrixIndexer()
