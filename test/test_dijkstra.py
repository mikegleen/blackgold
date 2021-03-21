"""

"""
from collections import namedtuple
import time


GSite = namedtuple('GSite', 'wellsq goalsq')


def goals_on_path(goal_node):
    """
    goal node: a node next to a node that is a potential drill site.
    Return a list of goal nodes on the path to this goal node, including this
    node.
    Each list entry is a tuple containing the node with wells and the node on
    our path to stop at in order to drill there.

    """
    ret = []
    node = goal_node
    while node:
        for n in node.adjacent:
            if n.wells:
                ret.append(GSite(n, node))
        node = node.previous
        # If the node has wells, we're not allowed to stop there.
        while node and node.wells:
            node = node.previous
    print(repr(goal_node), ret)
    return ret


def time_dijkstra(graph, dijkstra, _args):
    """
    Called if the --timeit command-line option is selected.
    @param graph:
    @return: None
    """
    t1 = time.time()
    for _ in range(_args.timeit):
        graph.reset_graph()
        dijkstra(graph, graph.board[_args.row][_args.column],
                 maxcost=_args.maxcost, verbose=_args.verbose)
    t2 = time.time()
    print(t2 - t1)


def one_dijkstra(graph, dijkstra, _args, _verbose):
    """
    Called if --dijkstra is selected on the command line.
    @param graph:
    @return: dict of drill sites on the path to our goal
    """
    goals = dijkstra(graph, graph.board[_args.row][_args.column],
                     maxcost=_args.maxcost, verbose=_args.verbose)
    # print(goals[1])
    gsites = {g: goals_on_path(g) for g in goals[1]}
    if _verbose >= 2:
        print(f'{goals=}')
        print(f'{gsites=}')
    return gsites


