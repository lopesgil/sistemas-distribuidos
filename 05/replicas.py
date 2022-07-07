import rpyc, sys, multiprocessing, getopt

procs = []

USAGE = (
    "Uso: python3 replicas.py [-c|--create] <id>"
    + "\n"
    + "Onde:\n"
    + "  -c, --create Cria as réplicas permanentes nas portas 5001-5004"
    + "\n"
    + "  <id> É o identificador da réplica a ser conectada"
)


class Replica(rpyc.Service):
    def __init__(self, identifier, procs_lock) -> None:
        self.identifier = identifier
        self.X = 0
        self.primary = 1
        self.history = []
        self.lock = procs_lock
        self.others = dict()
        super().__init__()

    def exposed_get_identifier(self) -> int:
        return self.identifier

    def exposed_get_primary(self) -> int:
        return self.primary

    def exposed_get_X(self) -> int:
        return self.X

    def exposed_set_X(self, X) -> None:
        self.X = X

    def exposed_get_history(self) -> list:
        return self.history

    def exposed_set_primary(self, primary) -> None:
        self.primary = primary

    def exposed_append_history(self, new_x) -> None:
        if self.identifier == self.primary:
            self.history.append((self.identifier, new_x))
        elif len(self.history) > 0 and self.primary == self.history[-1][0]:
            self.history[-1] = (self.primary, new_x)
        else:
            self.history.append((self.primary, new_x))

    def exposed_update_X(self, X) -> None:
        with self.lock:
            if self.identifier == self.primary:
                self.X = X
                self.history.append((self.identifier, X))
                for others in self.others.values():
                    others.root.set_X(X)
                    others.root.append_history(X)
            else:
                self.primary = self.identifier
                self.X = X
                self.history.append((self.identifier, X))
                for others in self.others.values():
                    others.root.set_primary(self.identifier)
                    others.root.set_X(X)
                    others.root.append_history(X)

    def exposed_connect_to_node(self, host, port) -> None:
        self.others[port - 5000] = rpyc.connect(host, port=port)

    def exposed_close_connections(self) -> None:
        for other in self.others.values():
            other.close()
        self.others = dict()


def start_server(id, procs_lock):
    try:
        s = rpyc.utils.server.ThreadedServer(Replica(id, procs_lock), port=id + 5000)
        s.start()
    except OSError:
        print("Erro ao iniciar o servidor")
        print(
            "Caso já haja outra instância do servidor rodando, a opção -c ou --create não deve ser usada"
        )
        sys.exit(1)


def parse(arguments):
    try:
        opts, args = getopt.getopt(arguments, "c", ["create"])
    except getopt.GetoptError:
        print(USAGE)
        end()

    if len(opts) == 0:
        return (False, int(args[0]))
    elif len(opts) == 1 and opts[0][0] == "-c" or opts[0][0] == "--create":
        return (True, int(args[0]))
    else:
        print(USAGE)
        end()


def create_replicas(procs_lock):
    for i in range(1, 5):
        procs.append(multiprocessing.Process(target=start_server, args=(i, procs_lock)))
        procs[i - 1].start()


def make_connections():
    for i in range(1, 5):
        conn = rpyc.connect("localhost", port=i + 5000)
        for j in range(1, 5):
            if i != j:
                conn.root.connect_to_node("localhost", j + 5000)
        conn.close()


def read_X(conn):
    print("O valor de X é: " + str(conn.root.get_X()))


def read_history(conn):
    print("O histórico de alterações é: " + str(conn.root.get_history()))


def update_X(conn, value):
    conn.root.update_X(value)
    print("O valor de X foi atualizado para " + str(value))


def connect_to_replica(id):
    conn = rpyc.connect("localhost", port=id + 5000)
    return conn


def end():
    for proc in procs:
        proc.terminate()

    if len(procs) > 0:
        print("Todos as réplicas foram encerradas!")
        print(
            "Encerre os outros terminais e execute o programa novamente para criar novas réplicas."
        )
    sys.exit(0)


def main():
    procs_lock = multiprocessing.Lock()

    args = sys.argv[1:]
    if not args:
        print(USAGE)
        end()

    (should_create, id) = parse(args)

    if should_create:
        create_replicas(procs_lock)
        make_connections()

    try:
        conn = rpyc.connect("localhost", port=id + 5000)
    except ConnectionRefusedError:
        print("Não foi possível conectar à réplica " + str(id))
        print(
            "Para criar as réplicas permanentes, é preciso executar o comando 'python3 replicas.py -c <id>'"
        )
        end()

    while True:
        print("\n")
        print("Conexão estabelecida com o réplica " + str(id))
        print("Selecione uma opção:")
        print("1. Ler o valor atual de X na réplica")
        print("2. Ler o histórico de alterações do valor de X")
        print("3. Alterar o valor de X")
        print("4. Conectar com outra réplica")
        print("5. Sair")

        opcao = int(input("Opção: "))

        if opcao == 1:
            read_X(conn)
        elif opcao == 2:
            read_history(conn)
        elif opcao == 3:
            value = int(input("Digite o novo valor de X: "))
            update_X(conn, value)
        elif opcao == 4:
            print("Selecione uma réplica (1-4):")
            replica = int(input("Réplica: "))
            conn.close()
            id = replica
            conn = connect_to_replica(replica)
        elif opcao == 5:
            break
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    main()
    end()
