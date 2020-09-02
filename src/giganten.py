"""

"""
import argparse
from colorama import Fore, Style
import heapq
import re
import sys
import time

LEFTWARDS_ARROW = '\u2190'
UPWARDS_ARROW = '\u2191'
RIGHTWARDS_ARROW = '\u2192'
DOWNWARDS_ARROW = '\u2193'


class Node:
    """
    cost: Number of movement points it costs to enter this node.
    exhausted: True if a derrick has been built and all of the oil has been extracted.
    goal: True if a neighbor is an oil well; changes to False if a derrick is built
    """

    def set_neighbors(self, board):
        """
        This is called by Graph.__init__.
        
        :param board: the board from a Graph instance
        
        adjacent contains a list of nodes next to this node.
        A node can have up to 4 adjacent, reduced if it is on an edge.

        :return: None. The adjacent list in all nodes are set.
        """
        def set1neighbor(nrow, ncol):
            """
            :param nrow: neighbor row
            :param ncol: neighbor column
            :return: None; the neighbor is added to the list
            """
            neighbor = board[nrow][ncol]
            self.adjacent.append(neighbor)
            # If the neighbor has wells, you aren't allowed to stop there,
            # so it can't be a goal.
            if neighbor.wells == 0:
                neighbor.goal |= self.wells > 0 and not (self.derrick or
                                                         self.exhausted)

        lastrow = len(board) - 1
        lastcol = len(board[0]) - 1
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
        self.barrels = 0
        self.adjacent = []  # will be populated by set_neighbors
        self.distance: int = sys.maxsize
        self.previous = None  # will be set when visited

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
        s += f'previous={repr(self.previous)}, '
        s += f'dist: {"∞" if self.distance == sys.maxsize else self.distance}, '
        s += f'adjacent: {sorted(self.adjacent)}'
        return s

    def __repr__(self):
        s = f'{self.id}'
        return s

    # Needed by heapq
    def __lt__(self, other):
        return self.distance < other.distance


class Graph:
    # board will hold the numpy array[rows, cols] of Node instances

    # for print_board: 0->illegal 1->flat 2->hilly 3->mountain
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RESET = Style.RESET_ALL
    RED = Fore.RED
    TERRAIN_CH = ('@', GREEN + '—  ' + RESET, GREEN + '~~ ' + RESET,
                  GREEN + '^^^' + RESET)

    def __init__(self, rawboard, nplayers):
        three_players = nplayers == 3
        nrows = len(rawboard)
        ncols = len(rawboard[0])
        board = [[Node(r, c) for c in range(ncols)] for r in range(nrows)]
        # nodes = np.array(nodes)
        for r, row in enumerate(board):
            for c, node in enumerate(row):
                # See read_board() for a description of the pattern
                m = re.match(r'(\d?)(\.(\d)(x?))?', cell := rawboard[r][c])
                if m is None:
                    raise ValueError(
                        f"In row {r}, col {c}, '{cell}' failed match.")
                node.terrain = 1 if m.group(1) == '' else int(m.group(1))
                if m.group(3):  # if wells are specified
                    node.wells = 0 if (m.group(4) == 'x' and three_players
                                       ) else int(m.group(3))
        self.board = board
        self.rows = nrows
        self.columns = ncols
        # Make a 1d view of the 2d board
        self.graph = [node for row in board for node in row]
        # print(self.graph)
        for node in self.graph:
            node.set_neighbors(board)

    def get_rows_cols(self):
        return self.rows, self.columns

    def reset_distance(self):
        for node in self.graph:
            node.distance = sys.maxsize
            node.visited = False

    def dump_board(self):
        print('Dump Board')
        for row in range(self.rows):
            for col in range(self.columns):
                node = self.board[row][col]
                print('printing node: ', end='')
                print(node)
                if node.previous:
                    print('    printing path: ', end='')
                    node.print_path()

    def print_board_narrow(self):

        def pr_dist(node):
            dist = node.distance
            return f'{dist:2d}' if dist < sys.maxsize else '  '

        def pr_wells(node):
            return'D' if node.derrick else 'W'

        # self.board[4][13].derrick = True  # test feature
        print('   ' + ''.join([f'| {n:02} ' for n in range(self.columns)]) + '|')
        for nrow, row in enumerate(self.board):
            print('   ' + '|————' * self.columns + '|')
            r1 = [Graph.TERRAIN_CH[n.terrain] + pr_dist(n) for n in row]
            print(f' {nrow:02}|' + '|'.join(r1) + '|')
            r2 = [(pr_wells(n) * n.wells) + (' ' * (3 - n.wells))
                  + ('G' if n.goal else ' ') for n in row]
            print('   |' + '|'.join(r2) + '|')
        print('   ' + '|————' * self.columns + '|')

    def print_board(self):

        def pr_dist(node):
            dist = node.distance
            return f'{dist:2d}' if dist < sys.maxsize else '  '

        def pr_wells(node):
            return'D' if node.derrick else 'W'

        def from_arrow(node):
            if not (previous := node.previous):
                return ' '
            if node.row == previous.row:
                return (LEFTWARDS_ARROW if node.col > previous.col else
                        RIGHTWARDS_ARROW)
            else:
                return (UPWARDS_ARROW if node.row > previous.row else
                        DOWNWARDS_ARROW)

        # self.board[4][13].derrick = True  # test feature
        print('   ' + ''.join([f'| {n:03d} ' for n in range(self.columns)]) + '|')
        for nrow, row in enumerate(self.board):
            print('   ' + '|—————' * self.columns + '|')
            r1 = [Graph.TERRAIN_CH[n.terrain] + pr_dist(n) for n in row]
            print(f' {nrow:02}|' + '|'.join(r1) + '|')
            r2 = [(pr_wells(n) * n.wells) + (' ' * (3 - n.wells))
                  + from_arrow(n)
                  + (Graph.RED + 'G' + Graph.RESET if n.goal else ' ') for n in row]
            print('   |' + '|'.join(r2) + '|')
        print('   ' + '|—————' * self.columns + '|')


