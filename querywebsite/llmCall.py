from langchain_community.document_loaders.url import UnstructuredURLLoader
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

load_dotenv()

# 1. Load data
urls = ["https://otaheri.github.io/"]
loader = UnstructuredURLLoader(urls=urls)
data = loader.load()

# 2. Split into chunks
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", " "],
    chunk_size=500,
    chunk_overlap=100
)
chunks = text_splitter.split_documents(data)

# 3. Create embeddings & LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# 4. Build FAISS index
vector_index = FAISS.from_documents(chunks, embeddings)

# 5. Save FAISS index locally
vector_index.save_local("vector_index_dir")

# 6. Load FAISS index again
vector_index = FAISS.load_local(
    "vector_index_dir",
    embeddings,
    allow_dangerous_deserialization=True
)

# 7. Create RetrievalQA chain
chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_index.as_retriever(),
    return_source_documents=True
)

# 8. Query the chain
query = "What is the person expertise?"
import langchain
langchain.debug = True

result = chain.invoke({"query": query})

print("Answer:", result["result"])
print("Sources:", [doc.metadata for doc in result["source_documents"]])
