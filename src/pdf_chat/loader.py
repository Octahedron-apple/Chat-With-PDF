import os
from pypdf import PdfReader
from langchain_core.documents import Document
class pdfloader :
    def __init__(self,file_path = None, chunk_size = 1000, chunk_overlap = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text = ""
        self.chunks = []
        self.file_path = file_path
    def load_pdf(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")      
        text = ""
        reader = PdfReader(self.file_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"    
        self.text=  text
        return text
    def chunk_maker(self):
        temp = str(self.text)
        if len(temp) <= self.chunk_size:
            self.chunks = [temp]
            return [temp] 
        chunks = []
        start = 0
        while start < len(temp):
            end = start + self.chunk_size
            chunks.append(temp[start:end])
            if end >= len(temp):
                break
            start += self.chunk_size - self.chunk_overlap
        self.chunks = chunks
        return chunks
    def docs_maker(self):
        docs = []
        for chunk in self.chunks:
            docs.append(Document(page_content=chunk, metadata={"source": self.file_path}))
        self.docs = docs
        return docs
    