import numpy as np 
import csv

def main():

    a = lerArquivo('a.csv', 'vetor')
    M = lerArquivo('M.csv', 'matriz')
    N = lerArquivo('N.csv', 'matriz')

    print(f'a = {a}')
    print(f'M = {M}')
    print(f'N = {N}')
    print(f'aM = {np.dot(a,M)}')
    print(f'MN = {np.dot(M,N)}')

def lerArquivo(nome, tipo):

    if tipo.lower() == 'vetor':
        linhas = 1
    
    elif tipo.lower() == 'matriz':
        linhas = 10

    else:
        print('Tipo nao definido')
        return
    
    a = np.zeros((linhas, 10))

    caminho = 'Tarefa02/' + nome

    with open(caminho, 'r') as arquivo:

        dados = csv.reader(arquivo, delimiter=';')
        cont = 0

        for linha in dados:

            a[cont] = linha
            cont = cont + 1

    return a

if __name__ == '__main__':
    main()

