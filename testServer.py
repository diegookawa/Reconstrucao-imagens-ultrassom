import csv
import time
import socket as st

def read_csv(filename, return_type):
    prefix = 'Tarefa02/'
    with open(prefix + filename, "r") as csvfile:
        datareader = csv.reader(csvfile)
        for row in datareader:
            is_v = len(row) > 0
            break
        if is_v:
            for row in datareader:
                yield [return_type(i) for i in row]
        else:
            for row in datareader:
                yield return_type(i)

def load_csvs():
    print("Loading files")
    start_time = time.time()
    H = list(read_csv('H-1.csv', float))
    print("H matrix loaded")
    g = list(read_csv('G-1.csv', float))
    print("G signal loaded")
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

if __name__ == '__main__': 
    # Load variables in cache
    H, g = load_csvs()
    # Initiate socket
    s = initiate_socket()
    # Listen to socket
    listen_socket(s, H, g)




