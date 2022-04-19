import socket
import sys

HOST = 'localhost'
PORT = 9090

sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(1)
while True:
    try:
        print(f'Esperando conexão em {HOST}:{PORT}...')
        (conn, addr) = sock.accept()

        print('Cliente conectado: ', addr)
        while True:
            data = conn.recv(1024)
            if data.decode() == '\quit' or not data:
                break
            print('Recebido: ', data.decode())
            conn.send(data)

        conn.close()
        print('Conexão encerrada.')

    except KeyboardInterrupt:
        print('\nEncerrando servidor...')
        sock.close()
        sys.exit(0)
