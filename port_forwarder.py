'''
Simple port forwarder

Usage: <script> <LISTEN_PORT> <FORWARD_TO_HOST> <FORWARD_TO_PORT>

Author: Eli Finkel - eyfinkel@gmail.com
'''

import socket
import sys
import threading
import time

LISTEN_PORT = None
FORWARD_TO_HOST = None
FORWARD_TO_PORT = None

def main():
    global LISTEN_PORT
    global FORWARD_TO_HOST
    global FORWARD_TO_PORT
    
    try:
        LISTEN_PORT = int(sys.argv[1])
        FORWARD_TO_HOST = sys.argv[2]
        FORWARD_TO_PORT = int(sys.argv[3])
    except (IndexError, ValueError, AssertionError) as e:
        print(f'Please pass <LISTEN_PORT> <FORWARD_TO_HOST> <FORWARD_TO_PORT>')
        print(e)
        return
    
    try:
        threading.Thread(target=server, daemon=True).start()
        print(f'Starting (fowarding port {LISTEN_PORT} -> {FORWARD_TO_HOST}:{FORWARD_TO_PORT}). ctrl-c to stop.')
        # wait for <ctrl-c>
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        pass
    

def server():
    dock_socket = socket.socket()
    dock_socket.bind(('', LISTEN_PORT))
    dock_socket.listen()
    
    while True:
        print(f'\nWaiting for incoming connections...')
        client_socket = dock_socket.accept()[0]
        print(f'Received connection from {client_socket.getpeername()}... ', end='', flush=True)
        
        try:
            server_socket = socket.socket()
            server_socket.connect((FORWARD_TO_HOST, FORWARD_TO_PORT))
        except Exception as e:
            print(f'ERROR:')
            print(f'     Cannot forward connection - {e}\n')
            client_socket.shutdown(socket.SHUT_RDWR)
        else:
            print(f'Success')
            threading.Thread(target=forward, args=(client_socket, server_socket), daemon=True).start()
            threading.Thread(target=forward, args=(server_socket, client_socket), daemon=True).start()
            time.sleep(1) # allow threads to start and print
        

def forward(src, dest):
    threadName = f'forwarding {threading.current_thread().getName()} ' \
        f'{src.getpeername()}->{dest.getpeername()}'
    print(f'Starting {threadName}')
    data = '<>'
    try:
        while data:
            data = src.recv(4096)
            if data:
                dest.sendall(data)
            else:
                src.shutdown(socket.SHUT_RDWR)
                dest.shutdown(socket.SHUT_RDWR)
    except Exception as e:
            print(f'ERROR: in {threadName}')
            print(f'{e}\n')
            src.shutdown(socket.SHUT_RDWR)
            dest.shutdown(socket.SHUT_RDWR)
    print(f'Finishing {threadName}')

if __name__ == '__main__':
    main()
    