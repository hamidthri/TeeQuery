from langchain_community.document_loaders.url import UnstructuredURLLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Union
import streamlit as st

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " "],
            chunk_size=500,
            chunk_overlap=100
        )
    
    def load_urls(self, urls: List[str]) -> List:
        loader = UnstructuredURLLoader(urls=urls)
        return loader.load()
    
    def load_pdfs(self, file_paths: List[str]) -> List:
        documents = []
        for path in file_paths:
            loader = PyPDFLoader(path)
            documents.extend(loader.load())
        return documents
    
    def load_csv(self, file_path: str) -> List:
        loader = CSVLoader(file_path)
        return loader.load()
    
    def split_documents(self, documents: List) -> List:
        return self.text_splitter.split_documents(documents)