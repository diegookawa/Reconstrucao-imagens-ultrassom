import os
import socket as st
import threading
import numpy as np
import pandas as pd
import pickle
import base64
import feather
import matplotlib.pyplot as plt

from matplotlib.ticker import MaxNLocator
from enum import Enum
from queue import Queue
from time import time
from datetime import datetime
from PIL import Image

PORT = 5053
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
HEADERSIZE = 10
BASE_PATH = 'Server'
PROCESSING_QUEUE = Queue()

server = st.socket(st.AF_INET, st.SOCK_STREAM)
server.bind(ADDR)

class Algorithm(Enum):
    CGNE = 1
    CGNR = 2

def load_feather(path):
    # Loads feather file based on path
    filename = os.path.splitext(os.path.split(path)[1])[0]
    start_time = time()
    print(f'    [LOADING] File {filename}')
    file = pd.read_feather(path).to_numpy(dtype=float)
    end_time = time()
    print(f'    [LOADING] Finished, time spent: {end_time - start_time}.')
    return file

def handle_client(conn, addr):
    print(f"[CONNECTION] IP: {addr[0]}, Port: {addr[1]} connected.")

    full_msg = b''
    new_msg = True

    connected = True
    while connected:
        msg = conn.recv(1024)
        if msg != b'':
            if new_msg:
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            full_msg += msg

            if len(full_msg) - HEADERSIZE == msglen:
                info = pickle.loads(full_msg[HEADERSIZE:])
                new_msg = True
                full_msg = b''
                if len(info) == 3:
                    print(f'    [PROCESSING] File added into the queue.')
                    PROCESSING_QUEUE.put(info)
                else:
                    images = []
                    if(isinstance(info[2], int)):
                        itr = 1
                        #Deve ter um jeito melhor de fazer isso, tipo pegar o indice da imagem direto em vez de percorrer todas as imagens
                        for image in os.listdir(BASE_PATH + f'/Images/{info[1]}'):
                            if(itr == info[2]):
                                with open(BASE_PATH + f'/Images/{info[1]}/{image}', "rb") as file:
                                    img = base64.b64encode(file.read())
                                p = pickle.dumps(img)
                                p = bytes(f'{len(p):<{HEADERSIZE}}', FORMAT) + p
                                conn.send(p)
                                break
                            itr = itr + 1
                    else:
                        if info[2] == '1':
                            for image in os.listdir(BASE_PATH + f'/Images/{info[1]}'):
                                images.append(image)
                            p = pickle.dumps(images)
                            p = bytes(f'{len(p):<{HEADERSIZE}}', FORMAT) + p
                            conn.send(p)

                        elif info[2] == '2':
                            for image in os.listdir(BASE_PATH + f'/Images/{info[1]}'):
                                with open(BASE_PATH + f'/Images/{info[1]}/{image}', "rb") as file:
                                    img = base64.b64encode(file.read())
                                images.append(img)
                            p = pickle.dumps(images)
                            p = bytes(f'{len(p):<{HEADERSIZE}}', FORMAT) + p
                            conn.send(p)
                        else:
                            print('Invalid option')

                connected = False
    conn.close()
    print(f"[CONNECTION] IP: {addr[0]}, Port: {addr[1]} disconnected.")

def dot_transpose(v):
    return np.transpose(v).dot(v)

def cgne(H, g, image):
    f_i = np.zeros((image ** 2, 1))
    r_i = g - np.dot(H, f_i)
    p_i = np.dot(np.transpose(H), r_i)
    erro = 1e-4

    for i in range(0, len(g)):
        # i variables        
        r_d = r_i
        a_i = dot_transpose(r_d) / dot_transpose(p_i)

        f_i = f_i + a_i * p_i
        h_p = np.dot(H, p_i) 
        r_i = r_i - a_i * h_p
        beta = dot_transpose(r_i) / dot_transpose(r_d)

        erro_i = abs(np.linalg.norm(r_i, ord=2) - np.linalg.norm(r_d, ord=2))
        
        if erro_i < erro:
            print(f'    [PROCESSING] Image processed {i + 1} times.')
            break

        p_i = np.dot(np.transpose(H), r_i) + beta * p_i
    return f_i

def cgnr(H, g, image):
    f_i = np.zeros((image ** 2, 1))
    r_i = g - np.dot(H, f_i)
    z_i = np.dot(np.transpose(H), r_i)
    p_i = z_i
    erro = 1e-4

    for i in range(0, len(g)):
        w_i = np.dot(H, p_i)
        r_d = r_i
        # i variables
        z_norm = np.linalg.norm(z_i, ord=2) ** 2
        a_i =  z_norm / np.linalg.norm(w_i, ord=2) ** 2

        f_i = f_i + a_i * p_i
        r_i = r_i - a_i * w_i
        z_i = np.dot(np.transpose(H), r_i)
        beta = np.linalg.norm(z_i, ord=2) ** 2/ z_norm

        erro_i = abs(np.linalg.norm(r_i, ord=2) - np.linalg.norm(r_d, ord=2))

        if erro_i < erro:
            print(f'    [PROCESSING] Image processed {i + 1} times.')
            break

        p_i = z_i + beta * p_i
    return f_i

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

def process_image(info):
    process_start = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    image_size = 0
    if len(info[3]) > 50000:
        image_size = 60
        model_path = BASE_PATH + '/Models/H-1.feather'
    else:
        image_size = 30
        model_path = BASE_PATH + '/Models/H-2.feather'

    H = load_feather(model_path)

    alg = Algorithm(int(info[2])).name 

    # Process 
    start_time = time()
    if alg == 'CGNE':
        f = cgne(H, info[3], image_size)
    elif alg == 'CGNR':
        f = cgnr(H, info[3], image_size)
    else:
        print('Error')
    end_time = time()
    print(f'    [PROCESSING] Time spent: {end_time - start_time}')

    f = np.reshape(f, (image_size, image_size), order='F')

    process_end = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    name_dir = f'{BASE_PATH}/Images/{info[1]}'
    mkdir_p(name_dir)

    metadata = {
        'Title':f'{info[1]}',
        'Author':'Lucas Venâncio e Diego Okawa',
        'Description': f'Algorithm used: {alg} | Image size: {image_size}px | Start date: {process_start} | End date: {process_end} | Time spent: {round(end_time - start_time, 2)}s',
    }
    # plt.imshow(f, 'gray')
    # plt.savefig(f'{name_dir}/{info[1]}-{process_end}.png', metadata=metadata)
    plt.imsave(f'{name_dir}/{info[1]}-{process_end}.png', f, metadata=metadata, cmap='gray')
    print(f'    [PROCESSING] Image saved')

def start_server():
    server.listen(5)

    print(f"[LISTENING] Server is listening on {SERVER}")

    while True:
        conn, addr = server.accept()

        response_thread = threading.Thread(target=handle_client, name=f'Connection thread',args=(conn, addr))
        response_thread.start()

def process_queue():
    while True:
        if PROCESSING_QUEUE.qsize() > 0:
            print(f'    [PROCESSING] Signal found in queue')
            process_image(PROCESSING_QUEUE.get())

if __name__ == '__main__':
    print('[PROCESSING] Processing queue initiated.')
    queue_thread = threading.Thread(target=process_queue, name='Processing Thread')
    queue_thread.start()

    print("[STARTING] Server is starting...")
    start_server()
