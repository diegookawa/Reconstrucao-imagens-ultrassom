import socket as st
import pandas as pd
import pickle
import os
import feather
from time import time

SERVER = '127.0.0.1'
PORT = 5052
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
HEADERSIZE = 10
DISCONNECT_MESSAGE = "!DISCONNECT"

def convert_feather(path):
    start_time = time()
    df = pd.read_csv(f'{path}.csv', header=None)
    df.columns = df.columns.astype(str)
    df.to_feather(f'{path}.feather')
    print(f'Size of feather: {len(df)}')
    end_time = time()
    return end_time - start_time

def printMainMenu():
    option = int (input('Informe uma opção:\n1 - Reconstruir Imagem\n2 - Receber imagens\n3 - Sair\n'))
    return option

def clearConsole():
    os.system('clear')

def load_feather(path):
    filename = os.path.splitext(os.path.split(path)[1])[0]
    start_time = time()

    print(f'[LOADING] File {filename}')

    file = pd.read_feather(path).to_numpy(dtype=float)
    end_time = time()

    print(f'[LOADING FINISHED]')
    print(f'[TIME SPENT] {end_time - start_time}')

    return file

if __name__ == '__main__':
    name = input('Informe seu nome: ')
    while True:
        option = printMainMenu()

        if option == 1:
            client = st.socket(st.AF_INET, st.SOCK_STREAM)
            client.connect(ADDR)

            algorithm = input('Informe o algoritmo: CGNE (1) ou CGNR (2): ')
            filename = input('Informe o nome do arquivo de sinal: ')

            convert_feather(f'{filename}')

            g = load_feather(f'{filename}.feather')

            info = {1: name, 2: algorithm, 3: g}
            msg = pickle.dumps(info)

            msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg

            client.send(msg)

            client.close()

        elif option == 2:
            client = st.socket(st.AF_INET, st.SOCK_STREAM)
            client.connect(ADDR)

            tp = input('Informe se irá ser recebido uma(1) ou todas as imagens (2)')

            info = {1: name, 2: tp}
            msg = pickle.dumps(info)
            msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg

            client.send(msg)

            client.close()
        elif option == 3:
            break

        else:
            print('Opção inválida')
            input()     

        clearConsole()