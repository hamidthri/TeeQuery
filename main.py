import streamlit as st
from langchain_helper import TShirtQueryHelper
import asyncio

# Custom CSS for better UI
st.markdown("""
    <style>
    .stTextInput input {
        font-size: 18px;
        padding: 10px;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border-radius: 4px;
    }
    .query-result {
        font-size: 24px;
        padding: 20px;
        margin: 20px 0;
        border-radius: 5px;
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_query_helper():
    try:
        return TShirtQueryHelper()
    except RuntimeError as e:
        if "no current event loop" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return TShirtQueryHelper()
        raise

st.title("🎽 T-Shirt Inventory Analytics")
st.subheader("Ask natural language questions about your inventory")

query_helper = get_query_helper()

# Sample questions for quick access
sample_questions = [
    "How many Adidas T shirts I have left in my store?",
    "How many t-shirts do we have left for Nike in XS size and white color?",
    "How much sales amount will be generated if we sell all small size Adidas shirts today after discounts?"
]

question = st.selectbox(
    "Choose a sample question or type your own:",
    options=sample_questions,
    index=0
)

custom_question = st.text_input("Or enter your own question:")

if custom_question:
    question = custom_question

if st.button("Get Answer", type="primary"):
    with st.spinner("Analyzing your inventory..."):
        answer = query_helper.query_tshirt_inventory(question)
        
        if "Error" in str(answer):
            st.error(answer)
        else:
            st.markdown(f"""
            <div class="query-result">
                <h3>Result:</h3>
                <p style='font-size:36px; color:#2e86c1'>{answer}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("View query details"):
                st.write("**Your question:**", question)
                st.write("**Interpreted as:**", f"'{question}'")
                st.write("**Result value:**", answer)