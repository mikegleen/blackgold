"""

"""
from collections import defaultdict
from heapq import *

TRACE = True


def trace(s):
    if TRACE:
        print(s)


def dijkstra(edges, from_node, to_node):
    graph = defaultdict(list)
    for fromnode, tonode, cost in edges:
        graph[fromnode].append((cost, tonode))
    del fromnode, tonode
    node_queue = [(0, from_node, ())]
    seen = set()
    mins = {from_node: 0}
    while node_queue:
        trace(f'{node_queue=}')
        # v1 is the lowest cost node in the queue
        cost, v1, path = heappop(node_queue)
        trace(f'  {cost=}, {v1=}, {path=}')
        if v1 not in seen:
            seen.add(v1)
            trace(f'  {seen=}')
            path: tuple = (v1, path)
            trace(f'  {path=}')
            if v1 == to_node:
                trace(f'returning {cost=}, {path=}')
                return cost, path
            # v2
            for next_step_cost, v2 in graph.get(v1, ()):
                trace(f'    {v2=}, {next_step_cost=}')
                if v2 in seen:
                    trace('    skip')
                    continue
                prev = mins.get(v2, None)
                nextcost = cost + next_step_cost
                trace(f'    {prev=}, {nextcost=}')
                if prev is None or nextcost < prev:
                    trace(f'    mins[{v2}] = {nextcost}, pushing {v2}')
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
    print('edges=', edges)
    print("A -> E:")
    print('result:', dijkstra(edges, "A", "E"))
    # print("F -> G:")
    # print('result:',dijkstra(edges, "F", "G"))


if __name__ == "__main__":
    main()
