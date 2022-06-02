import csv
import feather
from time import time
import numpy as np
import pandas as pd

def feather_read():
    start_time = time()
    df = pd.read_feather('Tarefa02/H-1.feather')
    end_time = time()
    return df, end_time - start_time

if "__main__" == __name__:
    df, read_time = feather_read()
    print(f'Feather read time: {read_time}')
    pre_transpose = time()
    np.transpose(df)
    after_transpose = time()
    print(f'Numpy transpose time: {after_transpose - pre_transpose}')
