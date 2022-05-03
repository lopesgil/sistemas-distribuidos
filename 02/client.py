import socket

HOST = "localhost"
PORT = 5000

sock = socket.socket()
sock.connect((HOST, PORT))
print("Conectado ao servidor")

# Camada de interface de usuário
while True:
    msg = input("Digite o nome do arquivo: ")
    sock.send(msg.encode())
    if msg == "/quit":
        break
    resp = sock.recv(1024)
    print("Resposta do servidor: \n", resp.decode())

print("Conexão encerrada.")
sock.close()
