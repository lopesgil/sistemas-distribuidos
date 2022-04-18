import socket

HOST = 'localhost'
PORT = 9090

sock = socket.socket()
sock.bind((HOST, PORT))
sock.listen(1)
print('Esperando conexão...')
(conn, addr) = sock.accept()

print('Cliente conectado: ', addr)
while True:
    data = conn.recv(1024)
    if str(data, 'utf-8') == '\quit' or not data:
        break
    conn.send(data)

conn.close()
print('Conexão encerrada.')
sock.close()
