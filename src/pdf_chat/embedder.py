import os
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
store_path = os.path.expanduser("~/.pdfchat/")
class Embedder:
    def get_embedder(self,provider="ollama", model_name="qwen3-embedding:0.6b"):
        if provider == "ollama":
            return OllamaEmbeddings(model=model_name)    
        if provider == "open_router":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("Missing Environment Key: Please set 'OPENROUTER_API_KEY'.") 
            return OpenAIEmbeddings(
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                model=model_name
            )
        raise ValueError(f"Invalid provider: {provider}")

class Database: 
    def create_and_save(self,documents: list[Document], embedder: Embeddings):
        if not documents: 
            raise ValueError("No documents provided")        
        os.makedirs(store_path, exist_ok=True)
        db = FAISS.from_documents(documents, embedder)
        db.save_local(store_path)
        return db
    def load_db(self,embedder: Embeddings):
        return FAISS.load_local(store_path, embedder, allow_dangerous_deserialization=True)