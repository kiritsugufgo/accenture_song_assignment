import os
import chromadb
from chromadb.utils import embedding_functions

class ChromaIngestor:
    def __init__(self, db_path="./data/chroma_db"):
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=db_path)
        # Using a default open-source embedding function 
        self.emb_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="policy_docs", 
            embedding_function=self.emb_fn
        )

    def ingest_directory(self, docs_path):
        #Line-by-line chunking 
        documents = []
        metadatas = []
        ids = []
        
        chunk_idx = 0
        for filename in os.listdir(docs_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(docs_path, filename)
                with open(file_path, "r") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip()]
                    
                for line in lines:
                    documents.append(line)
                    metadatas.append({"source": filename})
                    ids.append(f"id_{chunk_idx}")
                    chunk_idx += 1
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Ingested {len(documents)} policy chunks into ChromaDB.")

# Quick execution
if __name__ == "__main__":
    ingestor = ChromaIngestor()
    ingestor.ingest_directory("data/raw/documents")