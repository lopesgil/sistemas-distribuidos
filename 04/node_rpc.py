import rpyc


class Node(rpyc.Service):
    def __init__(self, identifier) -> None:
        self.identifier = identifier
        self.lowest_identifier = self.identifier
        self.port = self.identifier + 5000
        self.neighbors = dict()
        self.status = "standby"
        self.parent = None
        self.to_wait = -1
        self.acks = -1
        super().__init__()

    def exposed_connect_to_node(self, host, port) -> None:
        # Armazena as conexões num dicionário indexado pelo identificador do nó
        self.neighbors[port - 5000] = rpyc.connect(host, port=port)

    def exposed_get_port(self) -> int:
        return self.port

    def exposed_get_identifier(self) -> int:
        return self.identifier

    def exposed_get_neighbors(self) -> list:
        return list(self.neighbors.keys())

    def exposed_start_election(self) -> None:
        self.status = "election"
        self.to_wait = 0
        self.acks = 0
        for neighbor in self.neighbors.values():
            rpyc.async_(neighbor.root.probe)(self.identifier)

    def exposed_echo(self, lowest_identifier) -> None:
        self.to_wait -= 1
        # atualiza o identificador mais baixo até agora
        if self.lowest_identifier > lowest_identifier:
            self.lowest_identifier = lowest_identifier

        # Se já recebeu todos os echos esperados, passa o echo acima
        if (
            self.status != "election"
            and self.to_wait == 0
            and self.acks == len(self.neighbors) - 1
        ):
            self.status = "echo"
            self.acks = 0
            self.to_wait = 0
            rpyc.async_(self.parent.root.echo)(self.lowest_identifier)

        # Se também é o nó que iniciou a eleição, exibe o resultado
        if (
            self.status == "election"
            and self.to_wait == 0
            and self.acks == len(self.neighbors)
        ):
            print("Eleição encerrada.")
            print("Nó eleito: " + str(self.lowest_identifier))

    def exposed_ack(self, will_echo=False) -> None:
        self.acks += 1
        # Se é nó pai, atualiza o contador de echos esperados
        if will_echo:
            self.to_wait += 1

        # Se não é nó pai e todos os acks foram recebidos, passa o echo acima
        if self.acks == len(self.neighbors) - 1 and self.to_wait == 0:
            self.status = "echo"
            self.acks = 0
            self.to_wait = 0
            rpyc.async_(self.parent.root.echo)(self.lowest_identifier)

    def exposed_probe(self, identifier) -> None:
        # Se ainda não recebeu probe, define o nó pai como o nó que enviou o probe
        # e passa o probe abaixo
        if self.status == "standby":
            self.status = "probe"
            self.to_wait = 0
            self.acks = 0
            self.parent = self.neighbors[identifier]
            rpyc.async_(self.parent.root.ack)(will_echo=True)
            for neighbor in self.neighbors.values():
                if neighbor != self.parent:
                    rpyc.async_(neighbor.root.probe)(self.identifier)
            # Se só possui o pai de vizinho, passa o echo acima
            if len(self.neighbors) == 1:
                self.status = "echo"
                self.acks = 0
                self.to_wait = 0
                rpyc.async_(self.parent.root.echo)(self.identifier)
        else:
            # Caso já tenha recebido probe antes, apenas passa o ack
            rpyc.async_(self.neighbors[identifier].root.ack)()

    def exposed_close_connections(self) -> None:
        for neighbor in self.neighbors.values():
            neighbor.close()
        self.neighbors = dict()


def start_server(identifier):
    s = rpyc.utils.server.ThreadedServer(Node(identifier), port=5000 + identifier)
    s.start()
