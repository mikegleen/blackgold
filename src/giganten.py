"""

"""
import argparse
import heapq
import re
import sys

import numpy as np


class Node:
    """
    cost: Number of movement points it costs to enter this node.
    exhausted: True if a derrick has been built and all of the oil has been extracted.
    goal: True if a neighbor is an oil well; changes to False if a derrick is built
    """
    #

    def set_neighbors(self, nodes):
        """
        neighbors contains a priority queue of tuples of (cost, row, column)
        A node can have up to 4 neighbors, reduced if it is on an edge.
        Although the cost can be obtained from nodes[row, column].cost, it is
        included in the tuple as the priority value.
        :return:
        """
        def set1neighbor(nrow, ncol):
            """
            :param nrow: neighbor row
            :param ncol: neighbor column
            :return: None; the neighbor is added to the list
            """
            neighbor = nodes[nrow, ncol]
            cost = neighbor.terrain
            # heapq.heappush(self.neighbors, (cost, nrow, ncol))
            heapq.heappush(self.neighbors, neighbor)
            # If the neighbor has wells, you aren't allowed to stop there,
            # so it can't be a goal.
            if neighbor.wells == 0:
                neighbor.goal |= self.wells > 0

        rows, cols = nodes.shape
        if self.row > 0:
            set1neighbor(self.row - 1, self.col)
        if self.col > 0:
            set1neighbor(self.row, self.col - 1)
        if self.row < rows - 1:
            set1neighbor(self.row + 1, self.col)
        if self.col < cols - 1:
            set1neighbor(self.row, self.col + 1)

    def add_derrick(self):
        # Make the neighbors not to be goals.
        # Make this node impassable
        pass

    def remove_derrick(self):
        # Make this node passable
        pass

    def __init__(self, row, col):
        self.row: int = row
        self.col: int = col
        self.terrain: int = 0
        self.wells: int = 0
        self.exhausted: bool = False
        self.goal: bool = False
        self.derrick: bool = False
        self.neighbors = []  # a priority queue
        self.totalcost: int = sys.maxsize
        self.previousnode = -1  # will be set when visited

    def __str__(self):
        e = 'T' if self.exhausted else 'F'
        g = 'T' if self.goal else 'F'
        d = 'T' if self.derrick else 'F'
        s = f'node[{self.row},{self.col}] terrain: {self.terrain}, '
        # s += f'wells: {self.wells} '
        # s += f'exhausted: {e}, goal: {g}, derrick: {d}, '
        # s += f'totcost: {"∞" if self.totalcost == sys.maxsize else self.totalcost}, '
        # s += f'neighbors: {sorted(self.neighbors)}'

        s = f'n[{self.row},{self.col}] t: {self.terrain}, '
        s += f'w: {self.wells} '
        s += f'ex: {e}, goal: {g}, derrick: {d}, '
        s += f'tot: {"∞" if self.totalcost == sys.maxsize else self.totalcost}, '
        s += f'neighbors: {sorted(self.neighbors)}'
        return s

    def __repr__(self):
        s = f'n[{self.row},{self.col}].t: {self.terrain}'
        return s

    def __lt__(self, other):
        return self.terrain < other.terrain


class Graph:
    board = None


def create_board(csvfile, nplayers):
    """
    Each line in the csv file contains one column of the board. (It was easier
    to type this way)
    :param csvfile: The file contains a description of the board. Each cell
    contains:

        <cell> ::= <terrain> | <terrain> "." <oilwell> | "." <oilwell>
        <terrain> ::= 1 | 2 | 3
        <oilwell> ::= <wellcount> | <wellcount> <3-player marker>
        <wellcount> ::= 1 | 2 | 3
        <3-player marker> = "x"

    If <terrain> is absent, "1" is assumed.

    :param nplayers: If equals 3, exclude wells from cells with a trailing "x".
    :return: An array of Node instances
    """
    r = []  # rows
    ncols = 0
    for nline, line in enumerate(csvfile):
        nline += 1
        c = line.strip().split(',')
        if ncols == 0:
            ncols = len(c)
        if len(c) != ncols:
            raise ValueError(f"Length of line {nline + 1} is {len(c)}, {ncols} expected.")
        r.append(c)
    # board = list(map(list, zip(*board)))  # create list of lists, not tuples
    rawboard = list(zip(*r))  # invert the array giving a list of tuples
    if _args.verbose >= 2:
        print(rawboard)
    three_players = nplayers == 3
    nrows = len(rawboard)
    ncols = len(rawboard[0])
    nodes = [[Node(r, c) for c in range(ncols)] for r in range(nrows)]
    nodes = np.array(nodes)
    for r, row in enumerate(nodes):
        for c, node in enumerate(row):
            m = re.match(r'(\d?)(\.(\d)(x?))?', cell := rawboard[r][c])
            if m is None:
                raise ValueError(f"In row {r}, col {c}, '{cell}' failed match.")
            node.terrain = 1 if m.group(1) == '' else int(m.group(1))
            if m.group(3):  # if wells are specified
                node.wells = 0 if (m.group(4) == 'x' and three_players
                                   ) else int(m.group(3))
    for r in nodes:
        for node in r:
            node.set_neighbors(nodes)
    return nodes


def main(args):
    Graph.board = create_board(args.incsv, 4)
    rows, cols = Graph.board.shape
    if _args.verbose >= 1:
        print(f'{rows=} {cols=}')
    if _args.verbose >= 2:
        for row in range(rows):
            for col in range(cols):
                print(Graph.board[row, col])

    # print(board)


def getargs():
    parser = argparse.ArgumentParser(
        description='''
        Play the game giganten.
        ''')
    parser.add_argument('incsv', type=argparse.FileType('r'), help='''
         The file containing the board description.''')
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
