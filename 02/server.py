import socket
import os.path
import sys

FILE_NOT_FOUND = "Arquivo não encontrado."

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


def main():
    HOST = "localhost"
    PORT = 5000

    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen(1)
    while True:
        try:
            print(f"Esperando conexão em {HOST}:{PORT}...")
            (conn, addr) = sock.accept()

            print("Cliente conectado: ", addr)
            while True:
                data = conn.recv(1024)
                if data.decode() == "/quit" or not data:
                    break
                print("Recebido: ", data.decode())
                conn.send(data_process(data.decode()).encode())

            conn.close()
            print("Conexão encerrada.")

        except KeyboardInterrupt:
            print("\nEncerrando servidor...")
            sock.close()
            sys.exit(0)


if __name__ == "__main__":
    main()
