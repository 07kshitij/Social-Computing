import sys
import os
import snap
import statistics
from collections import deque

DATA_PATH = 'facebook_combined.txt'

ROOT_PATH = 'centralities'
CLOSENESS_FILE = 'closeness.txt'
BETWEENNESS_FILE = 'betweenness.txt'
PAGERANK_FILE = 'pagerank.txt'

DEBUG = False

class Analyse_Centrality:
    def __init__(self):
        self.graph = self.load_graph()
        if DEBUG and not os.path.exists('analysis'):
            os.makedirs('analysis')

    def load_graph(self):
        graph = snap.LoadEdgeList(snap.PUNGraph, DATA_PATH, 0, 1)
        return graph

    def closeness_centrality(self):
        res = dict()
        for node in self.graph.Nodes():
            closeness = snap.GetClosenessCentr(self.graph, node.GetId())
            res[node.GetId()] = closeness
        order = sorted(res.items(), key=lambda item: item[1], reverse=True)
        order = order[:100]
        snap_nodes = [node[0] for node in order]
        self_nodes = []
        with open(os.path.join(ROOT_PATH, CLOSENESS_FILE), 'r') as readFile:
            for line in readFile.readlines():
                if len(self_nodes) == len(snap_nodes):
                    break
                u, v = line.split()
                u = int(u)
                self_nodes.append(u)
        common = len(set(snap_nodes).intersection(self_nodes))
        print('#overlaps for Closeness Centrality: {}'.format(common))

        if DEBUG:
            with open(os.path.join('analysis', CLOSENESS_FILE), 'w') as file:
                for node in order:
                    file.write('{} {}\n'.format(node[0], res[node[0]]))

    def betweenness_centrality(self):
        Nodes = snap.TIntFltH()
        Edges = snap.TIntPrFltH()
        snap.GetBetweennessCentr(self.graph, Nodes, Edges, 0.8)
        res = dict()
        for node in Nodes:
            res[node] = Nodes[node]
        order = sorted(res.items(), key=lambda item: item[1], reverse=True)
        order = order[:100]
        snap_nodes = [node[0] for node in order]
        self_nodes = []
        with open(os.path.join(ROOT_PATH, BETWEENNESS_FILE), 'r') as readFile:
            for line in readFile.readlines():
                if len(self_nodes) == len(snap_nodes):
                    break
                u, v = line.split()
                u = int(u)
                self_nodes.append(u)
        common = len(set(snap_nodes).intersection(self_nodes))
        print('#overlaps for Betweenness Centrality: {}'.format(common))

        if DEBUG:
            with open(os.path.join('analysis', BETWEENNESS_FILE), 'w') as file:
                for node in order:
                    file.write('{} {}\n'.format(node[0], Nodes[node[0]]))

    def pagerank(self):
        pageRank = snap.TIntFltH()
        snap.GetPageRank(self.graph, pageRank)
        res = dict()
        for node in pageRank:
            res[node] = pageRank[node]
        order = sorted(res.items(), key=lambda item: item[1], reverse=True)
        order = order[:100]
        snap_nodes = [node[0] for node in order]
        self_nodes = []
        with open(os.path.join(ROOT_PATH, PAGERANK_FILE), 'r') as readFile:
            for line in readFile.readlines():
                if len(self_nodes) == len(snap_nodes):
                    break
                u, v = line.split()
                u = int(u)
                self_nodes.append(u)
        common = len(set(snap_nodes).intersection(self_nodes))
        print('#overlaps for PageRank Centrality: {}'.format(common))

        if DEBUG:
            with open(os.path.join('analysis', PAGERANK_FILE), 'w') as file:
                for node in order:
                    file.write('{} {}\n'.format(node[0], pageRank[node[0]]))

if __name__ == "__main__":
    obj = Analyse_Centrality()
    obj.closeness_centrality()
    obj.betweenness_centrality()
    obj.pagerank()
    pass
