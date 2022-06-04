import csv
from tracemalloc import start
import feather
from time import time
import numpy as np
import pandas as pd

def feather_read():
    start_time = time()
    df = pd.read_feather('Models/H-1.feather')
    end_time = time()
    return df, end_time - start_time

def convert_feather(path):
    start_time = time()
    df = pd.read_csv(f'{path}.csv')
    df.to_feather(f'{path}.feather')
    end_time = time()
    return end_time - start_time

if "__main__" == __name__:
    print(f"Time to convert: {convert_feather('Signals/G-2')}")
