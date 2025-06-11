import sys
import os
try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")  # Force updated SQLite
except ImportError:
    print("⚠️ pysqlite3-binary is missing. Install it using `pip install pysqlite3-binary`.")

from dateutil import parser
import random

from memory_utils import paragraph_df

def normalize_date(date_input):
    try:
        dt = parser.parse(date_input, fuzzy=True, dayfirst=False)
        return dt.strftime("%m/%d/%Y")
    except Exception:
        return None

def get_image_from_df(date=None, metas=None):
    df = paragraph_df  # ensure df is loaded globally or passed here

    if date:
        match = df[df["Date"] == date]
        images = match["Image"].dropna().astype(str)
        image = images.iloc[0].strip() if not images.empty else None

    elif metas:
        events = list({m["event"] for m in metas})
        filtered = df[df["Event"].isin(events)]
        images = filtered["Image"].dropna().astype(str)
        image = images.iloc[0].strip() if not images.empty else None

    else:
        image = None

    return image if image and image.startswith("http") else None

def get_random_images():
    img_lst = paragraph_df["Image"].dropna().tolist()
    return random.choice(img_lst)


def get_available_dates():
    return paragraph_df["Date"].dropna().unique().tolist()
