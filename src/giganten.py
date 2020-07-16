"""

"""
import argparse
import heapq
import re
import sys


class Node:
    """
    cost: Number of movement points it costs to enter this node.
    exhausted: True if a derrick has been built and all of the oil has been extracted.
    goal: True if a neighbor is an oil well; changes to False if a derrick is built
    """
    #

    def set_neighbors(self, nodes):
        """
        adjacent contains a priority queue of tuples of (terrain, row, column)
        A node can have up to 4 adjacent, reduced if it is on an edge.
        Although the terrain can be obtained from nodes[row, column].terrain,
        it is included in the tuple as the priority value.
        :return: None. The adjacent list in all nodes are set.
        """
        def set1neighbor(nrow, ncol):
            """
            :param nrow: neighbor row
            :param ncol: neighbor column
            :return: None; the neighbor is added to the list
            """
            neighbor = nodes[nrow][ncol]
            cost = neighbor.terrain
            # heapq.heappush(self.adjacent, (cost, nrow, ncol))
            heapq.heappush(self.adjacent, neighbor)
            # If the neighbor has wells, you aren't allowed to stop there,
            # so it can't be a goal.
            if neighbor.wells == 0:
                neighbor.goal |= self.wells > 0

        lastrow = len(nodes) - 1
        lastcol = len(nodes[0]) - 1
        if self.row > 0:
            set1neighbor(self.row - 1, self.col)
        if self.col > 0:
            set1neighbor(self.row, self.col - 1)
        if self.row < lastrow:
            set1neighbor(self.row + 1, self.col)
        if self.col < lastcol:
            set1neighbor(self.row, self.col + 1)

    def add_derrick(self):
        # Make the adjacent not to be goals.
        # Make this node impassable
        pass

    def remove_derrick(self):
        # Make this node passable
        pass

    def print_path(self):
        nextprev = self.previous
        path = []
        while nextprev:
            # print(f'nextprev: {nextprev}')
            path.append(nextprev)
            nextprev = nextprev.previous
        path.reverse()
        print('   ', path)

    def __init__(self, row, col):
        self.row: int = row
        self.col: int = col
        self.id: str = f'[{row},{col}]'
        self.terrain: int = 0
        self.wells: int = 0
        self.exhausted: bool = False
        self.goal: bool = False
        self.derrick: bool = False
        self.adjacent = []  # a priority queue
        self.distance: int = sys.maxsize
        self.previous = None  # will be set when visited
        self.visited = False

    def __str__(self):
        e = 'T' if self.exhausted else 'F'
        g = 'T' if self.goal else 'F'
        d = 'T' if self.derrick else 'F'
        # s = f'node[{self.row},{self.col}] terrain: {self.terrain}, '
        # s += f'wells: {self.wells} '
        # s += f'exhausted: {e}, goal: {g}, derrick: {d}, '
        # s += f'totcost: {"∞" if self.distance == sys.maxsize else self.distance}, '
        # s += f'adjacent: {sorted(self.adjacent)}'

        s = f'{self.id} t: {self.terrain}, '
        s += f'w: {self.wells} '
        s += f'ex: {e}, goal: {g}, derrick: {d}, '
        s += f'{self.previous=}, '
        s += f'dist: {"∞" if self.distance == sys.maxsize else self.distance}, '
        s += f'adjacent: {sorted(self.adjacent)}'
        return s

    def __repr__(self):
        s = f'{self.id}.t: {self.terrain}'
        return s

    def __lt__(self, other):
        return self.distance < other.distance


class Graph:
    # board will hold the numpy array[rows, cols] of Node instances

    def __init__(self, board):
        self.board = board
        self.rows = len(board)
        self.columns = len(board[0])
        # Make a 1d view of the 2d board
        self.graph = [node for row in board for node in row]
        print(self.graph)
        for node in self.graph:
            node.set_neighbors(board)

    def get_rows_cols(self):
        return self.rows, self.columns

    def reset_totalcost(self):
        for node in self.graph:
            node.totalcost = sys.maxsize
            node.visited = False

    def print_board(self):
        for row in range(self.rows):
            for col in range(self.columns):
                print(self.board[row][col])
                if self.board[row][col].previous:
                    self.board[row][col].print_path()


