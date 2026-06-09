import functions.file as f
import functions.workers as w
import functions.database as db
import os

def process(file_path):
    os.makedirs("db", exist_ok=True)
    db.init_db()
    chunks = f.split_csv(file_path)
    cleaned_df = w.distribute_work(chunks)
    db.insert_records(cleaned_df)

    #show how the parallel programming works

if __name__ == "__main__":
    process("C:\\Users\\Renz\\Downloads\\archive\\train.csv")