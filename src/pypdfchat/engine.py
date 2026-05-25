import os
import re
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI 
class ChatEngine:
    def __init__(self, retriever, provider="ollama", model="qwen3.5:2b"):
        self.provider = provider
        self.model = model
        if retriever:
            self.retriever = retriever 
        else:
            raise ValueError("No retriever provided")   
        self.history = os.path.expanduser("~/.pdfchat/history.md")
        self.chat_history = self.load_memory()
        
        provider = provider.lower()
        if provider == "ollama":
            self.llm = ChatOllama(model=model, temperature=0.3)
        elif provider == "open_router":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("Missing Environment Key: Please set 'OPENROUTER_API_KEY'.")
            self.llm = ChatOpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                model=model,
                temperature=0.3,
                model_kwargs={"extra_body": {"include_reasoning": False}}
            )
        else:
            raise ValueError(f"Unknown provider '{provider}'.")   
        self.rag_chain_build()
    def rag_chain_build(self):
        search_sys_prompt = """
        Do not answer the question . 
        formulate an standalone question which can be understood without the chat history.
        Do not answer the question, reformulate it.
        """
        search_prompt = ChatPromptTemplate.from_messages([
            ("system", search_sys_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, search_prompt
        )
        system_prompt = """
        You are an expert AI assistant.
        Answer the question based on the provided context.
        If you don't know the answer clearly say that you don't.
        IMPORTANT: Do NOT output any internal thinking, reasoning steps, or <think> tags. Provide ONLY the final answer.
        """
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt + "\n\nContext: {context}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ])
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)
        self.chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        return self.chain
    def _save_memory(self):
        os.makedirs(os.path.dirname(self.history), exist_ok=True)
        with open(self.history, "w", encoding="utf-8") as f:
            for msg in self.chat_history:
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
            self.chat_history = []
    def ask(self, question: str):
        answer = ""
        for chunk in self.chain.stream({
            "input": question,
            "chat_history": self.chat_history
        }):
            if "answer" in chunk:
                text_chunk = chunk["answer"]
                answer += text_chunk
                yield text_chunk
        
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=answer))
        self._save_memory()