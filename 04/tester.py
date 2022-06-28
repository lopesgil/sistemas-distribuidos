import random, multiprocessing, rpyc
from node_rpc import start_server

procs = []  # Lista de processos onde rodam os nós
conns = []  # Conexões dos nós com o processo principal de teste
nodes_id = []  # Ids geradas aleatoriamente para os nós
NUM_OF_NODES = 10  # Quantidade de nós a serem criados


def initialize_nodes():
    for i in range(NUM_OF_NODES):
        nodes_id.append(random.randint(0, 1000))
        # Apenas o identificador é passado, a porta é gerada somando 5000
        procs.append(multiprocessing.Process(target=start_server, args=(nodes_id[i],)))
        procs[i].start()


# Conectar os nós com o processo principal de teste
def connect_to_nodes():
    for i in range(NUM_OF_NODES):
        node_id = nodes_id[i]
        conns.append(rpyc.connect("localhost", port=5000 + node_id))


# Gera as conexões entre os nós
def make_connections():
    remaining = list(range(NUM_OF_NODES))  # índices restantes
    already_connected = random.sample(range(NUM_OF_NODES), 2)  # índices já conectados
    conns[already_connected[0]].root.connect_to_node(
        "localhost", nodes_id[already_connected[1]] + 5000
    )
    conns[already_connected[1]].root.connect_to_node(
        "localhost", nodes_id[already_connected[0]] + 5000
    )
    remaining.remove(already_connected[0])
    remaining.remove(already_connected[1])

    # Garante que o grafo obtido seja conexo, usando as conexões já existentes
    # como base para as seguintes
    for i in remaining:
        # conecta o nó atual a algum dos que já estão no grafo
        node_to_connect = random.randint(0, len(already_connected) - 1)
        conns[i].root.connect_to_node(
            "localhost", nodes_id[already_connected[node_to_connect]] + 5000
        )
        conns[already_connected[node_to_connect]].root.connect_to_node(
            "localhost", nodes_id[i] + 5000
        )
        # adiciona o nó atual à lista de já conectados
        already_connected.append(i)

    for i in range(NUM_OF_NODES):
        print(conns[i].root.get_identifier(), conns[i].root.get_neighbors())


# Teste de eleição
def election_test():
    node_to_start = random.randint(
        0, NUM_OF_NODES - 1
    )  # Define um nó aleatório para iniciar a eleição
    print(
        "Iniciando eleição no nó "
        + str(conns[node_to_start].root.get_identifier())
        + "."
    )
    print("O nó eleito será o que possuir o menor identificador.")
    conns[node_to_start].root.start_election()


# Encerra todas as conexões entre os nós, e posteriormente as conexões com o processo principal
def close_connections():
    for conn in conns:
        conn.root.close_connections()
        conn.close()


# Encerra todos os processos
def terminate_processes():
    for proc in procs:
        proc.terminate()
    for proc in procs:
        proc.join()


def main():
    initialize_nodes()
    connect_to_nodes()
    make_connections()
    election_test()
    input("Pressione 'Enter' para fechar conexões...")
    close_connections()
    terminate_processes()
    print("Feito.")
    input("Pressione 'Enter' para sair...")
    exit(0)


if __name__ == "__main__":
    main()
