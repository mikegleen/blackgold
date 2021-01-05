"""

"""
import argparse
from enum import Enum
import heapq
import sys
import time

from .node import Node
from .graph import Graph


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


class PlayerIDs(Enum):
    RED = '-R-'
    TAN = '-T-'
    BLUE = '-B-'
    ORANGE = '-O-'


# hardcode the rows in the first column to place the trucks
TRUCK_INIT_ROWS = [1, 5, 7, 9]


class Game:

    def __init__(self, graph, nplayers):
        lp = list(PlayerIDs)
        self.players = []
        assert nplayers <= len(lp)
        for n in range(nplayers):
            node: Node = graph.board[TRUCK_INIT_ROWS[n]][0]
            player = Player(lp[n], node)
            node.truck = player
            self.players.append(player)


class Player:

    def __init__(self, playerid, truck_node: Node):
        self.id = playerid  # am enum member
        self.truck_node = truck_node
        self.train_col = None
        self.oilrigs = 0
        self.rigs_in_use = []
        self.cash = 15_000
        self.barrels = 0


def read_board(csvfile):
    """
    Each line in the csv file describes one row or one column of the board,
    depending on argument --bycols.
    Lines beginning with '#' and blank lines are ignored.
    Each cell contains:

        <cell> ::= <terrain> | <terrain> "." <oilwell> | "." <oilwell>
        <terrain> ::= 1 | 2 | 3
        <oilwell> ::= <wellcount> | <wellcount> <variant>
        <wellcount> ::= 1 | 2 | 3
        <variant> = "x" | "d"

    If <terrain> is absent, "1" is assumed.
    If <variant> == "x" then this is a cell ignored for 3-person games.
    If <variant> == "d" then this cell contains a derrick (used for testing).

    :param csvfile: The file containing the board as described above.
    :return: A list of rows containing tuples corresponding to the columns.
             Each cell is the string as defined above.
    """
    r = []  # rows
    nrows = 0
    for nline, line in enumerate(csvfile):
        if line.startswith('#'):
            continue
        if len(c := line.split()) == 0:  # one column
            continue
        if nrows == 0:
            nrows = len(c)
        if len(c) != nrows:
            raise ValueError(f"Length of line {nline + 1} is "
                             f"{len(c)}, {nrows} expected.")
        r.append(c)
    if _args.bycols:
        # Invert the array giving a list of tuples where each tuple is one row.
        rawboard = list(zip(*r))
    else:
        rawboard = r
    if _args.verbose >= 2:
        print('rawboard:', rawboard)
    return rawboard


def dijkstra(root: Node, maxcost=sys.maxsize, verbose=1):
    """
    :param root: the Node to start from. The Nodes have been initialized
             during the creation of the Graph instance.
    :param maxcost: Do not search for nodes more than maxcost away.
    :param verbose: the debug level
    :return: The Node's distance field is updated in each instance in the
             board that is reachable from the root node given the game's
             constraints such as within the maximum distance from the root
             where the "distance" is the sum of the costs of entering each
             node depending on the terrain.
    """

    def idist(distance):
        return "∞" if distance == sys.maxsize else distance

    root.distance = 0
    unvisited_queue = [root]
    visited = set()
    goals = set()
    while unvisited_queue:
        # Pops a vertex with the smallest distance
        current = heapq.heappop(unvisited_queue)
        visited.add(current)
        if current.goal:
            goals.add(current)
        trace(3, 'current={} current.adjacent={}', current, current.adjacent)
        if current.distance >= maxcost:
            trace(3, '    stopping at distance {}.', current.distance)
            continue
        for nextn in sorted(current.adjacent):  # iterate over adjacent nodes
            trace(3, 'nextn={} {}', nextn, "DERRICK" if nextn.derrick else "")
            if nextn in visited:  # if visited, skip
                trace(3, 'skipping, visited: nextn={}', nextn)
                continue
            if nextn.derrick:
                trace(3, 'skipping, derrick: nextn={}', nextn)
                continue
            new_dist = current.distance + nextn.terrain
            nextn_dist = nextn.distance
            #
            # If the next node has wells, the player may not stop there.
            if nextn.wells and new_dist >= maxcost:
                trace(3, 'skipping, wells: nextn={}', nextn)
                continue
            if new_dist < nextn_dist and new_dist <= maxcost:
                nextn.distance = new_dist
                nextn.previous = current
                heapq.heappush(unvisited_queue, nextn)
                updated = 'updated'  # just used for logging
            else:
                updated = 'not updated'
            if verbose >= 3:
                # print('%s : current = %s next = %s new_dist = %s'
                #       % (updated, current.id, nextn.id, nextn_dist))
                print(f'{updated}: current: {current.id}, next: {nextn.id}, '
                      f'dist: {idist(nextn_dist)} -> {nextn.distance}')
        trace(3, 'unvisited: {}', unvisited_queue)
    goals = sorted(list(goals), key=lambda node: node.col, reverse=True)
    return goals


def main(args):
    rawboard = read_board(args.incsv)
    graph = Graph(rawboard, args.nplayers)
    graph.dump_raw_board(args.dumprawboard)
    if args.verbose >= 3:
        graph.dump_board()
    nrows, ncols = graph.get_rows_cols()
    if args.verbose >= 1:
        m = args.maxcost
        print(f'{nrows=} {ncols=}'
              f'{" maxcost=" + str(m) if m < sys.maxsize else ""}')
    if args.timeit:
        t1 = time.time()
        for _ in range(args.timeit):
            graph.reset_distance()
            dijkstra(graph.board[args.row][args.column],
                     maxcost=args.maxcost, verbose=_args.verbose)
        t2 = time.time()
        print(t2 - t1)
    else:
        graph.reset_distance()
        goals = dijkstra(graph.board[args.row][args.column],
                         maxcost=args.maxcost, verbose=_args.verbose)
        print(f'{goals=}')
    if args.verbose >= 2:
        graph.dump_board()
    # print(board)
    if args.print:
        graph.print_board()


def getargs():
    parser = argparse.ArgumentParser(
        description='''
        Play the game giganten.
        ''')
    parser.add_argument('incsv', type=argparse.FileType('r'), help='''
         The file containing the board description.''')
    parser.add_argument('--bycols', action='store_true', help='''
    The input CSV file contains data by columns and needs to be flipped.
    ''')
    parser.add_argument('-c', '--column', type=int, default=0, help='''
    Start column.
    ''')
    parser.add_argument('--dumprawboard', help='''
    Specify the file to dump the raw board to.
    ''')
    parser.add_argument('-m', '--maxcost', type=int, default=sys.maxsize,
                        help='''
    Maximum distance of interest.
    ''')
    parser.add_argument('-n', '--nplayers', default=4, type=int, help='''
    Specify the number of players; the default is 4.
    ''')
    parser.add_argument('-p', '--print', action='store_true', help='''
    Print the finished board with distances.
    ''')
    parser.add_argument('-r', '--row', type=int, default=0, help='''
    Start row.
    ''')
    parser.add_argument('-t', '--timeit', type=int, help='''
    Time the dijkstra function with this number of iterations.
    ''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
    Modify verbosity.
    ''')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 8)
    _args = getargs()
    if _args.verbose > 1:
        print(f'verbosity: {_args.verbose}')
    main(_args)
    print('End giganten.')
