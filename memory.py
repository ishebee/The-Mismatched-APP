import pandas as pd
import streamlit as st
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"



groq_client = Groq()
mem_path = "resources/Memories.csv"
chroma_client = chromadb.Client()
collection_name = "memories"

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='sentence-transformers/all-MiniLM-L6-v2'
)
def ingest_memory_data(path):
        if collection_name not in [c.name for c in chroma_client.list_collections()]:
            print(f"Memories getting inserted to Chromadb collection : {collection_name}")
            collection = chroma_client.get_or_create_collection(
                name= collection_name,
                embedding_function = ef
            )
            df = pd.read_csv(path)
            documents = df["Memory"].tolist()
            metadatas = [
                {
                    "date": str(row["Date"]),
                    "event": row["Event "],
                    "tag": row["Tag"],
                    "image_url": row["Image"]
                }
                for _, row in df.iterrows()
            ]
            ids = [f"ids_{i}" for i in range(len(df))]

            collection.add(
                documents = documents,
                metadatas = metadatas,
                ids = ids
            )
            print(f"Memories inserted to Chromadb collection : {collection_name}")
        else:
            print("Collection Already Exists !!")


def get_relevant_qa(query):
    collection = chroma_client.get_collection(
        name=collection_name,
        embedding_function=ef
    )
    result = collection.query(
        query_texts=[query],
        n_results= 5
    )
    return result


def ask_llm(query):
    result = get_relevant_qa(query)
    docs = result["documents"][0]
    metas = result["metadatas"][0]

    context = ""
    for i, (m, meta) in enumerate(zip(docs, metas)):
        context += f" Date: {meta.get('date')}\n📝 Memory: {m}\n📌 Event: {meta.get('event')}\n🏷️ Tag: {meta.get('tag')}\n\n"
    answer = generate_answer(query,context)
    return answer


def generate_answer(query, context):
    prompt = f"""
    You are Zwan, a boy who is deeply attached to a girl named Vita. You are speaking in first-person tone, directly answering questions Vita might ask you. Your responses must be:

    - 💬 Polite and respectful
    - ❤️ Emotionally honest and warm
    - 🧠 Based strictly on the memories provided below
    - 🧭 If multiple memories refer to meetings or conversations, consider the **earliest dated memory** as the first
    - ❌ Never invent events or emotions not present in the memory
    - ✅ If the question is just a greeting like "Hi" or "How are you", feel free to respond lovingly as Zwan

    Here are the memories between Zwan and Vita, along with their dates:

    {context}

    Now, based on these memories, answer the following question as **Zwan**, using the **earliest accurate date** mentioned for any meeting:

    **Q (from Vita):** {query}

    **A (as Zwan):**
    """
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model= os.environ["GROQ_MODEL"]
    )
    return chat_completion.choices[0].message.content
    

def ask_query(query):
    ingest_memory_data(mem_path)
    answer = ask_llm(query)
    match_result = chroma_client.get_collection(
        name=collection_name,
        embedding_function=ef
    ).query(
        query_texts=[answer],
        n_results=1
    )
    selected_image_url = match_result["metadatas"][0][0].get("image_url", "")
    return answer, selected_image_url



if __name__ == "__main__":
    ingest_memory_data(mem_path)
    query = "When did we first message on instagram?"
    answer = ask_llm(query)
    match_result = chroma_client.get_collection(
        name=collection_name,
        embedding_function=ef
    ).query(
        query_texts=[answer],
        n_results=1
    )
    selected_image_url = match_result["metadatas"][0][0].get("image_url", "")
    print(answer, selected_image_url)
