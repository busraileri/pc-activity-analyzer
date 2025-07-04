from sentence_transformers import SentenceTransformer
import chromadb

class VectorStoreManager:
    def __init__(self, collection_name="usage_data", persist_path="./chroma_db"):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(path=persist_path)
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        try:
            collection = self.chroma_client.get_collection(name=self.collection_name)
            print("✅ Existing collection found.")
            return collection
        except Exception:
            collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Computer usage data embeddings"}
            )
            print("✅ New collection created.")
            return collection

    def add_documents(self, documents):
        texts = [doc.page_content for doc in documents]
        embeddings = self.embedding_model.encode(texts)
        ids = [f"doc_{i}" for i in range(len(documents))]

        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[doc.metadata for doc in documents],
            ids=ids
        )
        print(f"✅ {len(documents)} records added to vector store.")

    def get_collection_count(self):
        return self.collection.count()

    def query(self, query_text, n_results=3):
        query_embedding = self.embedding_model.encode(query_text).tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        return results

    def query_relevant_docs(self, query_text, n_results=3):
        results = self.query(query_text, n_results)
        # 'documents' key exists and is not empty, return the first result, otherwise return an empty list
        if 'documents' in results and results['documents'] and results['documents'][0]:
            docs = results['documents'][0]
        # Basic cleaning and natural language format conversion
            cleaned_docs = []
            for doc in docs:
                text = doc.strip().replace('\n', ' ')  # remove unnecessary new lines
                cleaned_docs.append(text)
            return "\n".join(cleaned_docs)
        return "No relevant data found."
