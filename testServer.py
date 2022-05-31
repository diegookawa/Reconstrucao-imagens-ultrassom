import csv
import time
import socket as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def read_csv(filename, return_type):
    prefix = 'Tarefa02/'
    with open(prefix + filename, "r") as csvfile:
        datareader = csv.reader(csvfile)
        for row in datareader:
            yield [return_type(i) for i in row]

def load_csvs():
    print("Loading files")
    start_time = time.time()
    H = list(read_csv('H-1.csv', float))
    print(f"H matrix loaded")
    g = list(read_csv('G-1.csv', float))
    print(f"{len(g)} lines of G signal loaded")
    end_time = time.time()
    print("Finished loading")
    print(f"Load time: {end_time - start_time}")
    return H, g

def initiate_socket():
    try:
        s = st.socket()
        print(f"Socketed created")
    except st.error as err:
        print(f"Socket error {err}")

    HOST = '127.0.0.1'
    PORT = 12345

    s.bind((HOST, PORT))
    print(f"Socket binded to {PORT} on {HOST}")

    s.settimeout(100)

    return s

def listen_socket(s, H, g):
    while True:
        s.listen()

        c, addr = s.accept()
        print(f"Connection created from {addr}")

        c.send(f"Connected to the server".encode())

        c.send(f"G Signal: {g[0]}".encode())

def cgne(H, g):

    f = np.zeros((3600, 1))
    r = g - np.dot(H, f)
    p = np.dot(np.transpose(H), r)
    erro = 1e-4

    for i in range(1, len(g)):
        ap = np.dot(H, p)
        rsold = np.dot(np.transpose(r), r)

        a = rsold / np.dot(np.transpose(p), p)
        f = f + np.dot(a, p)
        r = r - np.dot(a, ap)
        beta = np.dot(np.transpose(r), r) / rsold

        if beta < erro:
            break

        p = np.dot(np.transpose(H), r) + beta * p

    return f

# def cgne02(H, g):

#      f = []
#      r = []
#      p = []
#      erro = 1e10-4

#      f.append(0)
#      r.append(g - np.dot(H, f[0]))
#      p.append(np.dot(np.transpose(H), r[0]))

#      for i in range(len(g)):

#          a = (np.dot(np.transpose(r[i]), r[i])) / (np.dot(np.transpose(p[i]), p[i]))
#          f.append(f[i] + np.dot(a, p[i]))
#          r.append(r[i] - np.dot(a, np.dot(H, p[i])))
#          b = np.dot(np.transpose(r[i + 1]), r[i + 1]) / np.dot(np.transpose(r[i]), r[i])
#          if np.sqrt(r[i + 1]) < erro:
#              break
#          p.append(np.dot(np.transpose(H), r[i + 1]) + np.dot(b, p[i]))

#      return f

# def create_mesh(f):
#     x = np.arange(0, 60, 1)
#     y = np.arange(0, 60, 1)
#     X, Y = np.meshgrid(x, y)
#     Z = np.zeros(X.shape)
#     mesh_size = range(len(X))
#     for i, j in product(mesh_size, mesh_size):
#         x_coor = X[i][j]
#         y_coor = Y[i][j]
#         Z[i][j] = f(np.array([x_coor, y_coor]))
#     return X, Y, Z

# def plot_contour(ax, X, Y, Z):
#     ax.set(
#         title='Path During Optimization Process',
#         xlabel='x1',
#         ylabel='x2'
#     )
#     CS = ax.contour(X, Y, Z)
#     ax.clabel(CS, fontsize='smaller', fmt='%1.2f')
#     ax.axis('square')
#     return ax

# def f(x):
#     Ax = np.dot(H, x)
#     xAx = np.dot(x, Ax)
#     gx = np.dot(g, x)
#     return 0.5 * xAx - gx

if __name__ == '__main__': 
    # Load variables in cache
    H, g = load_csvs()
    # Initiate socket
    #s = initiate_socket()
    # Listen to socket
    #listen_socket(s, H, g)

    f = cgne(H, g)

    #fig, ax = plt.subplots(figsize=(60, 60))
    #X, Y, Z = create_mesh(f)
    #ax = plot_contour(ax, X, Y, Z)
    #ax.plot(xs[:,0], xs[:,1], linestyle='--', marker='o', color='orange')
    #ax.plot(xs[-1,0], xs[-1,1], 'ro')
    #plt.show()
    

    f = np.reshape(f, (60, 60))

    f = np.transpose(f)

    plt.imshow(f, cmap='gray')
    plt.savefig('image.png')
    
    #print(H)




