import streamlit as st
import os
import tempfile
from pathlib import Path
from document_processor import DocumentProcessor
from query_engine import QueryEngine
from utils import setup_page_config, display_results


import asyncio
import nest_asyncio

nest_asyncio.apply()

try:
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        asyncio.set_event_loop(asyncio.new_event_loop())
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
    
def main():
    setup_page_config()
    
    st.title("🔍 Hamid AI")
    st.markdown("---")
    
    if "query_engine" not in st.session_state:
        st.session_state.query_engine = None
    
    with st.sidebar:
        st.header("📚 Data Sources")
        
        source_type = st.radio(
            "Choose Source Type:",
            ["URLs", "PDF Files", "CSV Files"],
            index=0
        )
        
        processor = DocumentProcessor()
        
        if source_type == "URLs":
            st.subheader("🌐 Website URLs")
            urls_input = st.text_area(
                "Enter URLs (one per line):",
                height=100,
                placeholder="https://example.com\nhttps://another-site.com"
            )
            
            if st.button("Process URLs", type="primary"):
                if urls_input.strip():
                    urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
                    with st.spinner("Loading and processing URLs..."):
                        try:
                            documents = processor.load_urls(urls)
                            chunks = processor.split_documents(documents)
                            st.session_state.query_engine = QueryEngine(chunks)
                            st.success(f"✅ Processed {len(chunks)} chunks from {len(urls)} URLs")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Please enter at least one URL")
        
        elif source_type == "PDF Files":
            st.subheader("📄 PDF Documents")
            uploaded_files = st.file_uploader(
                "Upload PDF files:",
                type=['pdf'],
                accept_multiple_files=True
            )
            
            if uploaded_files and st.button("Process PDFs", type="primary"):
                with st.spinner("Processing PDF files..."):
                    try:
                        temp_paths = []
                        for file in uploaded_files:
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                                tmp.write(file.read())
                                temp_paths.append(tmp.name)
                        
                        documents = processor.load_pdfs(temp_paths)
                        chunks = processor.split_documents(documents)
                        st.session_state.query_engine = QueryEngine(chunks)
                        st.success(f"✅ Processed {len(chunks)} chunks from {len(uploaded_files)} PDFs")
                        
                        for path in temp_paths:
                            os.unlink(path)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        elif source_type == "CSV Files":
            st.subheader("📊 CSV Documents")
            uploaded_file = st.file_uploader("Upload CSV file:", type=['csv'])
            
            if uploaded_file and st.button("Process CSV", type="primary"):
                with st.spinner("Processing CSV file..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
                            tmp.write(uploaded_file.read())
                            temp_path = tmp.name
                        
                        documents = processor.load_csv(temp_path)
                        chunks = processor.split_documents(documents)
                        st.session_state.query_engine = QueryEngine(chunks)
                        st.success(f"✅ Processed {len(chunks)} chunks from CSV")
                        
                        os.unlink(temp_path)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Ask Your Question")
        query = st.text_input(
            "Enter your question:",
            placeholder="What information are you looking for?",
            key="query_input"
        )
        
        col_search, col_clear = st.columns([1, 1])
        with col_search:
            search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
        with col_clear:
            if st.button("🗑️ Clear Results", use_container_width=True):
                if "results" in st.session_state:
                    del st.session_state.results
    
    with col2:
        if st.session_state.query_engine:
            st.success("✅ Ready to search!")
            st.info(f"📊 {len(st.session_state.query_engine.retriever.vectorstore.docstore._dict)} documents loaded")
        else:
            st.warning("⚠️ Please process some documents first")
    
    if search_clicked and query and st.session_state.query_engine:
        with st.spinner("Searching for answers..."):
            try:
                result = st.session_state.query_engine.query(query)
                st.session_state.results = result
            except Exception as e:
                st.error(f"❌ Search Error: {str(e)}")
    
    if "results" in st.session_state:
        display_results(st.session_state.results)

if __name__ == "__main__":
    main()