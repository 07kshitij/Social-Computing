import sys
import os
import snap
import statistics
# import time
# start_time = time.time()

global Rnd


def get_edge_file_path(file_name):
    return os.path.join("subgraphs", file_name)


def check_existance(file_name):
    return os.path.exists(file_name)


def remove_file(file_name):
    os.remove(file_name)


def rename_file(old_name, new_name):
    os.rename(old_name, new_name)


def save_plot(ftype, file_name, prefix):
    plot_file = '{}_{}.elist.png'.format(prefix, file_name)
    if check_existance(plot_file):
        remove_file(plot_file)
    rename_file('{}.{}.png'.format(ftype, file_name), plot_file)

    if check_existance(os.path.join('plots', plot_file)):
        remove_file(os.path.join('plots', plot_file))

    rename_file(plot_file, os.path.join('plots', plot_file))

def get_full_diameter(graph, N):
    full_diameter = snap.GetBfsFullDiam(graph, N, False)
    print('Approximate full diameter by sampling {} nodes: {}'
        .format(N, round(full_diameter, 4)))
    return full_diameter

def get_effective_diameter(graph, N):
    effective_diameter = snap.GetBfsEffDiam(graph, N, False)
    print('Approximate effective diameter by sampling {} nodes: {}'
        .format(N, round(effective_diameter, 4)))
    return effective_diameter

def network_size(graph):
    print('Number of nodes: {}'.format(graph.GetNodes()))
    print('Number of edges: {}'.format(graph.GetEdges()))

def degree_characteristics(graph, root_file, file_name):
    degree_required = 7
    print('Number of nodes with degree={}: {}'.format(
        degree_required, snap.CntDegNodes(graph, degree_required)))

    DegV = snap.TIntPrV()
    snap.GetNodeInDegV(graph, DegV)

    maxDegree = max([node.GetVal2() for node in DegV])
    nodesMaxDegree = [node.GetVal1()
                      for node in DegV if node.GetVal2() == maxDegree]
    nodesMaxDegree.sort()

    print('Node id(s) with highest degree: {}'.format(
        ", ".join([str(node) for node in nodesMaxDegree])))

    snap.PlotInDegDistr(graph, '{}'.format(root_file),
                        '{} - Degree Distribution'.format(file_name))

    save_plot('inDeg', root_file, 'deg_dist')

def path_characteristics(graph, root_file, file_name):
    full_diameters = []
    full_diameters.append(get_full_diameter(graph, 10))
    full_diameters.append(get_full_diameter(graph, 100))
    full_diameters.append(get_full_diameter(graph, 1000))

    print('Approximate full diameter (mean and variance): {}, {}'
        .format(
            round(statistics.mean(full_diameters), 4), 
            round(statistics.variance(full_diameters), 4)))

    eff_diameters = []
    eff_diameters.append(get_effective_diameter(graph, 10))
    eff_diameters.append(get_effective_diameter(graph, 100))
    eff_diameters.append(get_effective_diameter(graph, 1000))

    print('Approximate effective diameter (mean and variance): {}, {}'
        .format(
            round(statistics.mean(eff_diameters), 4), 
            round(statistics.variance(eff_diameters), 4)))

    snap.PlotShortPathDistr(graph, '{}'.format(root_file), 
                                '{} - Shortest Path Distribution'.format(file_name))

    save_plot('diam', root_file, 'shortest_path')

def graph_connectivity(graph, root_file, file_name):
    print('Fraction of nodes in largest connected component: {}'
        .format(round(snap.GetMxSccSz(graph), 4)))

    edge_bridges = snap.TIntPrV()
    snap.GetEdgeBridges(graph, edge_bridges)
    print('Number of edge bridges: {}'.format(len(edge_bridges)))

    articulation_points = snap.TIntV()
    snap.GetArtPoints(graph, articulation_points)
    print('Number of articulation points: {}'.format(len(articulation_points)))

    snap.PlotSccDistr(graph, '{}'.format(root_file),
                            '{} - Connected Component Sizes Distribution'.format(file_name))

    save_plot('scc', root_file, 'connected_comp')

def clustering_characteristics(graph, root_file, file_name):
    clustering_coeff = snap.GetClustCf(graph, -1)
    print('Average clustering coefficient: {}'.format(round(clustering_coeff, 4)))

    triads = snap.GetTriads(graph, -1)
    print('Number of triads: {}'.format(triads))

    node = graph.GetRndNId(Rnd)
    rnd_clustering_coeff = snap.GetNodeClustCf(graph, node)
    print('Clustering coefficient of random node {}: {}'.format(node, round(rnd_clustering_coeff, 4)))

    node = graph.GetRndNId(Rnd)
    rnd_triads = snap.GetNodeTriads(graph, node)
    print('Number of triads random node {} participates: {}'.format(node, rnd_triads))

    min_one_triad = snap.GetTriadEdges(graph, -1)
    print('Number of edges that participate in at least one triad: {}'.format(min_one_triad))

    snap.PlotClustCf(graph, '{}'.format(root_file),
                        '{} - Clustering Coefficient Distribution'.format(file_name))

    save_plot('ccf', root_file, 'clustering_coeff')

def gen_structure(file_name):

    root_file = ""
    if "facebook" in file_name:
        root_file = "facebook"
    elif "amazon" in file_name:
        root_file = "amazon"
    else:
        root_file = "undefined"

    file_name = get_edge_file_path(file_name)

    graph = snap.TUNGraph.New()

    with open(file_name, 'r') as file:
        __graph = file.readlines()
        for edge in __graph:
            u, v = map(int, edge.split())
            if not graph.IsNode(u):
                graph.AddNode(u)
            if not graph.IsNode(v):
                graph.AddNode(v)
            graph.AddEdge(u, v)

    # Create a plots folder if already not present
    if not os.path.exists("plots"):
        os.makedirs("plots")

    # --- Size of Network ---

    network_size(graph)

    # --- Degree of nodes in the network ---

    degree_characteristics(graph, root_file, file_name)

    # --- Paths in the network ---

    path_characteristics(graph, root_file, file_name)

    # --- Components of the network ---
    # For an Undirected Graph Strongly Connected = Weakly Connected

    graph_connectivity(graph, root_file, file_name)

    # --- Connectivity and clustering in the network ---

    clustering_characteristics(graph, root_file, file_name)

if __name__ == "__main__":
    Rnd = snap.TRnd(42)
    Rnd.Randomize()
    file_name = sys.argv[1]
    gen_structure(file_name)
    # print("--- {} seconds ---".format(time.time() - start_time))
