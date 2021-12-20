"""

"""
from colorama import Fore, Style
import re
import sys

from node import Node

LEFTWARDS_ARROW = '\u2190'
UPWARDS_ARROW = '\u2191'
RIGHTWARDS_ARROW = '\u2192'
DOWNWARDS_ARROW = '\u2193'


class Graph:
    # board - hold the array[rows, cols] of Node instances
    # graph - a 1d list of the Nodes, easier to iterate over.
    # for print_board: 0->illegal 1->flat 2->hilly 3->mountain
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    RESET = Style.RESET_ALL
    """
    TERRAIN_CH is indexed by terrain type. Zero is illegal. Types 1, 2, and 3
    refer to flat, hilly, or mountain and correspond to the cost of moving into
    that square.
    """
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
                m = re.match(r'(\d?)(\.(\d?)([xd]?))?',
                             (cell := rawboard[r][c]).lower())
                node.cell = cell
                # print(f'{r=} {c=} {m.group(1,2,3,4)=}')
                if m is None:
                    raise ValueError(
                        f"In row {r}, col {c}, '{cell}' failed match.")
                node.terrain = 1 if m.group(1) == '' else int(m.group(1))
                if m.group(3):  # if wells are specified
                    node.wells = 0 if (m.group(4) == 'x' and three_players
                                       ) else int(m.group(3))
                # For testing, force a derrick
                # print(node)
                # print(f'{m.group(4)=}')
                if m.group(4) == 'd':
                    node.derrick = True
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

    def reset_graph(self):
        """
        Called by dijkstra() before each move.
        @return:
        """
        for node in self.graph:
            node.distance = sys.maxsize
            node.visited = False
            node.previous = None

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

    def dump_raw_board(self, outfilename):
        """
            This is a little utility method to create a file readable as an
            input board CSV file. This is useful if the original CSV file was
            created manually by columns but we want to proceed with the
            file as rows as this is more understandable.
        """
        if outfilename is None:
            return
        outfile = open(outfilename, 'w')
        for row in range(self.rows):
            r = ''
            for col in range(self.columns):
                node = self.board[row][col]
                cell = node.cell
                r += f'{cell:>5}'
            print(r, file=outfile)
        outfile.close()

    def print_board_narrow(self):

        def pr_dist(node):
            dist = node.distance
            return f'{dist:2d}' if dist < sys.maxsize else '  '

        def pr_wells(node):
            if node.exhausted:
                return 'X'
            return'D' if node.derrick else 'W'

        # self.board[4][13].derrick = True  # test feature
        print('   ' + ''.join([f'| {n:02} ' for n in range(self.columns)])
              + '|')
        for nrow, row in enumerate(self.board):
            print('   ' + '|————' * self.columns + '|')
            r1 = [Graph.TERRAIN_CH[n.terrain] + pr_dist(n) for n in row]
            print(f' {nrow:02}|' + '|'.join(r1) + '|')
            r2 = [(pr_wells(n) * n.wells) + (' ' * (3 - n.wells))
                  + (n.goal if n.goal else ' ') for n in row]
            print('   |' + '|'.join(r2) + '|')
        print('   ' + '|————' * self.columns + '|')

    def print_board(self):

        def pr_dist(node):
            dist = node.distance
            return f'{dist:2d}' if dist < sys.maxsize else '  '

        def pr_wells(node):
            if node.exhausted:
                return 'X  '
            well = 'D' if node.derrick else 'w'
            return well * node.wells + (' ' * (3 - node.wells))

        def from_arrow(node):
            if not (previous := node.previous):
                return ' '
            if node.row == previous.row:
                return (LEFTWARDS_ARROW if node.col > previous.col else
                        RIGHTWARDS_ARROW)
            else:
                return (UPWARDS_ARROW if node.row > previous.row else
                        DOWNWARDS_ARROW)

        print('   ' + ''.join([f'| {n:03d} ' for n in range(self.columns)])
              + '|')
        for nrow, row in enumerate(self.board):
            print('   ' + '|—————' * self.columns + '|')
            r1 = [Graph.TERRAIN_CH[n.terrain] + pr_dist(n) for n in row]
            print(f' {nrow:02}|' + '|'.join(r1) + '|')
            r2 = [pr_wells(n)
                  + from_arrow(n)
                  + (Graph.RED + str(n.goal) + Graph.RESET if n.goal else ' ')
                  for n in row]
            print('   |' + '|'.join(r2) + '|')
        print('   ' + '|—————' * self.columns + '|')
