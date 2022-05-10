import numpy as np 
import csv

def main():

    a = lerArquivo('a.csv')
    M = lerArquivo('M.csv')
    N = lerArquivo('N.csv')

    print(f'M = {M}')
    print(f'N = {N}')
    print(f'aM = {np.dot(a,M)}')
    print(f'MN = {np.dot(M,N)}')

def lerArquivo(nome):

    caminho = 'Tarefa02/' + nome

    with open(caminho, 'r') as arquivo:

        dados = csv.reader(arquivo, delimiter=';')
        linhas = 0

        for linha in dados:
            linhas = linhas + 1
    
    a = np.zeros((linhas, 10))
    
    with open(caminho, 'r') as arquivo:

        dados = csv.reader(arquivo, delimiter=';')
        linhas = 0

        for linha in dados:
            a[linhas] = linha
            linhas = linhas + 1

    return a

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
    main()

