"""

"""
from collections import defaultdict
from heapq import *


def dijkstra(edges, from_node, to_node):
    graph = defaultdict(list)
    for fromnode, tonode, cost in edges:
        graph[fromnode].append((cost, tonode))
    del fromnode, tonode
    node_queue = [(0, from_node, ())]
    seen = set()
    mins = {from_node: 0}
    while node_queue:
        # print(f'{node_queue=}')
        cost, v1, path = heappop(node_queue)
        # print(f'{cost=}, {v1=}, {path=}')
        if v1 not in seen:
            seen.add(v1)
            # print(f'{seen=}')
            path: tuple = (v1, path)
            if v1 == to_node:
                return cost, path

            for c, v2 in graph.get(v1, ()):
                if v2 in seen:
                    continue
                prev = mins.get(v2, None)
                nextcost = cost + c
                if prev is None or nextcost < prev:
                    mins[v2] = nextcost
                    heappush(node_queue, (nextcost, v2, path))

    return float("inf")


def main():
    edges = [
        ("A", "B", 7),
        ("A", "D", 5),
        ("B", "C", 8),
        ("B", "D", 9),
        ("B", "E", 7),
        ("C", "E", 5),
        ("D", "E", 15),
        ("D", "F", 6),
        ("E", "F", 8),
        ("E", "G", 9),
        ("F", "G", 11)
    ]

    print("=== Dijkstra ===")
    print(edges)
    print("A -> E:")
    print(dijkstra(edges, "A", "E"))
    print("F -> G:")
    print(dijkstra(edges, "F", "G"))


if __name__ == "__main__":
    main()
