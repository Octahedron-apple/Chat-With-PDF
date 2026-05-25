import os
from pypdf import PdfReader
class pdfloader :
    def __init__(self, chunk_size = 1000, chunk_overlap = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text = ""
        self.chunks = []
    def load_pdf(self,file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")      
        text = ""
        reader = PdfReader(file_path)
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