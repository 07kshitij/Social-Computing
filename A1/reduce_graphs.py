import sys
import os


def SaveEdgeList(file_name):

    source = ""
    if "facebook" in file_name:
        source = "facebook"
    elif "amazon" in file_name:
        source = "amazon"
    else:
        assert(False)
    if not os.path.exists('subgraphs'):
        os.makedirs('subgraphs')

    final_edges = []

    with open(file_name, 'r') as file:
        graph = file.readlines()
        for edge in graph:
            u, v = map(int, edge.split())
            if source == "facebook":
                if u % 5 and v % 5:
                    final_edges.append((u, v))
            else:
                if not (u % 4 or v % 4):
                    final_edges.append((u, v))

    with open(os.path.join('subgraphs', source + '.elist'), 'w') as file:
        file.write('\n'.join('{} {}'.format(
            node[0], node[1]) for node in final_edges))
    return


if __name__ == "__main__":
    file_name = sys.argv[1]
    SaveEdgeList(file_name)
