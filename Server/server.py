import os
import socket as st
import threading
import numpy as np
import pandas as pd
import pickle
import base64
import feather
import matplotlib.pyplot as plt
import resource
import platform
import sys
import gc

from matplotlib.ticker import MaxNLocator

from queue import Queue
from time import time
from datetime import datetime
from PIL import Image

PORT = 5052
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
HEADERSIZE = 10
BASE_PATH = 'Server'
PROCESSING_QUEUE = Queue()

erro = 1e-4

MODELS = {
    60:'H-1',
    30:'H-2'
}

server = st.socket(st.AF_INET, st.SOCK_STREAM)
server.bind(ADDR)

def memory_limit(percentage: float):
    if platform.system() != "Linux":
        print('Only works on linux!')
        return
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (get_memory() * 1024 * percentage, hard))

def get_memory():
    with open('/proc/meminfo', 'r') as mem:
        free_memory = 0
        for i in mem:
            sline = i.split()
            if str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
                free_memory += int(sline[1])
    return free_memory

def memory(percentage=0.8):
    def decorator(function):
        def wrapper(*args, **kwargs):
            memory_limit(percentage)
            try:
                return function(*args, **kwargs)
            except MemoryError:
                mem = get_memory() / 1024 /1024
                print('Remain: %.2f GB' % mem)
                sys.stderr.write('\n\nERROR: Memory Exception\n')
                sys.exit(1)
        return wrapper
    return decorator

def load_feather(path):
    # Loads feather file based on path
    filename = os.path.splitext(os.path.split(path)[1])[0]
    start_time = time()
    print(f'    [LOADING] File {filename}')
    file = pd.read_feather(path).to_numpy(dtype=float)
    end_time = time()
    print(f'    [LOADING] Finished, time spent: {end_time - start_time}.')
    return file

def pickle_format(info):
    msg = pickle.dumps(info)
    return bytes(f'{len(msg):<{HEADERSIZE}}', FORMAT) + msg

def handle_info(info, conn):
    if info['mode'] == 'process':
        print(f'    [PROCESSING] File added into the queue.')
        PROCESSING_QUEUE.put(info)
    elif info['mode'] == 'send_image':
        images = {}
        image_path = BASE_PATH + f'/Images/{info["name"]}'
        if info['image_option'] == 'U':
            if os.path.isdir(image_path):
                for image in os.listdir(image_path):
                    images[image] = image
            else:
                print('[CONNECTION] No image found')
        elif info['image_option'] == 'A':
            for image in os.listdir(image_path):
                with open(f'{image_path}/{image}', "rb") as file:
                    images[image] = base64.b64encode(file.read())
        else:
            # Send specific image
            if os.path.exists(f'{image_path}/{info["image_option"]}'):
                with open(f'{image_path}/{info["image_option"]}', "rb") as file:
                    images[os.path.basename(file.name)] = base64.b64encode(file.read())
            else:
                print('[CONNECTION] Received wrong image name')

        p = pickle_format(images)
        conn.send(p)

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
                handle_info(info, conn)
                connected = False
    conn.close()
    print(f"[CONNECTION] IP: {addr[0]}, Port: {addr[1]} disconnected.")

def dot_transpose(v):
    return np.transpose(v).dot(v)

def cgne(H, g, image):
    f_i = np.zeros((image ** 2, 1))
    r_i = g - np.dot(H, f_i)
    p_i = np.dot(np.transpose(H), r_i)

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
    return f_i, i

def cgnr(H, g, image):
    f_i = np.zeros((image ** 2, 1))
    r_i = g - np.dot(H, f_i)
    z_i = np.dot(np.transpose(H), r_i)
    p_i = z_i

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
    return f_i, i

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
    image_size = info['size']
    model_path = f'{BASE_PATH}/Models/{MODELS[info["size"]]}.feather'

    H = load_feather(model_path)

    # Process 
    start_time = time()
    f = globals()[info['alg']](H, info['signal'], image_size)
    end_time = time()
    print(f'    [PROCESSING] Time spent: {end_time - start_time}')

    f = np.reshape(f, (image_size, image_size), order='F')

    process_end = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

    name_dir = f'{BASE_PATH}/Images/{info["name"]}'
    mkdir_p(name_dir)

    metadata = {
        'Title':f'{info["name"]}',
        'Author':'Lucas Venâncio e Diego Okawa',
        'Description': f'Algorithm used: {info["alg"]} | Image size: {image_size}px | Start date: {process_start} | End date: {process_end} | Time spent: {round(end_time - start_time, 2)}s',
    }
    plt.imshow(f, 'gray')
    plt.savefig(f'{name_dir}/{info["name"]}-{process_end}.png', metadata=metadata)
    # plt.imsave(f'{name_dir}/{info["name"]}-{process_end}.png', f, metadata=metadata, cmap='gray')
    print(f'    [PROCESSING] Image saved')

    # Clear memory
    del H
    del f
    gc.collect()

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

@memory(percentage=0.8)
def main():
    print('[PROCESSING] Processing queue initiated.')
    queue_thread = threading.Thread(target=process_queue, name='Processing Thread')
    queue_thread.start()

    print("[STARTING] Server is starting...")
    start_server()


if __name__ == '__main__':
    main()