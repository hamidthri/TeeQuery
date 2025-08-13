import streamlit as st
from typing import Dict, Any

def setup_page_config():
    st.set_page_config(
        page_title="AI Document Query System",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .answer-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        margin: 10px 0;
    }
    .source-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
        margin: 5px 0;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)

def display_results(results: Dict[str, Any]):
    st.markdown("---")
    st.subheader("📋 Search Results")
    
    st.markdown(f"""
    <div class="answer-box">
    <h4>💡 Answer</h4>
    <p style="font-size: 16px; line-height: 1.6;">{results['answer']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if results['sources']:
        st.subheader("📚 Source Documents")
        
        for i, doc in enumerate(results['sources'], 1):
            with st.expander(f"📄 Source {i}", expanded=False):
                st.markdown(f"""
                <div class="source-box">
                <p><strong>Content:</strong></p>
                <p style="font-size: 14px; line-height: 1.5;">{doc.page_content[:500]}{'...' if len(doc.page_content) > 500 else ''}</p>
                <p><strong>Metadata:</strong> {doc.metadata}</p>
                </div>
                """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <h4>📊 Total Sources</h4>
        <p style="font-size: 24px; font-weight: bold; color: #667eea;">{len(results['sources'])}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_length = sum(len(doc.page_content) for doc in results['sources']) // len(results['sources']) if results['sources'] else 0
        st.markdown(f"""
        <div class="metric-card">
        <h4>📏 Avg. Content Length</h4>
        <p style="font-size: 24px; font-weight: bold; color: #667eea;">{avg_length}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
        <h4>📝 Answer Length</h4>
        <p style="font-size: 24px; font-weight: bold; color: #667eea;">{len(results['answer'].split())}</p>
        </div>
        """, unsafe_allow_html=True)