def create_graph(csvfile, nplayers):
    """
    Each line in the csv file describes one column of the board. (It was easier
    to type this way). Each line contains cells separated by white space.
    Each cell contains:

        <cell> ::= <terrain> | <terrain> "." <oilwell> | "." <oilwell>
        <terrain> ::= 1 | 2 | 3
        <oilwell> ::= <wellcount> | <wellcount> <3-player marker>
        <wellcount> ::= 1 | 2 | 3
        <3-player marker> = "x"

    If <terrain> is absent, "1" is assumed.

    :param csvfile: The file containing the board as described above.
    :param nplayers: If equals 3, exclude wells from cells with a trailing "x".
    :return: An array of Node instances
    """
    r = []  # rows
    ncols = 0
    for nline, line in enumerate(csvfile):
        c = line.split()
        if ncols == 0:
            ncols = len(c)
        if len(c) != ncols:
            raise ValueError(f"Length of line {nline + 1} is {len(c)}, {ncols} expected.")
        r.append(c)
    # board = list(map(list, zip(*board)))  # create list of lists, not tuples
    # Invert the array giving a list of tuples corresponding to the columns.
    rawboard = list(zip(*r))
    if _args.verbose >= 2:
        print('rawboard:', rawboard)
    three_players = nplayers == 3
    nrows = len(rawboard)
    ncols = len(rawboard[0])
    board = [[Node(r, c) for c in range(ncols)] for r in range(nrows)]
    # nodes = np.array(nodes)
    for r, row in enumerate(board):
        for c, node in enumerate(row):
            m = re.match(r'(\d?)(\.(\d)(x?))?', cell := rawboard[r][c])
            if m is None:
                raise ValueError(f"In row {r}, col {c}, '{cell}' failed match.")
            node.terrain = 1 if m.group(1) == '' else int(m.group(1))
            if m.group(3):  # if wells are specified
                node.wells = 0 if (m.group(4) == 'x' and three_players
                                   ) else int(m.group(3))
    # for r in board:
    #     for node in r:
    #         node.set_neighbors(board)
    # print(nodes)
    graph = Graph(board)
    return graph


def djikstra(a_graph, root):
    """
    :param a_graph: the Graph instance
    :param root: the node to start from
    :return:
    """
    root.distance = 0
    unvisited_queue = a_graph.graph[:]
    heapq.heapify(unvisited_queue)
    while len(unvisited_queue):
        # Pops a vertex with the smallest distance
        current = heapq.heappop(unvisited_queue)
        current.visited = True
        if _args.verbose >= 3:
            print(f'{current=}')
        # for next in v.adjacent:
        for nextv in sorted(current.adjacent):
            # if visited, skip
            if nextv.visited:
                if _args.verbose >= 3:
                    print(f'skipping {nextv=}')
                continue
            new_dist = current.distance + nextv.terrain
            nextv_dist = nextv.distance
            if new_dist < nextv_dist:
                nextv.distance = new_dist
                nextv.previous = current
                updated = 'updated'  # just used for logging
            else:
                updated = 'not updated'
            if _args.verbose >= 3:
                # print('%s : current = %s next = %s new_dist = %s'
                #       % (updated, current.id, nextv.id, nextv_dist))
                print(f'{updated}: current: {current.id}, next: {nextv.id}, '
                      f'dist: {nextv_dist}->{nextv.distance}')
        # Rebuild heap
        # Put all vertices not visited into the queue
        unvisited_queue = [v for v in a_graph.graph if not v.visited]
        if _args.verbose >= 3:
            print(f'unvisited: {unvisited_queue}')

        heapq.heapify(unvisited_queue)


def main(args):
    graph = create_graph(args.incsv, nplayers=4)
    rows, cols = graph.get_rows_cols()
    if _args.verbose >= 1:
        print(f'{rows=} {cols=}')
    graph.reset_totalcost()
    djikstra(graph, graph.board[0][0])
    if _args.verbose >= 2:
        graph.print_board()
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
