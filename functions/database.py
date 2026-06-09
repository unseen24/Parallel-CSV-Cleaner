import sqlite3
import pandas as pd

DB_PATH = "db/results.db"

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            row_id          INTEGER,
            order_id        TEXT,
            order_date      TEXT,
            ship_date       TEXT,
            ship_mode       TEXT,
            customer_id     TEXT,
            customer_name   TEXT,
            segment         TEXT,
            country         TEXT,
            city            TEXT,
            state           TEXT,
            postal_code     TEXT,
            region          TEXT,
            product_id      TEXT,
            category        TEXT,
            sub_category    TEXT,
            product_name    TEXT,
            sales           REAL
        )
    """)
    conn.commit()
    conn.close()

def insert_data(df):

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("sales", conn, if_exists="append", index=False)
    conn.close()

def fetch_data():

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    conn.close()
    return df