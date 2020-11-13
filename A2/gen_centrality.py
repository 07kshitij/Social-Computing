import os
import copy
from collections import deque

DATA_PATH = 'facebook_combined.txt'

ROOT_PATH = 'centralities'
CLOSENESS_FILE = 'closeness.txt'
BETWEENNESS_FILE = 'betweenness.txt'
PAGERANK_FILE = 'pagerank.txt'
INFINITY = 10**9 + 7

''' Class implementing the various centrality metrics 
    - Closeness Centrality, Betweenness Centrality, PageRank '''


class Centrality_Metrics:
    def __init__(self):
        self.graph = self.load_graph()
        self.num_nodes = len(self.graph.keys())

    ''' Add edge from node u to v in the Graph 'graph' '''

    def add_edge(self, graph, u, v):
        try:
            graph[u].append(v)
        except KeyError:
            graph[u] = []
            graph[u].append(v)

    ''' Load facebook_combined.txt to a graph structure '''

    def load_graph(self):
        graph = dict()
        with open(DATA_PATH, 'r') as edge_list:
            for edge in edge_list.readlines():
                u, v = list(map(int, edge.split()))
                self.add_edge(graph, u, v)
                self.add_edge(graph, v, u)
        return graph

    ''' Wrapper method over closeness and betweenness centrality computation
        Computes the centrality measure in the required output format '''

    def centrality(self):
        closeness, betweenness = self.brandes_algorithm()

        # Sort according to centrality values
        sorted_closeness = sorted(
            closeness.items(),   key=lambda item: item[1], reverse=True)
        sorted_betweenness = sorted(
            betweenness.items(), key=lambda item: item[1], reverse=True)

        with open(os.path.join(ROOT_PATH, CLOSENESS_FILE), 'w') as file:
            for key in sorted_closeness:
                file.write("{} {}\n".format(
                    key[0], round(closeness[key[0]], 6)))

        with open(os.path.join(ROOT_PATH, BETWEENNESS_FILE), 'w') as file:
            for key in sorted_betweenness:
                file.write("{} {}\n".format(
                    key[0], round(betweenness[key[0]], 6)))

    ''' Brandes' Algorithm 
        Reference - https://www.cl.cam.ac.uk/teaching/1617/MLRD/handbook/brandes.pdf
        Returns the closenss and betweenness centrality scores for all the nodes in the graph '''

    def brandes_algorithm(self):
        closeness = dict((node, 0) for node in range(self.num_nodes))
        betweenness = dict((node, 0) for node in range(self.num_nodes))

        for src in range(self.num_nodes):
            if len(self.graph[src]) == 0:
                continue
            stack = []
            parent = [[] for node in range(self.num_nodes)]
            sigma = [0 for node in range(self.num_nodes)]
            sigma[src] = 1
            delta = [0 for node in range(self.num_nodes)]
            # Shortest path length vector from all nodes to `src`
            distance = [INFINITY for node in range(self.num_nodes)] 
            distance[src] = 0

            # Breadth First Search from `src`
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
                if node != src and distance[node] != INFINITY:
                    closeness[src] += distance[node]

            # Update betweenness centrality of all nodes in the paths from `src`
            while stack:
                u = stack.pop()
                for v in parent[u]:
                    delta[v] += (sigma[v] / sigma[u]) * (1 + delta[u])
                if u != src:
                    betweenness[u] += delta[u]

        for key in range(self.num_nodes):
            closeness[key] = (self.num_nodes - 1) / closeness[key]
            betweenness[key] *= (2 / ((self.num_nodes - 1)
                                      * (self.num_nodes - 2)))
        return closeness, betweenness

    ''' Approx. L1 norm for pageRank values '''

    def normalize(self, pageRank):
        sum_scores = sum(pageRank)
        pageRank = [value / sum_scores for value in pageRank]
        return pageRank

    ''' Computes the pageRank centrality metric for all nodes using power iteration method '''

    def pagerank(self):
        S = sum([1 for x in range(self.num_nodes) if not (x % 4)])
        degree = [len(self.graph[node]) for node in range(self.num_nodes)]
        # Bias nodes divisble by 4 over others
        prefVector = [1 / S if not (node % 4)
                      else 0 for node in range(self.num_nodes)]
        pageRank = prefVector

        # Error observed to be significantly less for ~ 100 iterations
        num_iterations = 100
        alpha = 0.8

        while num_iterations:

            new_pageRank = copy.deepcopy(pageRank)

            for node in range(self.num_nodes):
                curr_sum = 0
                for v in self.graph[node]:
                    curr_sum += pageRank[v] / degree[v]
                new_pageRank[node] = alpha * curr_sum + (1 - alpha) * prefVector[node]

            pageRank = self.normalize(new_pageRank)

            num_iterations -= 1

        node_pageRank_map = dict()

        # Map scores to a dict for sorting according to pageRank values
        for node in range(self.num_nodes):
            node_pageRank_map[node] = pageRank[node]

        sorted_pagerank = sorted(
            node_pageRank_map.items(), key=lambda item: item[1], reverse=True
        )

        with open(os.path.join(ROOT_PATH, PAGERANK_FILE), 'w') as file:
            for key in sorted_pagerank:
                file.write("{} {}\n".format(
                    key[0], round(node_pageRank_map[key[0]], 6)))


if __name__ == "__main__":

    if not os.path.exists(ROOT_PATH):
        os.makedirs(ROOT_PATH)
    centrality_metrics = Centrality_Metrics()
    centrality_metrics.centrality()
    centrality_metrics.pagerank()
