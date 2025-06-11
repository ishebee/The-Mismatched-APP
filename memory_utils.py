import sys
import os
try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")  # Force updated SQLite
except ImportError:
    print("⚠️ pysqlite3-binary is missing. Install it using `pip install pysqlite3-binary`.")

import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

collection_name = "memories"
mem_path = "resources/Memories.csv"  # for sentence data
paragraph_path = "resources/Memories - Sheet1.csv"  # for paragraph context

# Load paragraph DataFrame once and normalize Date
paragraph_df = pd.read_csv(paragraph_path)
paragraph_df["Date"] = pd.to_datetime(paragraph_df["Date"], errors='coerce').dt.strftime("%m/%d/%Y")

# Load chromadb collection
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
chroma_client = chromadb.Client()

def ingest_memory_data(path=mem_path):
    if collection_name not in [c.name for c in chroma_client.list_collections()]:
        df = pd.read_csv(path)
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            embedding_function=ef
        )
        docs = df["Memory"].tolist()
        metas = [
            {
                "date": str(row["Date"]),
                "event": row["Event"],
                "tag": row["Tag"]
            }
            for _, row in df.iterrows()
        ]
        ids = [f"id_{i}" for i in range(len(df))]
        collection.add(documents=docs, metadatas=metas, ids=ids)

def get_relevant_qa(query, n_results=10):
    collection = chroma_client.get_collection(name=collection_name, embedding_function=ef)
    return collection.query(query_texts=[query], n_results=n_results)

def get_context_from_df(date=None, metas=None):
    if date:
        df = paragraph_df[paragraph_df["Date"] == date]
    elif metas:
        events = list({m['event'] for m in metas})
        df = paragraph_df[paragraph_df["Event"].isin(events)]
    else:
        return ""

    context = ""
    for _, row in df.iterrows():
        context += f" Date: {row['Date']}\n📝 Memory: {row['Memory']}\n📌 Event: {row['Event']}\n🏷️ Tag: {row['Tag']}\n\n"
    return context
