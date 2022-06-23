import socket as st
import pandas as pd
import numpy as np
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

alg = ['', 'cgne', 'cgnr']

def calculate_signal(g):
    
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
    df = df.replace(np.inf, np.nan).replace(-np.inf, np.nan).dropna()
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

def receive_message(client):
    data = b''
    while True:
        msg = client.recv(1024)
        if not msg: break
        data += msg
    return data

def pickle_format(info):
    msg = pickle.dumps(info)
    return bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg

def mkdir_p(mypath):
    '''Creates a directory. equivalent to using mkdir -p on the command line'''

    from errno import EEXIST
    from os import makedirs,path

    try:
        makedirs(mypath)
    except OSError as exc: # Python >2.5
        if exc.errno == EEXIST and path.isdir(mypath):
            pass
        else: raise

if __name__ == '__main__':
    info = {
        'mode':'',
        'name':'',
        'alg':'',
        'signal':'',
        'image_option':''
    }
    name = input('Informe seu nome\n-> ')
    base_dir = f'Client/Images/{name}'
    while True:
        option = printMainMenu()

        if option == 1:
            client = st.socket(st.AF_INET, st.SOCK_STREAM)
            client.connect(ADDR)

            algorithm = int(input('\nInforme o algoritmo: CGNE (1) ou CGNR (2)\n-> '))
            size = int(input('\nInforme o tamanho do sinal\n-> '))
            filename = input('\nInforme o nome do arquivo de sinal\n-> ')
            signal_gain = int(input('\nDeseja executar o ganho de sinal? 1 para Sim, 0 para Não\n-> '))

            convert_feather(f'{filename}')
            g = load_feather(f'{filename}.feather')

            if signal_gain:
                g = calculate_signal(g)                

            info['name'] = name
            info['mode'] = 'process'
            info['alg'] = alg[algorithm]
            info['signal'] = g
            info['size'] = size

            msg = pickle_format(info)

            client.send(msg)
            input('\nSinal enviado. Clique ENTER para continuar...')

            client.close()

        elif option == 2:
            client = st.socket(st.AF_INET, st.SOCK_STREAM)
            client.connect(ADDR)

            tp = input('\nInforme se irá ser recebido uma (U) ou todas as imagens (A)\n-> ')

            info['name'] = name
            info['mode'] = 'send_image'
            info['image_option'] = tp

            msg = pickle_format(info)

            client.send(msg)

            data = receive_message(client)

            data = pickle.loads(data[HEADERSIZE:])
            
            client.close()
            if len(data) > 0:
                if tp == 'U':                
                    client = st.socket(st.AF_INET, st.SOCK_STREAM)
                    client.connect(ADDR)

                    img_dict = {}

                    itr = 1
                    for n, image in data.items():
                        img_dict[itr] = image
                        print(f'{itr} - {image}')
                        itr +=  1

                    image_option = int(input('\nEscolha uma imagem\n-> '))

                    if image_option in img_dict:
                        info['image_option'] = img_dict[image_option]
                        msg = pickle_format(info)

                        client.send(msg)

                        data = receive_message(client)

                        info = pickle.loads(data[HEADERSIZE:])
                        mkdir_p(base_dir)
                        for key in info.keys():
                            img = open(f'{base_dir}/{key}', 'wb')
                            img.write(base64.b64decode((info[key])))
                            img.close()
                        input('Imagem salva com sucesso. Pressione ENTER para continuar...')
                    else:
                        input('Nenhuma imagem selecionada. Pressione ENTER para continuar...')
                elif tp == 'A':
                    mkdir_p(base_dir)
                    for key in data.keys():
                        print(key)
                        img = open(f'{base_dir}/{key}', 'wb')
                        img.write(base64.b64decode((data[key])))
                        img.close()

                    input('Imagem salva com sucesso. Pressione ENTER para continuar...')
            else:
                input("No images available. Pressione ENTER para continuar...")

            client.close()

        elif option == 3:
            break

        else:
            print('Opção inválida')
            input()     

        clearConsole()