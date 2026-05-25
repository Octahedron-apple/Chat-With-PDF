import os
import re
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI 
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
class chat_engine:
    def __init__(self,retriver,provider="ollama",model="qwen3.5:2b"):
        self.provider = provider
        self.model = model
        if retriver:
            self.retriver = retriver 
        else:
            raise ValueError("No retriver provided")
        self.history = os.path.expanduser("~/.pdfchat/history.md")
        provider = provider.lower()
        if provider == "ollama":
            self.llm = ChatOllama(model=model_name, temperature=0.3)
        elif provider == "open_router":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("Missing Environment Key: Please set 'OPENROUTER_API_KEY'.")
            self.llm = ChatOpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                model=model_name,
                temperature=0.3
            )
        else:
            raise ValueError(f"Unknown provider '{provider}'.")
    def rag_chain_build(self):
        search_sys_prompt = """
        Do not answer the question . 
        formulate an standalone question which can be understood without the chat history.
        Do not answer the question, reformulate it.
        """
        search_prompt = ChatPromptTemplate.from_messages([("system",search_sys_prompt),MessagesPlaceholder("chat_history"),("human","{input}")])
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriver, search_prompt
        )
        system_prompt="""
        You are an expert AI assistant.
        Answer the question based on the provided context.
        If you don't know the answer clearly say that you don't    
        """
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt + "\n\nContext: {context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        self.rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        return self.rag_chain
    def save_memory(self, chat_history):
        os.makedirs(os.path.dirname(self.history), exist_ok=True)
        with open(self.history, "w", encoding="utf-8") as f:
            for msg in chat_history:
                if isinstance(msg, HumanMessage):
                    f.write(f"**Human:** {msg.content}\n\n")
                elif isinstance(msg, AIMessage):
                    f.write(f"**AI:** {msg.content}\n\n")

    def load_memory(self):
        chat_history = []
        if not os.path.exists(self.history):
            return chat_history
            
        with open(self.history, "r", encoding="utf-8") as f:
            content = f.read()
            
        parts = re.split(r'\*\*(Human|AI):\*\*\s*', content)
        for i in range(1, len(parts), 2):
            role = parts[i]
            text = parts[i+1].strip()
            if role == "Human":
                chat_history.append(HumanMessage(content=text))
            elif role == "AI":
                chat_history.append(AIMessage(content=text))
                
        return chat_history

    def clear_memory(self):
        if os.path.exists(self.history):
            os.remove(self.history)
