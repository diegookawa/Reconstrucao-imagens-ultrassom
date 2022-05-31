import csv
import numpy as np

def load(path):
    with open(path, "r") as csvfile:
        datareader = csv.reader(csvfile)
        for row in datareader:
            yield row

if "__main__" == __name__:
    path = "Tarefa02/G-1.csv"
    g = list(load(path))
    g.tobytes()
    
