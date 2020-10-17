import sys
import os
import snap
import statistics
from collections import deque

DATA_PATH = 'facebook_combined.txt'


class Centrality_Metrics:
    def __init__(self):
        self.graph = self.load_graph()
        self.num_nodes = len(self.graph.keys())
        if not os.path.exists('centralities'):
            os.makedirs('centralities')

    def add_edge(self, graph, u, v):
        try:
            graph[u].append(v)
        except KeyError:
            graph[u] = []
            graph[u].append(v)

    def load_graph(self):
        graph = dict()
        with open(DATA_PATH, 'r') as edgeList:
            for edge in edgeList.readlines():
                u, v = list(map(int, edge.split()))
                self.add_edge(graph, u, v)
                self.add_edge(graph, v, u)
        return graph

    def closeness_centrality(self):
        closeness, betweenness = self.Brandes()
        sorted_closeness = sorted(
            closeness.items(),   key=lambda item: item[1], reverse=True)
        sorted_betweenness = sorted(
            betweenness.items(), key=lambda item: item[1], reverse=True)

        with open(os.path.join('centralities', 'closeness.txt'), 'w') as file:
            for key in sorted_closeness:
                file.write("{} {}\n".format(key[0], closeness[key[0]]))

        with open(os.path.join('centralities', 'betweenness.txt'), 'w') as file:
            for key in sorted_betweenness:
                file.write("{} {}\n".format(key[0], betweenness[key[0]]))
        return

    # https://www.cl.cam.ac.uk/teaching/1617/MLRD/handbook/brandes.pdf
    def Brandes(self):
        closeness = dict((node, 0) for node in range(self.num_nodes))
        betweenness = dict((node, 0) for node in range(self.num_nodes))
        steps = 0
        for src in range(self.num_nodes):
            stack = []
            parent = [[] for node in range(self.num_nodes)]
            sigma = [0 for node in range(self.num_nodes)]
            sigma[src] = 1
            delta = [0 for node in range(self.num_nodes)]
            distance = [10 ** 9 for node in range(self.num_nodes)]
            distance[src] = 0
            queue = deque([])
            queue.append(src)
            while queue:
                u = queue.popleft()
                stack.append(u)
                for v in self.graph[u]:
                    if distance[v] == 10 ** 9:
                        distance[v] = distance[u] + 1
                        queue.append(v)
                    if distance[v] == distance[u] + 1:
                        sigma[v] += sigma[u]
                        parent[v].append(u)
            for node in range(self.num_nodes):
                if node != src:
                    closeness[src] += 1 / distance[node]
            while stack:
                u = stack.pop()
                for v in parent[u]:
                    delta[v] += (sigma[v] / sigma[u]) * (1 + delta[u])
                if u != src:
                    betweenness[u] += delta[u]
            steps += 1
            if steps % 100 == 0:
                print("Steps done: {}".format(steps))
        for key in range(self.num_nodes):
            closeness[key] *= 1 / (self.num_nodes - 1)
            betweenness[key] *= (2 / ((self.num_nodes - 1)
                                      * (self.num_nodes - 2)))
        return closeness, betweenness


if __name__ == "__main__":
    obj = Centrality_Metrics()
    obj.closeness_centrality()
    pass
