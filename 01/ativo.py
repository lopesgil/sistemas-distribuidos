import socket

HOST = 'localhost'
PORT = 9090

sock = socket.socket()
sock.connect((HOST, PORT))
print('Conectado ao servidor')

while True:
    msg = input('Digite uma mensagem: ')
    sock.send(msg.encode())
    if msg == '\quit':
        break
    resp = sock.recv(1024)
    print('Resposta do servidor: ', resp.decode())

print('Conexão encerrada.')
sock.close()
