import socket as st
import pandas as pd
import pickle
import base64
import os
import feather

from time import time
from math import sqrt

SERVER = '127.0.0.1'
PORT = 5052
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
HEADERSIZE = 10
DISCONNECT_MESSAGE = "!DISCONNECT"

def calculate_signal(filename):
    convert_feather(f'{filename}')
    g = load_feather(f'{filename}.feather')
    n = 64

    s = 794 if len(g) > 50000 else 436

    for c in range(n):
        for l in range(s):
            y = 100 + (1/20) * l * sqrt(l)
            g[l + c * s] = g[l + c * s] * y

    return g

def convert_feather(path):
    start_time = time()
    df = pd.read_csv(f'{path}.csv', header=None)
    df.columns = df.columns.astype(str)
    df.to_feather(f'{path}.feather')
    print(f'\nSize of feather: {len(df)}')
    end_time = time()
    return end_time - start_time

def printMainMenu():
    option = int (input('\nInforme uma opção:\n1 - Reconstruir Imagem\n2 - Receber imagens\n3 - Sair\n-> '))
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
    name = input('Informe seu nome\n-> ')
    while True:
        option = printMainMenu()

        if option == 1:
            client = st.socket(st.AF_INET, st.SOCK_STREAM)
            client.connect(ADDR)

            algorithm = input('\nInforme o algoritmo: CGNE (1) ou CGNR (2)\n-> ')
            filename = input('\nInforme o nome do arquivo de sinal\n-> ')

            g = calculate_signal(filename)

            info = {1: name, 2: algorithm, 3: g}
            msg = pickle.dumps(info)
            msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg

            client.send(msg)
            input('\nSinal enviado. Clique ENTER para continuar...')

            client.close()

        elif option == 2:
            client = st.socket(st.AF_INET, st.SOCK_STREAM)
            client.connect(ADDR)

            tp = input('\nInforme se irá ser recebido uma(1) ou todas as imagens (2)\n-> ')

            info = {1: name, 2: tp}
            msg = pickle.dumps(info)
            msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg

            client.send(msg)

            data = b''
            while True:
                msg = client.recv(1024)
                if not msg: break
                data += msg

            info = pickle.loads(data[HEADERSIZE:])
            
            client.close()
            if tp == '1':                
                client = st.socket(st.AF_INET, st.SOCK_STREAM)
                client.connect(ADDR)

                itr = 1
                for image in info:
                    print(f'{itr} - {image}')
                    itr = itr + 1

                image_option = int(input('\nEscolha uma imagem\n-> '))

                info = {1: name, 2: image_option}
                msg = pickle.dumps(info)
                msg = bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg

                client.send(msg)

                data = b''
                while True:
                    msg = client.recv(1024)
                    if not msg: break
                    data += msg

                info = pickle.loads(data[HEADERSIZE:])

                img = open(f'{image_option}.png', 'wb')
                img.write(base64.b64decode((info)))
                img.close()

                input('Imagem salva com sucesso. Clique ENTER para continuar...')

                client.close()
            
            elif tp == '2':
                itr = 1
                for image in info:
                    img = open(f'{itr}.png', 'wb')
                    img.write(base64.b64decode((image)))
                    img.close()
                    itr = itr + 1
                    
                input('Imagens salvas com sucesso. Clique ENTER para continuar...')

            else:
                print('ERROR')

            client.close()

        elif option == 3:
            break

        else:
            print('Opção inválida')
            input()     

        clearConsole()