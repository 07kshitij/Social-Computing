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
INFINITY = 10 ** 9

class Centrality_Metrics:
    def __init__(self):
        self.graph = self.load_graph()
        self.num_nodes = len(self.graph.keys())

    def add_edge(self, graph, u, v):
        try:
            graph[u].append(v)
        except KeyError:
            graph[u] = []
            graph[u].append(v)

    def load_graph(self):
        graph = dict()
        with open(DATA_PATH, 'r') as edge_list:
            for edge in edge_list.readlines():
                u, v = list(map(int, edge.split()))
                self.add_edge(graph, u, v)
                self.add_edge(graph, v, u)
        return graph

    def centrality(self):
        closeness, betweenness = self.brandes_algorithm()
        sorted_closeness = sorted(
            closeness.items(),   key=lambda item: item[1], reverse=True)
        sorted_betweenness = sorted(
            betweenness.items(), key=lambda item: item[1], reverse=True)

        with open(os.path.join(ROOT_PATH, CLOSENESS_FILE), 'w') as file:
            for key in sorted_closeness:
                file.write("{} {}\n".format(key[0], closeness[key[0]]))

        with open(os.path.join(ROOT_PATH, BETWEENNESS_FILE), 'w') as file:
            for key in sorted_betweenness:
                file.write("{} {}\n".format(key[0], betweenness[key[0]]))

    # https://www.cl.cam.ac.uk/teaching/1617/MLRD/handbook/brandes.pdf
    def brandes_algorithm(self):
        closeness = dict((node, 0) for node in range(self.num_nodes))
        betweenness = dict((node, 0) for node in range(self.num_nodes))
        steps = 0
        for src in range(self.num_nodes):
            if len(self.graph[src]) == 0:
                continue
            stack = []
            parent = [[] for node in range(self.num_nodes)]
            sigma = [0 for node in range(self.num_nodes)]
            sigma[src] = 1
            delta = [0 for node in range(self.num_nodes)]
            distance = [INFINITY for node in range(self.num_nodes)]
            distance[src] = 0
            queue = deque([])
            queue.append(src)
            while queue:
                u = queue.popleft()
                stack.append(u)
                for v in self.graph[u]:
                    if distance[v] == INFINITY:
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

    def normalize(self, pageRank):
        sum_scores = sum(pageRank)
        pageRank = [value / sum_scores for value in pageRank]
        return pageRank

    def pagerank(self):
        S = sum([1 for x in self.graph.keys() if not (x % 4)])
        degree = [len(self.graph[node]) for node in range(self.num_nodes)]
        prefVector = [1 / S if not (node % 4) else 0 for node in range(self.num_nodes)]
        pageRank = prefVector

        num_iterations = 100
        alpha = 0.8

        while num_iterations:

            for node in range(self.num_nodes):
                if len(self.graph[node]) == 0:
                    continue
                curr_sum = 0
                for v in self.graph[node]:
                    curr_sum += pageRank[v] / degree[v]
                pageRank[node] = alpha * curr_sum + (1 - alpha) * prefVector[node]

            pageRank = self.normalize(pageRank)

            num_iterations -= 1

        pageRank_scores = dict()

        for node in self.graph.keys():
            pageRank_scores[node] = pageRank[node]

        sorted_pagerank = sorted(
            pageRank_scores.items(), key=lambda item: item[1], reverse=True
        )

        with open(os.path.join(ROOT_PATH, PAGERANK_FILE), 'w') as file:
            for key in sorted_pagerank:
                file.write("{} {}\n".format(key[0], pageRank_scores[key[0]]))

if __name__ == "__main__":
    if not os.path.exists(ROOT_PATH):
        os.makedirs(ROOT_PATH)
    obj = Centrality_Metrics()
    obj.centrality()
    obj.pagerank()
    pass
