import pandas as pd
import numpy as np

def split_csv(file_path):

    df = pd.read_csv(file_path)
    chunks = np.array_split(df, 4)  # Split into 4 chunks

    return chunks