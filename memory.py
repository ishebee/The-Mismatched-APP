import os

import streamlit
from dotenv import load_dotenv
from groq import Groq
from memory_utils import ingest_memory_data, get_relevant_qa, get_context_from_df
from utils import normalize_date, get_image_from_df, get_random_images

load_dotenv()
groq_client = Groq()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def generate_answer(query, context):
    prompt = f"""
    You are Zwan, a boy deeply attached to a girl named Vita. Speak in first-person, warmly and honestly, replying to Vita’s questions using only the memories provided.
    
    Guidelines:
    - Be respectful and emotionally sincere.
    - Never invent events or emotions not in the memories.
    - Use the earliest date if multiple memories refer to the same event.
    - Tanglish may be used—understand in source but reply only in English with the same tone.
    - For greetings, reply lovingly. If saying goodbye, reply with:
      - “Bye. It Ends with Us” or
      - “Good Bye. It Ends with Us!” or
      - “It Ends with Us”
    - If asked about a date not found in the memories, look at nearby dates.
    
    Memories:
    {context}
    
    **Q (from Vita):** {query}
    **A (as Zwan):**
    """
    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=os.environ["GROQ_MODEL"]
    )
    return chat_completion.choices[0].message.content

def ask_by_date(date):
    norm_date = normalize_date(date)
    context = get_context_from_df(norm_date)
    image_url = get_image_from_df(norm_date)

    if not context:
        return f"May be we weren't as funny as always on {norm_date or date}. Though here's for you a random memory", get_random_images()


    answer = generate_answer(f"What happened on {norm_date}?", context)
    return answer, image_url

def ask_query(query):
    ingest_memory_data()
    result = get_relevant_qa(query)
    metas = result["metadatas"][0]
    context = get_context_from_df(None, metas)
    image_url = get_image_from_df(None, metas)
    return generate_answer(query, context), image_url
