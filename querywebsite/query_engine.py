from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from typing import List, Dict, Any
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

class QueryEngine:
    def __init__(self, chunks: List):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("Please set GOOGLE_API_KEY in your .env file")
            st.stop()
        
        os.environ["GOOGLE_API_KEY"] = api_key
        
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
        self.vector_index = FAISS.from_documents(chunks, self.embeddings)
        self.retriever = self.vector_index.as_retriever(search_kwargs={"k": 4})
    
    def query(self, question: str) -> Dict[str, Any]:
        try:
            docs = self.retriever.get_relevant_documents(question)
            context = "\n\n".join([doc.page_content for doc in docs[:3]])
            
            prompt = f"""
            Based on the following context, answer the question:
            
            Context:
            {context}
            
            Question: {question}
            
            Answer:
            """
            
            response = self.llm.invoke(prompt)
            
            return {
                "answer": response.content,
                "sources": docs
            }
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return {
                "answer": "Sorry, an error occurred while processing your query.",
                "sources": []
            }