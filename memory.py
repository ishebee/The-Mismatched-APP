import sys
import os
try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")  # Force updated SQLite
except ImportError:
    print("⚠️ pysqlite3-binary is missing. Install it using `pip install pysqlite3-binary`.")

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
    - Just start with Hey Vita or Vita... or Hey nga or Ennanga or Kanna or Hey Kanna ...(Nothing other than this) 
    
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
        journal_image = "https://raw.githubusercontent.com/ishebee/The-Mismatched-APP/refs/heads/main/resources/images/The-Birthday-Journal.jpg"
        return f"""
        Hey Vita,\n
        This date {norm_date or date} may be we hadn't talked much. Why not You look for some specific dates like in:  
        January 2024   : 11, 12, 14 & 16\t
        February 2024  : 02, 13, 14, 21 & 26\n
        March 2024     : 03, 05, 15, 25 & 26\t
        April 2024     : 01, 02, 09, 10, 16 -> 19, 21, 26, 28 & 30\n
        May 2024       : 02, 03, 06, 10, 11, 13, 17, 18 & 29\t
        June 2024      : 05, 06, 08 -> 13, 15 -> 18, 21, 23, 25 & 29\n
        July 2024      : 02, 03, 09, 11 -> 13, 15 -> 27 & 29 \t
        August 2024    : 01, 03, 04, 08, 10, 14, 23, 27 & 29 -> 31\n
        September 2024 : 01, 06, 11, 12, 15 -> 18, 22 & 23\t
        October 2024   : 01 -> 07, 15, 19 & 31\n
        Apart from choosing the above dates, if you remember any memory just say, I will check If I remember or not.
        Though here's for you the context of ur birthday journal to read. 
        """,  journal_image


    answer = generate_answer(f"What happened on {norm_date}?", context)
    return answer, image_url

def ask_query(query):
    ingest_memory_data()
    result = get_relevant_qa(query)
    metas = result["metadatas"][0]
    context = get_context_from_df(None, metas)
    image_url = get_image_from_df(None, metas)
    return generate_answer(query, context), image_url
