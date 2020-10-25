"""

"""
from heapq import heappush
import re
import sys
from dataclasses import dataclass

import numpy as np
from excel_cols import col2num  # in ~/pyprj/misc

testwells = '2b 2e 5d 6b 6f'
testrough = '2d 3f 4c 5a 5f'
testhilly = '1e 3c 3g 4e 6d'


class Node:
    """
    cost: Number of movement points it costs to enter this node.
    """
    row: int
    col: int
    cost: int
    isgoal: bool  # True if a neighbor is an oil well; will change to False
    #               if a derrick is built there.
    #
    # neighbors contains a list of tuples of (cost, row, column)
    neighbors: list

    def set_neighbors(self, board):
        """
        A node can have up to 4 neighbors, reduced if it is on an edge.
        :param board:
        :return:
        """
        def set1neighbor(nrow, ncol):
            """
            :param nrow: neighbor row
            :param ncol: neighbor column
            :return: None; the neighbor is added to the list
            """
            cost = board[nrow, ncol]
            if cost > 0:
                heappush(self.neighbors, (cost, nrow, ncol))

        self.neighbors = []  # a priority queue
        rows, cols = board.shape
        if self.row > 0:
            set1neighbor(self.row - 1, self.col)
        if self.col > 0:
            set1neighbor(self.row, self.col - 1)
        if self.row < rows - 1:
            set1neighbor(self.row + 1, self.col)
        if self.col < cols - 1:
            set1neighbor(self.row, self.col + 1)

    def __init__(self, row, col, board):
        self.row = row
        self.col = col
        self.cost = board[row, col]
        self.set_neighbors(board)


def build_board(nrows, ncols, wells, rough, hilly):
    """

    :param nrows:
    :param ncols:
    :param wells: A string of space-delimited excel-style locations of oil well
    :param rough: As above for rough cells
    :param hilly: As above for hilly cells
    :return: An array populated with the defined contents.

    The values are the number of moves required to enter the cell, except for
    the well cells which cannot be entered.

    """

    def extract_rc(s):
        """
        :param s: A string of excel_style cell addresses like '1a 2b'
        :return: A list of (row, col) tuples
        """
        extracted = []
        cells = s.split()
        for cell in cells:
            m = re.match(r'(\d+)(.+)$', cell)
            if m:
                exrow = int(m.group(1)) - 1  # make zero-based
                excol = col2num(m.group(2))
                extracted.append((exrow, excol))
            else:
                raise ValueError(f'Bad format: "{cell}" in "{s}"')
        return extracted

    brd = np.ones((nrows, ncols), dtype=int)
    for locs, value in ((wells, 0), (rough, 2), (hilly, 3)):
        for row, col in extract_rc(locs):
            brd[row, col] = value
    return brd


def read_board(csvfile):
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

    :return:
    """
    r = []  # rows
    line = csvfile.next().strip()
    c = line.split(',')
    r.append(c)
    ncols = len(c)
    nline = 1
    for line in csvfile:
        nline += 1
        c = line.strip().split(',')
        if len(c) != ncols:
            raise ValueError(f"Length of line {nline} is {len(c)}, {ncols} expected.")
        r.append(c)
    return r


if __name__ == '__main__':
    assert sys.version_info >= (3, 8)
    board1 = build_board(7, 7, testwells, testrough, testhilly)
    # for r in range(board.shape[0]):
    #     print(board[r])
    print(board1)
    gamemap = np.empty((7, 7), dtype=object)
    for i in range(7):
        for j in range(7):
            gamemap[i, j] = Node(i, j, board1)
    pass
    # board2 = np.rot90(board1, k=2)
    # print()
    # for r in range(board2.shape[0]):
    #     print(board2[r])
    # print(board2)
    for i in range(7):
        print(f'\n*********** ROW {i}')
        for j in range(7):
            print(j, gamemap[i, j].neighbors)

