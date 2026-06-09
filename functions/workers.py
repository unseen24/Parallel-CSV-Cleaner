import functions.clean as cln
import pandas as pd
from multiprocessing import Pool

def distribute_work(chunks):

    with Pool(processes=4) as pool:
        #call cleaning functions on each chunk
        results = pool.map(cln.clean_chunk, chunks)

    results = pd.concat(results, ignore_index=True)

    return results

def distribute_work_n(chunks, n):
    with Pool(processes=n) as pool:
        results = pool.map(cln.clean_chunk, chunks)
    return pd.concat(results).reset_index(drop=True)
