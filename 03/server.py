import socket
import os.path
import sys
import select
import threading

FILE_NOT_FOUND = "Arquivo não encontrado."
inputs = [sys.stdin]
connections = dict()

# Camada de acesso a dados
def data_access(filename):
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            return f.read()
    else:
        return FILE_NOT_FOUND


# Camada de processamento de dados
def data_process(filename):
    data = data_access(filename)
    if data == FILE_NOT_FOUND:
        return data

    word_count = dict()

    lines = data.split("\n")
    for line in lines:
        for word in line.split():
            word_count[word.lower()] = word_count.get(word.lower(), 0) + 1

    response = "Palavras mais encontradas e suas frequências: \n"
    response += str(sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:5])
    return response


def start_server():
    HOST = "localhost"
    PORT = 5000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    sock.setblocking(False)
    inputs.append(sock)
    print(f"Servidor iniciado em {HOST}:{PORT}")
    print("Comandos: /quit /hist")
    return sock


def accept_client(sock):
    client, address = sock.accept()
    print(f"Cliente conectado: {address}")
    connections[client] = address
    return client, address


def handle_client(client, address):
    while True:
        data = client.recv(1024)
        if not data or data.decode() == "/quit":
            print("Cliente desconectado:", address)
            client.close()
            return
        filename = data.decode()
        print(f"{address} Arquivo solicitado: {filename}")
        response = data_process(filename)
        client.send(response.encode())


def main():
    clients_threads = []
    sock = start_server()
    while True:
        reading, writing, errors = select.select(inputs, [], [])
        for ready in reading:
            if ready == sock:
                client, address = accept_client(sock)
                client_thread = threading.Thread(
                    target=handle_client, args=(client, address)
                )
                client_thread.start()
                clients_threads.append(client_thread)
            else:
                cmd = input()
                if cmd == "/quit":
                    if len(clients_threads) > 0:
                        print("Encerrando servidor. Aguardando clientes...")
                    for client_thread in clients_threads:
                        client_thread.join()
                    print("Servidor encerrado.")
                    sock.close()
                    sys.exit(0)
                elif cmd == "/hist":
                    print("Histórico de conexões:")
                    for client in connections:
                        print(connections[client])


if __name__ == "__main__":
    main()
