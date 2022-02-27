"""

"""
from __future__ import annotations
import sys
from typing import Union, TYPE_CHECKING
if TYPE_CHECKING:  # kludge to avoid circular imports at run time
    from player import Player


class Node:
    """
    cost: Number of movement points it costs to enter this node.
    exhausted: True if a derrick has been built and all the oil has been extracted.
    goal: Number of adjacent cells with wells. Decremented if a derrick is built
    """

    def set_neighbors(self, board):
        """
        This is called by Graph.__init__.

        :param board: the board from a Graph instance

        adjacent contains a list of nodes next to this node.
        A node can have up to 4 adjacent, reduced if it is on an edge.

        :return: None. The adjacent list in this node is set.
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
            if self.wells and not self.derrick:
                if neighbor.wells == 0:
                    neighbor.goal += 1

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
        assert self.derrick is False
        self.derrick = True
        for node in self.adjacent:
            # Assume there are no adjacent cells with wells which is true on
            # the Giganten board.
            assert node.goal > 0
            node.goal -= 1

    def remove_derrick(self):
        # Make this node passable
        assert self.derrick is True
        self.derrick = False
        self.exhausted = True
        self.wells = 0

    def print_path(self):
        nextprev = self.previous
        path = []
        while nextprev:
            # print(f'nextprev: {nextprev}')
            path.append(nextprev)
            nextprev = nextprev.previous
        path.reverse()
        print('   ', path)

    def __init__(self, row: int, col: int, derrick=False):
        self.row: int = row
        self.col: int = col
        self.id: str = f'<{row},{col}>'
        self.terrain: int = 0
        # wells: int in 0..3: the number of wells on the square. If non-zero
        # the square is covered with a tile at the start of the game. Wells
        # are assigned when the Graph is instantiated.
        self.wells: int = 0
        # oil_reserve: the number on the bottom side of the tile covering a
        # square with well(s) or the number of plastic markers under a derrick.
        # If wells == 2 then we cannot peek at the oil reserve in deciding
        # whether to drill.
        self.oil_reserve: int = 0
        self.exhausted: bool = False
        self.goal: int = 0  # count of adjacent nodes with unbuilt wells
        self.goal_reached: bool = False
        self.derrick: bool = derrick
        self.truck: Union[Player, None] = None  # set when a truck moves here
        self.adjacent = []  # will be populated by set_neighbors
        self.cell = None  # this node's string from rawboard

        # Fields set by dijkstra
        self.distance: int = sys.maxsize
        self.previous: Union[Node, None] = None  # will be set when visited

    def __repr__(self):
        e = 'T' if self.exhausted else 'F'
        g = self.goal
        t = self.truck
        d = 'T' if self.derrick else 'F'
        # s = f'node[{self.row},{self.col}] terrain: {self.terrain}, '
        # s += f'wells: {self.wells} '
        # s += f'exhausted: {e}, goal: {g}, derrick: {d}, '
        # s += f'totcost: {"∞" if self.distance == sys.maxsize else self.distance}, '
        # s += f'adjacent: {sorted(self.adjacent)}'

        s = f'{self.id} t: {self.terrain}, '
        s += f'w: {self.wells} '
        s += f'ex={e}, goal={g}, derrick={d}, truck={t}, '
        s += f'previous={self.previous}, '
        s += f'dist: {"∞" if self.distance == sys.maxsize else self.distance}, '
        sa = sorted(self.adjacent)
        s += f'adjacent: {(ss.id for ss in sa)}'
        return s

    def __str__(self):
        s = f'{self.id}{"*" if self.goal_reached else ""}'
        return s

    # Needed by heapq
    def __lt__(self, other):
        return self.distance < other.distance
