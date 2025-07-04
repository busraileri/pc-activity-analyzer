from sentence_transformers import SentenceTransformer
import streamlit as st
import chromadb

@st.cache_resource
class EmbeddingStore:
    def __init__(self, collection_name="usage_data", db_path="./chroma_db"):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        try:
            return self.chroma_client.get_collection(name=self.collection_name)
        except Exception:
            return self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Computer usage data embeddings"}
            )

    def add_documents(self, documents):
        texts = [doc.page_content for doc in documents]
        embeddings = self.embedding_model.encode(texts)
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[doc.metadata for doc in documents],
            ids=[f"doc_{i}" for i in range(len(documents))]
        )

    def count(self):
        return self.collection.count()

    def query(self, query_text, n_results=3):
        query_embedding = self.embedding_model.encode(query_text).tolist()
        return self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
