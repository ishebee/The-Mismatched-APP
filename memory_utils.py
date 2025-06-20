import sys
import os
try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    print("⚠️ pysqlite3-binary is missing. Install it using `pip install pysqlite3-binary`.")

import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

collection_name = "memories"
paragraph_path = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTcqUwnUPUyaXN4ZbrlUP9oRmz85k02nEH0PuS7D5sfjX5N6aPxCFYrxyWswhcNaZxmU9bJhKJUHv6u/pub?gid=0&single=true&output=csv"

def load_paragraph_df():
    df = pd.read_csv(paragraph_path)
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce').dt.strftime("%m/%d/%Y")
    return df

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
chroma_client = chromadb.Client()

def ingest_memory_data():
    if collection_name not in [c.name for c in chroma_client.list_collections()]:
        df = create_sentence_df_from_paragraph()
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
    df = load_paragraph_df()
    if date:
        df = df[df["Date"] == date]
    elif metas:
        events = list({m['event'] for m in metas})
        df = df[df["Event"].isin(events)]
    else:
        return ""

    context = ""
    for _, row in df.iterrows():
        context += f" Date: {row['Date']}\n📝 Memory: {row['Memory']}\n📌 Event: {row['Event']}\n🏷️ Tag: {row['Tag']}\n\n"
    return context

def create_sentence_df_from_paragraph(paragraph_path=paragraph_path):
    df = load_paragraph_df()
    df.dropna(subset=["Memory"], inplace=True)

    sentence_rows = []
    for _, row in df.iterrows():
        sentences = [s.strip() for s in row["Memory"].split('.') if s.strip()]
        for sentence in sentences:
            sentence_rows.append({
                "Memory": sentence,
                "Date": row["Date"],
                "Event": row["Event"],
                "Tag": row["Tag"]
            })

    return pd.DataFrame(sentence_rows)
