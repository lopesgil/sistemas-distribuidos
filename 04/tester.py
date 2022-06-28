import random, multiprocessing, rpyc
from node_rpc import start_server
from rpyc.utils.server import ForkingServer

procs = []
conns = []
nodes_id = []
NUM_OF_NODES = 10


def initialize_nodes():
    for i in range(NUM_OF_NODES):
        nodes_id.append(random.randint(0, 1000))
        procs.append(multiprocessing.Process(target=start_server, args=(nodes_id[i],)))
        procs[i].start()


def connect_to_nodes():
    for i in range(NUM_OF_NODES):
        node_id = nodes_id[i]
        conns.append(rpyc.connect("localhost", port=5000 + node_id))


def make_connections():
    already_connected = [0, 1]
    conns[0].root.connect_to_node("localhost", nodes_id[1] + 5000)
    conns[1].root.connect_to_node("localhost", nodes_id[0] + 5000)

    for i in range(2, NUM_OF_NODES):
        node_to_connect = random.randint(0, len(already_connected) - 1)
        conns[i].root.connect_to_node("localhost", nodes_id[node_to_connect] + 5000)
        conns[node_to_connect].root.connect_to_node("localhost", nodes_id[i] + 5000)

    for i in range(NUM_OF_NODES):
        print(conns[i].root.get_identifier(), conns[i].root.get_neighbors())


def election_test():
    node_to_start = random.randint(0, NUM_OF_NODES - 1)
    print(
        "Iniciando eleição no nó "
        + str(conns[node_to_start].root.get_identifier())
        + "."
    )
    print("O nó eleito será o que possuir o menor identificador.")
    conns[node_to_start].root.start_election()


def close_connections():
    for conn in conns:
        conn.root.close_connections()
        conn.close()


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
