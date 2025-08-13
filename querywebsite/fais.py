# pip install sentence-transformers
# pip install faiss-cpu

import pandas as pd


pd.set_option("display.max_columns", 100)


df = pd.read_csv("sample_text.csv")

# print(df.shape)

from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer("all-MiniLM-L6-v2")
vectors = encoder.encode(df.text)
print(vectors.shape)

dim = vectors.shape[1]

import faiss

index = faiss.IndexFlatL2(dim)
index.add(vectors)

search_query = "I want to buy a polo T shirt"
search_vector = encoder.encode([search_query])
D, I = index.search(search_vector, k=4)
print("Distances:", D)
print("Indices:", I)
print(df.iloc[I[0]])
