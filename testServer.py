import csv
from fileinput import filename
from hashlib import algorithms_available
import os
import socket as st
import threading
import numpy as np
import pandas as pd
import pickle
#import feather
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from time import time

HEADER = 64
PORT = 5052
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
HEADERSIZE = 10

#server = st.socket(st.AF_INET, st.SOCK_STREAM)
#server.bind(ADDR)

def load_feather(path):
    # Loads feather file based on path
    filename = os.path.splitext(os.path.split(path)[1])[0]
    start_time = time()
    print(f'[   Loading file: {filename}    ]')
    file = pd.read_feather(path).to_numpy(dtype=float)
    end_time = time()
    print(f'[   Loading finished.   ]')
    print(f'[   Time spent on loading: {end_time - start_time}  ]')
    return file

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT))

    conn.close()

def start_server():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

def dot_transpose(v):
    return np.transpose(v).dot(v)

def cgne_np(H, g):
    f_i = np.zeros((3600, 1))
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
            print(f'[   Processed {i + 1} times ]')
            break

        p_i = np.dot(np.transpose(H), r_i) + beta * p_i
    return f_i

def cgnr(H, g):
    f_i = np.zeros((3600, 1))
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
            print(f'[   Processed {i + 1} times ]')
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

def process_image(name, signal):
    # Load image based on request
    g = load_feather('Signals/' + signal)
    if len(g) > 50000:
        H = load_feather('Models/H-1.feather')
    else:
        H = load_feather('Models/H-2.feather')

    # Process 
    start_time = time()
    f = cgne_np(H, g)
    end_time = time()
    print(f'[   Time to process data: {end_time - start_time}    ]')
    # f = cgnr(H, g)
    f = np.reshape(f, (60, 60), order='F')

    signal_name = os.path.splitext(signal)[0]
    name_dir = f'Images/{name}'
    mkdir_p(name_dir)
    plt.imshow(f, cmap='gray')
    plt.savefig(f'{name_dir}/{signal_name}.png')




#New functions

def process_image02(name, g):
    # Load image based on request
    if len(g) > 50000:
        H = load_feather('Models/H-1.feather')
    else:
        H = load_feather('Models/H-2.feather')

    # Process 
    start_time = time()
    f = cgne_np(H, g)
    end_time = time()
    print(f'[   Time to process data: {end_time - start_time}    ]')
    # f = cgnr(H, g)
    f = np.reshape(f, (60, 60), order='F')

    #signal_name = os.path.splitext(g)
    name_dir = f'Images/{name}'
    mkdir_p(name_dir)
    plt.imshow(f, cmap='gray')
    plt.savefig(f'{name_dir}/Image.png')

def convert_csv_to_feather(path):

    df_file = pd.read_csv(path + '.csv')

    df_file.to_feather(path + '.feather', compression='uncompressed')

def start_server02():
    
    s = st.socket(st.AF_INET, st.SOCK_STREAM)
    s.bind(ADDR)
    s.listen(5)

    print('Server Started.')

    while True:

        conn, addr = s.accept()
        print(f'Client connected ip: <{addr}>')

        full_msg = b''
        new_msg = True

        while True:

            msg = conn.recv(1024)

            if new_msg:

                print(f'New msg lenght: {msg[:HEADERSIZE]}')
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            full_msg += msg

            if len(full_msg) - HEADERSIZE == msglen:

                print('Full msg received')

                info = pickle.loads(full_msg[HEADERSIZE:])
                username = info[1]
                print(username)
                algorithm = info[2]
                g = info[3]
                new_msg = True
                full_msg = b''

                process_image02(username, g)
                s.close()

if __name__ == '__main__':
    print("[STARTING] server is starting...")
    #start_server()
    start_server02()
    #convert_csv_to_feather()
    process_image('João', 'G-1.feather')
