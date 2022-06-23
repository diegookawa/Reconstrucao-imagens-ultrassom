from lib2to3.pytree import convert
import feather
import pandas as pd
from time import time
from enum import IntEnum

def convert_feather(path):
    start_time = time()
    df = pd.read_csv(f'{path}.csv', header=None)
    df.columns = df.columns.astype(str)
    df.to_feather(f'{path}.feather')
    print(f'\nSize of feather: {len(df)}')
    end_time = time()
    return end_time - start_time

if "__main__"  == __name__:
    convert_feather('Server/Models/H-2')