def read_board(csvfile):
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
    :return: A list of rows containing tuples corresponding to the columns.
             Each cell is the string as defined above.
    """
    r = []  # rows
    nrows = 0
    for nline, line in enumerate(csvfile):
        c = line.split()  # one column
        if nrows == 0:
            nrows = len(c)
        if len(c) != nrows:
            raise ValueError(f"Length of line {nline + 1} is "
                             f"{len(c)}, {nrows} expected.")
        r.append(c)
    # board = list(map(list, zip(*board)))  # create list of lists, not tuples
    # Invert the array giving a list of tuples where each tuple is one row.
    rawboard = list(zip(*r))
    if _args.verbose >= 2:
        print('rawboard:', rawboard)
    return rawboard


def djikstra(root: Node, maxcost=sys.maxsize):
    """
    :param root: the Node to start from. The Nodes have been initialized
             during the creation of the Graph instance.
    :param maxcost: Do not search for nodes more than maxcost away.
    :return: The Node's distance field is updated in each instance in the
             board that is reachable from the root node given the game's
             constraints such as within the maximum distance from the root
             where the "distance" is the sum of the costs of entering each
             node depending on the terrain.
    """
    root.distance = 0
    unvisited_queue = [root]
    visited = set()
    while unvisited_queue:
        # Pops a vertex with the smallest distance
        current = heapq.heappop(unvisited_queue)
        visited.add(current)
        if _args.verbose >= 3:
            print(f'{current=}')
        if current.distance >= maxcost:
            if _args.verbose >= 3:
                print(f'    stopping at distance {current.distance}.')
            continue
        for nextv in sorted(current.adjacent):
            if nextv in visited:  # if visited, skip
                if _args.verbose >= 3:
                    print(f'skipping {nextv=}')
                continue
            new_dist = current.distance + nextv.terrain
            nextv_dist = nextv.distance
            if new_dist < nextv_dist and new_dist <= maxcost:
                nextv.distance = new_dist
                nextv.previous = current
                heapq.heappush(unvisited_queue, nextv)
                updated = 'updated'  # just used for logging
            else:
                updated = 'not updated'
            if _args.verbose >= 3:
                # print('%s : current = %s next = %s new_dist = %s'
                #       % (updated, current.id, nextv.id, nextv_dist))
                print(f'{updated}: current: {current.id}, next: {nextv.id}, '
                      f'dist: {nextv_dist}->{nextv.distance}')
        if _args.verbose >= 3:
            print(f'unvisited: {unvisited_queue}')


def main(args):
    rawboard = read_board(args.incsv)
    graph = Graph(rawboard, args.nplayers)
    nrows, ncols = graph.get_rows_cols()
    if args.verbose >= 1:
        m = args.maxcost
        print(f'{nrows=} {ncols=}'
              f'{" maxcost=" + str(m) if m < sys.maxsize else ""}')
    if args.timeit:
        t1 = time.time()
        for _ in range(args.timeit):
            graph.reset_distance()
            djikstra(graph.board[args.row][args.column],
                     maxcost=args.maxcost)
        t2 = time.time()
        print(t2 - t1)
    else:
        graph.reset_distance()
        djikstra(graph.board[args.row][args.column],
                 maxcost=args.maxcost)
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
    parser.add_argument('-c', '--column', type=int, default=0, help='''
    Start column.
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
    Time the djikstra function with this number of iterations.
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
