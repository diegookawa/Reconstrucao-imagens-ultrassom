import numpy as np 
import csv

def main():

    a = lerArquivo('a.csv')
    print(a)

def lerArquivo(nome):

    a = []

    caminho = 'Tarefa02/' + nome

    with open(caminho, 'r') as arquivo:

        dados = csv.reader(arquivo, delimiter=';')

        for linha in dados:

            for coluna in linha:
            
                a = linha

    return a

if __name__ == '__main__':
    main()

