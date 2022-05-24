import numpy as np 
import csv

def read_csv(filename):
    with open(filename, "rb") as csvfile:
        datareader = csv.reader(csvfile)
        yield next(datareader)  # yield the header row
        count = 0
        for row in datareader:
            yield row
            count += 1
            if count:
                return

def cgne(H, g, f, r, p, a, B):

    f[0] = 0
    r[0] = g - np.dot(H, f[0])
    p[0] = np.dot(np.transpose(H), r[0])

    for i in range(len(g)):
        a[i] = (np.dot(np.transpose(r[i]), r[i])) / (np.dot(np.transpose(p[i]), p[i]))
        f[i + 1] = f[i] + np.dot(a[i], p[i])
        r[i + 1] = r[i] - np.dot(np.dot(a[i], H), p[i])
        B[i] = (np.dot(np.transpose(r[i + 1]), r[i + 1])) / (np.dot(np.transpose(r[i]), r[i]))
        p[i + 1] = np.dot(np.transpose(H), r[i + 1]) + np.dot(B[i], p[i])

if __name__ == '__main__':
    #a = read_csv('a.csv', 'float')
    #M = read_csv('M.csv', 'int')
    #N = read_csv('N.csv', 'int')

    #print(f'M = {M}')
    #print(f'N = {N}')
    #print(f'aM = {np.dot(a,M)}')
    #print(f'MN = {np.dot(M,N)}')

