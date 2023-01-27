"""

"""
from collections import namedtuple
import time


GSite = namedtuple('GSite', 'wellnode goalnode')


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
        for adj in node.adjacent:
            if adj.wells:
                ret.append(GSite(adj, node))
        node = node.previous
        # If the node has wells, we're not allowed to stop there.
        while node and node.wells:
            node = node.previous
    # print('goals_on_path:', repr(goal_node), ret)
    return ret


def time_dijkstra(graph, dijkstra, _args):
    """
    Called if the --timeit command-line option is selected.
    @param graph:
    @param dijkstra: function to call
    @param _args: argparse args
    @return: None
    """
    t0 = time.time()
    for _ in range(_args.timeit):
        graph.reset_graph()
    t1 = time.time()
    for _ in range(_args.timeit):
        graph.reset_graph()
        dijkstra(graph, graph.board[_args.row][_args.column],
                 maxcost=_args.maxcost, verbose=_args.verbose)
    t2 = time.time()
    reset_time = t1 - t0
    elapsed = t2 - t1
    elapsed_dijkstra = elapsed - reset_time
    ms_per_iteration = elapsed_dijkstra * 1000. / _args.timeit
    print(f'{_args.timeit} iterations.')
    print(f'Total elapsed: {elapsed:4.3f} seconds')
    print(f'Total reset time: {reset_time:4.3f} seconds')
    print(f'Time per iteration: {ms_per_iteration:6.2} MS')


def one_dijkstra(graph, dijkstra, args, verbose):
    """
    Called if --dijkstra is selected on the command line.
    @param graph: Graph instance
    @param dijkstra: function to call
    @param args: argparse arguguments
    @param verbose: verbosity
    @return: dict of drill sites on the path to our goal
    """
    visited, goals = dijkstra(graph, graph.board[args.row][args.column],
                              maxcost=args.maxcost, verbose=args.verbose)
    # print(goals[1])
    if verbose >= 2:
        print(f'{type(goals)=} {len(goals)} goals found.')
        for g in goals:
            # print(type(goals[g]), goals[g].id)
            print(type(g))
        # print(f'{goals=}')
    gsites = {g: goals_on_path(g) for g in goals}
    if verbose >= 2:
        print(f'{type(gsites)=}')
        for g in gsites:
            print(type(g), g.id, g.goal, [(gg.wellnode.id, gg.goalnode.id) for gg in gsites[g]])
        # print(f'{gsites=}')
    return gsites
