import os
class chat_engine:
    def __init__(self,retriver,provider="ollama",model="qwen3.5:2b"):
        self.provider = provider
        self.model = model