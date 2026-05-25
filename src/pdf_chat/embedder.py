import os
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
store_path = os.path.expanduser("~/.pdfchat/")
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings

class embedder:
    def get_embedder(self,provider="ollama", model_name="qwen3-embedding:0.6b"):
        if provider == "ollama":
            return OllamaEmbeddings(model=model_name)
        if provider == "open_router":
            api_key = os.getenv("OPENROUTER_API_KEY")
            return OpenAIEmbeddings(
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                model=model_name
            )
        raise ValueError("Invalid provider")
class data_base: 
    def create_and_save()