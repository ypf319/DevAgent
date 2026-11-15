import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

class VectorStore:
    def __init__(self, persist_dir:str = "./data/vector_db", collection_name:str="code_knowledge"):

        os.makedirs(persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path = persist_dir)

        self.embedding = SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-small-zh-v1.5"
        )

        self.collection = self.client.get_or_create_collection(
            name = collection_name,
            embedding_function = self.embedding,
            metadata={"description":"代码仓库知识库"}
        )

    def add_document(self,chunks:list[dict[str, str]]):

        ids = []
        documents = []
        metadatas = []
        for chunk in chunks:
            chunk_id = f"{chunk["file_path"]}#chunk_{chunk['chunk_index']}"
            ids.append(chunk_id)
            documents.append(chunk["content"])
            metadatas.append(
                {
                    "file_path": chunk["file_path"],
                    "chunk_index": chunk["chunk_index"],
                }
            )

        self.collection.upsert(
            ids = ids,
            documents = documents,
            metadatas = metadatas,
        )

        print(f"[向量库] 已存入 {len(ids)} 个文本块")

    def search(self,query:str, top_k:int=10):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        output = []
        for i in range(len(results["documents"][0])):
            output.append({
                "file_path": results["metadatas"][0][i]["file_path"],
                "content": results["documents"][0][i],
                "distance": results["distances"][0][i],
            })
        return output

vector_store = VectorStore()




