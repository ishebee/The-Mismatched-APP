import sys
import os
try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    print("⚠️ pysqlite3-binary is missing. Install it using `pip install pysqlite3-binary`.")

from dateutil import parser
import random
from memory_utils import load_paragraph_df

def normalize_date(date_input):
    try:
        dt = parser.parse(date_input, fuzzy=True, dayfirst=False)
        return dt.strftime("%m/%d/%Y")
    except Exception:
        return None

def get_image_from_df(date=None, metas=None):
    df = load_paragraph_df()

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
    df = load_paragraph_df()
    img_lst = df["Image"].dropna().tolist()
    return random.choice(img_lst)

def get_available_dates():
    df = load_paragraph_df()
    return df["Date"].dropna().unique().tolist()
