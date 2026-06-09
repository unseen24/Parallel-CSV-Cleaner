import pandas as pd

def remove_nulls(chunk):
    return chunk.dropna()

def remove_duplicates(chunk):
    return chunk.drop_duplicates(subset=["Order ID"])

def strip_whitespace(chunk):
    string_cols = ["Order ID", "Ship Mode", "Customer ID", "Customer Name", 
                   "Segment", "Country", "City", "State", "Region", 
                   "Product ID", "Category", "Sub-Category", "Product Name"]
    chunk[string_cols] = chunk[string_cols].apply(lambda col: col.str.strip())
    return chunk

def standardize_dates(chunk):
    chunk["Order Date"] = pd.to_datetime(chunk["Order Date"], dayfirst=True)
    chunk["Ship Date"] = pd.to_datetime(chunk["Ship Date"], dayfirst=True)
    return chunk

def fix_types(chunk):
    chunk["Sales"] = pd.to_numeric(chunk["Sales"], errors="coerce")
    chunk["Postal Code"] = chunk["Postal Code"].astype(str).str.zfill(5)
    chunk["Row ID"] = pd.to_numeric(chunk["Row ID"], errors="coerce")
    return chunk

def standardize_text(chunk):
    chunk["Ship Mode"] = chunk["Ship Mode"].str.title()
    chunk["Segment"] = chunk["Segment"].str.title()
    chunk["Category"] = chunk["Category"].str.title()
    chunk["City"] = chunk["City"].str.title()
    chunk["State"] = chunk["State"].str.title()
    chunk["Region"] = chunk["Region"].str.title()
    return chunk

def standardize_dates(chunk):
    chunk["Order Date"] = pd.to_datetime(chunk["Order Date"], dayfirst=True).dt.date
    chunk["Ship Date"] = pd.to_datetime(chunk["Ship Date"], dayfirst=True).dt.date
    return chunk


def clean_chunk(chunk):
    chunk = remove_nulls(chunk)
    chunk = remove_duplicates(chunk)
    chunk = strip_whitespace(chunk)
    chunk = standardize_dates(chunk)
    chunk = fix_types(chunk)
    chunk = standardize_text(chunk)
    chunk = standardize_dates(chunk)
    return chunk