"""

"""
import argparse
import config
import copy
import heapq
import random
import sys
import time

from node import Node
from graph import Graph
from player import Player
import oil_price


def trace(level, template, *args):
    if _args.verbose >= level:
        print(template.format(*args))


class OilCompany:
    def __init__(self, nplayers: int):
        self.price = config.INITIAL_PRICE
        self.storage_tanks = [0] * nplayers


class Game:
    def __init__(self, graph: Graph, nplayers):
        assert nplayers <= len(config.TRUCK_INIT_ROWS)
        self.nplayers = nplayers
        self.black_train_col = 0
        self.selling_price: list[int] = [5000] * 3
        self.players = []
        self.graph = graph
        for n in range(nplayers):
            trucknode: Node = graph.board[config.TRUCK_INIT_ROWS[n]][0]
            player = Player(n, trucknode)
            trucknode.truck = player
            self.players.append(player)
        self.beige_action_cards = copy.deepcopy(config.BEIGE_ACTION_CARDS)
        self.red_action_cards = copy.deepcopy(config.RED_ACTION_CARDS)
        self.beige_discards = []
        self.red_discards = []
        random.shuffle(self.beige_action_cards)
        random.shuffle(self.red_action_cards)
        tiles = copy.deepcopy(config.TILES)
        for k in (1, 2, 3):
            random.shuffle(tiles[k])
        for node in graph.graph:
            # Select a random tile from the shuffled list according
            # to the number of wells. Indicate that this is the amount
            # of oil underground.
            node.oil_reserve = tiles[node.wells].pop() if node.wells else 0

    def move_black_train(self, spaces_to_move):
        self.black_train_col += spaces_to_move
        game_ended = self.black_train_col >= self.graph.columns
        return game_ended


def draw_action_card(cards, discards):
    """
    
    @param cards: 
    @param discards: 
    @return: The drawn card, the modified cards list and the (possibly)
             modified discards list
    """
    try:
        card = cards.pop()
    except IndexError:  # Oops, the deck is empty
        cards = discards
        random.shuffle(cards)
        discards = []
        card = cards.pop()
    return card, cards, discards


def one_turn(starting_player: Player, game: Game):
    """
    @param starting_player:
    @param game:
    @return: None
    """
    
    # Action 1: Change the selling price
    for company in range(config.NUMBER_OF_OIL_COMPANIES):
        oil_price.set_price(game.selling_price, company)

    # Action 2: Take action cards
    action_cards = []
    red_card, game.red_action_cards, game.red_discards = draw_action_card(
        game.red_action_cards, game.red_discards)
    action_cards.append(red_card)
    if game.move_black_train(red_card.black_loco):
        return True  # game ended
    for i in range(len(game.players)):
        beige_card, game.beige_action_cards, game.beige_discards = (
            draw_action_card(game.beige_action_cards, game.beige_discards))
        action_cards.append(beige_card)

    # todo: Heuristic needed to select the best action card.

    # Each player selects one action card, starting with starting_player
    playern = starting_player.id
    for n in range(game.nplayers):
        player = game.players[playern]
        licenses = movement = markers = backwards = oilprice = 0

        cardn = random.randrange(len(action_cards))
        if cardn == 0:
            licenses = red_card.licenses
            movement = red_card.movement
            markers = red_card.markers
            backwards = red_card.backwards
            game.red_discards.append(red_card)
            del action_cards[0]
        else:
            card = action_cards[cardn]
            game.beige_discards.append(card)
            del action_cards[cardn]
            licenses = card.licenses
            movement = card.movement
            oilprice = card.oilprice

        # Action 3: Hand out licenses

        # Select the next player
        playern += 1
        if playern >= game.nplayers:
            playern = 0
    # goal: Node = choose_goal(player, game.graph, _maxcost)


def play_game(graph):

    game = Game(graph, _nplayers)
    game_ended = False
    while not game_ended:

        for playerid in range(_nplayers):
            game_ended = one_turn(game.players[playerid], game)
            if game_ended:
                return


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


def drill_sites(goal_node):
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
                ret.append((n, node))
        node = node.previous
        # If the node has wells, we're not allowed to stop there.
        while node and node.wells:
            node = node.previous
    return ret


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
            if nextn.derrick or nextn.truck:
                trace(3, 'skipping, derrick or truck: nextn={}', nextn)
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
    goals = sorted(list(goals), key=lambda node: node.col * 100 + node.row,
                   reverse=True)
    return goals


def choose_goal(player: Player, graph: Graph, maxcost: int) -> Node:
    """
    Choose a player's next move:
    Find all possible goal nodes.
    Assign points to a possible move according to:
    1. Columns moved right
    2. Oil reserve at potential drill site.
    @Player player
    @Graph graph
    @int maxcost

    """
    graph.reset_distance()
    truck_node = player.truck_node
    goals = dijkstra(graph.board[truck_node.row][truck_node.col],
                     maxcost=maxcost, verbose=_args.verbose)
    gsites = {g: drill_sites(g) for g in goals}
    return truck_node


def time_dijkstra(graph):
    t1 = time.time()
    for _ in range(_args.timeit):
        graph.reset_distance()
        dijkstra(graph.board[_args.row][_args.column],
                 maxcost=_args.maxcost, verbose=_args.verbose)
    t2 = time.time()
    print(t2 - t1)


def one_dijkstra(graph):
    goals = dijkstra(graph.board[_args.row][_args.column],
                     maxcost=_args.maxcost, verbose=_args.verbose)
    gsites = {g: drill_sites(g) for g in goals}
    if _verbose >= 2:
        print(f'{goals=}')
        print(f'{gsites=}')
    return gsites


def main():
    rawboard = read_board(_args.incsv)
    graph = Graph(rawboard, _args.nplayers)
    graph.dump_raw_board(_args.dumprawboard)
    if _verbose >= 3:
        graph.dump_board()
    nrows, ncols = graph.get_rows_cols()
    if _verbose >= 1:
        m = _args.maxcost
        print(f'{nrows=} {ncols=}'
              f'{" maxcost=" + str(m) if m < sys.maxsize else ""}')
    if _args.timeit:
        time_dijkstra(graph)
    elif _args.dijkstra:
        one_dijkstra(graph)
    else:
        play_game(graph)
    if _args.verbose >= 3:
        graph.dump_board()
    # print(board)
    if _args.print:
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
    parser.add_argument('-k', '--dijkstra', help='''
    Do one run of dijkstra. Implies -p.
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
    if args.dijkstra:
        args.print = True
    return args


if __name__ == '__main__':
    assert sys.version_info >= (3, 8)
    _args = getargs()
    _maxcost = _args.maxcost
    _verbose = _args.verbose
    _nplayers = _args.nplayers
    if _verbose > 1:
        print(f'verbosity: {_args.verbose}')
    main()
    print('End giganten.')
