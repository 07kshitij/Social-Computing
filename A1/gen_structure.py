import sys
import os

def get_file_path(file_name):
    return os.path.join('subgraphs', file_name)

def gen_structure(file_name):
    file_name = get_file_path(file_name)

    nodes = set()
    total_edges = 0

    with open(file_name, 'r') as file:
        graph = file.readlines()
        for edge in graph:
            u, v = map(int, edge.split())
            nodes.add(u)
            nodes.add(v)
            total_edges += 1

    total_nodes = len(nodes)

    print('Number of nodes: {}'.format(total_nodes))
    print('Number of edges: {}'.format(total_edges))

if __name__ == "__main__":
    file_name = sys.argv[1]
    gen_structure(file_name)