import socket as st
import pandas as pd
import pickle
import os
from time import time

SERVER = '127.0.0.1'
PORT = 5052
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
HEADERSIZE = 10

def main ():

    client = st.socket(st.AF_INET, st.SOCK_STREAM)
    client.connect(ADDR)

    while True:

        option = printMainMenu()

        if option == 1:

            name = input('Informe seu nome: ')
            algorithm = input('Informe o algoritmo: CGNE (1) ou CGNR (2): ')
            path = input('Informe o sinal: ')

            g = load_feather(path)

            info = {1: name, 2: algorithm, 3: g}
            msg = pickle.dumps(info)
            print(len(msg))

            msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg

            client.send(msg)
            
            # client.close()

            input()

        elif option == 2:
            break

        else:
            print('Opção inválida')
            input()     

        clearConsole()   

def printMainMenu():

    option = int (input('Informe uma opção:\n1 - Reconstruir Imagem\n2 - Sair\n'))
    return option

def clearConsole():
    os.system('clear')

def load_feather(path):

    filename = os.path.splitext(os.path.split(path)[1])[0]
    start_time = time()

    print(f'[   Loading file: {filename}    ]')

    file = pd.read_feather(path).to_numpy(dtype=float)
    end_time = time()

    print(f'[   Loading finished.   ]')
    print(f'[   Time spent on loading: {end_time - start_time}  ]')

    return file

if __name__ == '__main__':
    main()
            