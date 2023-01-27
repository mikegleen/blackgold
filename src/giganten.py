"""

"""
import argparse
from typing import NamedTuple
import config
import copy
import heapq
import inspect
import os.path
import random
import sys
import time

from test.test_dijkstra import time_dijkstra, one_dijkstra
from node import Node
from graph import Graph
from player import Player
import oil_price


def trace(level, template, *args):
    if _args.verbose >= level:
        stack = inspect.stack()
        # fileinfo = f'{module_name}: {stack[1][2]}: {stack[1][3]}'
        fileinfo = f'{stack[1][2]}: {stack[1][3]}'
        print(fileinfo, template.format(*args))


class Game:
    def __init__(self, graph: Graph, nplayers):
        assert nplayers <= len(config.TRUCK_INIT_ROWS)
        self.nplayers = nplayers
        self.black_train_col = 0
        self.selling_price: list[int] = [5000] * config.NCOMPANIES
        self.players = []
        self.graph = graph
        self.oil_marker_stockpile = config.INITIAL_OIL_MARKERS
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
        self.licenses = copy.deepcopy(config.LICENSE_CARDS)
        # print(f'\n{self.licenses=}')
        self.license_discards = []
        self.licenses_exhausted = False
        random.shuffle(self.licenses)

    def move_black_train(self, spaces_to_move):
        self.black_train_col += spaces_to_move
        game_ended = self.black_train_col >= self.graph.columns
        return game_ended

    def audit_licenses(self):
        licenses = 0
        for player in self.players:
            for card in player.single_licenses:
                assert card.num_licenses == 1
                licenses += 1
            for card in player.double_licenses:
                assert card.num_licenses == 2
                licenses += 2
        for card in self.licenses:
            licenses += card.num_licenses
        for card in self.license_discards:
            licenses += card.num_licenses
        assert licenses == config.TOTAL_LICENSES


def draw_card(cards, discards):
    """
    @param cards:
    @param discards:
    @return: The drawn card
    """
    try:
        card = cards.pop()
    except IndexError:  # Oops, the deck is empty
        while discards:
            card = discards.pop()
            cards.append(card)
        if cards:
            random.shuffle(cards)
            card = cards.pop()
        else:
            card = None
    return card


def deal_licenses(player: Player, game: Game):
    """
    A license card can have either one or two licenses. Accumulate .
    @param player:
    @param game:
    @return: None. The player's number of licenses is updated.
    """
    cards, discards = game.licenses, game.license_discards
    # oldnlicenses = player.nlicenses
    # oldlencards = len(cards)
    # oldlendiscards = len(discards)
    for n in range(player.actions.nlicenses):
        card: config.LicenseCard = draw_card(cards, discards)
        if card is None:
            if not game.licenses_exhausted:
                game.licenses_exhausted = True
                trace(2, 'Licenses exhausted')
            break
        if card.num_licenses == 1:
            player.single_licenses.append(card)
        else:
            player.double_licenses.append(card)
    player.nlicenses = (len(player.single_licenses)
                        + 2 * len(player.double_licenses))
    # print(f'deal_licenses: {player.id=} licenses:{oldnlicenses}->{player.nlicenses} cards:{oldlencards}->{len(cards)}, '
    #       f'discards: {oldlendiscards}->{len(discards)}')
    return


def read_board(csvfile):
    """
    :param: csvfile: The file containing the board as described above.
    :return: A list of rows containing tuples corresponding to the columns.
             Each cell is the string as defined above.
    Each line in the csv file describes one row or one column of the board,
    depending on argument --bycols.
    Lines beginning with '#' and blank lines are ignored.
    Cells are separated by whitespace. Each cell contains:

        <cell> ::= <terrain> | <terrain> "." <oilwell> | "." <oilwell>
        <terrain> ::= 1 | 2 | 3
        <oilwell> ::= <wellcount> | <wellcount> <variant>
        <wellcount> ::= 1 | 2 | 3
        <variant> = "x" | "d"

    If <terrain> is absent, "1" is assumed.
    If <variant> == "x" then this is a cell ignored for 3-person games.
    If <variant> == "d" then this cell contains a derrick (used for testing).

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
        # Note zip returns an iterable so call list() to expand it.
        rawboard = list(zip(*r))
    else:
        rawboard = r
    # if _args.verbose >= 2:
    #     print('rawboard:', rawboard)
    trace(3, '{}', rawboard)
    return rawboard


def dijkstra(graph: Graph, root: Node, maxcost=sys.maxsize, verbose=1):
    """
    :param: graph: So we can clear it before updating its Nodes
    :param: root: the Node to start from. The Nodes have been initialized
             during the creation of the Graph instance.
    :param: maxcost: Do not search for nodes more than maxcost away.
    :param: verbose: the debug level
    :return: A tuple of the set of visited nodes and a set of the goal nodes

             The Node's distance field is updated in each node in the
             board that is reachable from the root node given the game's
             constraints such as within the maximum distance from the root
             where the "distance" is the sum of the costs of entering each
             node depending on the terrain.
    """

    def idist(distance):
        return "∞" if distance == sys.maxsize else distance

    graph.reset_graph()  # distances = ∞, clear previous
    root.distance = 0
    unvisited_queue = [root]
    visited = dict()  # Use a dictionary instead of a set to preserve order
    goals = set()
    while unvisited_queue:
        # Pops a vertex with the smallest distance
        current = heapq.heappop(unvisited_queue)
        visited[current] = None  # kludge an ordered set
        if current.goal:
            goals.add(current)
        # trace(3, 'current={} current.adjacent={}', current, current.adjacent)
        if current.distance >= maxcost:
            trace(3, '    stopping at distance {}.', current.distance)
            continue
        for nextn in sorted(current.adjacent):  # iterate over adjacent nodes
            trace(4, 'nextn={}, current={} {}', nextn, current,
                  "DERRICK" if nextn.derrick else "")
            if nextn in visited:  # if visited, skip
                trace(4, 'skipping, visited: nextn={}, current={}', nextn,
                      current)
                continue
            if nextn.derrick or nextn.truck:
                trace(4, 'skipping, derrick or truck: nextn={}, current={}',
                      nextn, current)
                continue
            new_dist = current.distance + nextn.terrain
            nextn_dist = nextn.distance
            #
            # If the next node has wells, the player may not stop there.
            if nextn.wells and new_dist >= maxcost:
                trace(4, 'skipping, wells: nextn={}, current={}', nextn,
                      current)
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
                      f'dist: {idist(nextn_dist)} -> {idist(nextn.distance)}')
        # trace(3, 'unvisited: {}', unvisited_queue)
    # Convert the set of goals into a list sorted by column
    # goals = sorted(list(goals), key=lambda node: node.col, reverse=True)
    # print ("****returning from dijkstra")
    return visited, goals


def choose_goal(player: Player, graph: Graph) -> Node:
    """
    Choose a player's next move:
    Iterate over possible destination nodes:
    Assign a score to a possible move according to:
    1. Columns moved right
    2. Is the destination node a goal node?
    3. Are there other goal nodes on the path to the destination node?
    4. Do I need to advance my train?
    @Player player
    @Graph graph
    """
    scores = []
    graph.reset_graph()
    truck_node = player.truck_node
    maxcost = player.actions.movement

    visited, goals = dijkstra(graph, truck_node, maxcost, verbose=_args.verbose)
    # graph.print_board()
    # print(f'{visited=}')
    # print(f'{set(visited)=}')
    # sys.exit()
    for node in visited:
        score = 0
        # Increase the score for each column we move the truck
        score += (node.col - truck_node.col) * config.TRUCK_COLUMN_MULTIPLIER
        # Increase the score if adjacent nodes have wells
        score += node.goal * config.GOAL_MULTIPLIER
        prevnode: Node = node.previous
        examined = set()
        while prevnode:
            if prevnode in examined:
                print(f'loop from {node}: {prevnode=}, {examined=}')
                graph.print_board()
                sys.exit()
            examined.add(prevnode)
            # print(f'{player.id=} {prevnode=}')
            # Increase the score if a node on the path is a goal, but no extra
            # if the node has more than one neighbor with wells
            score += prevnode.goal * config.PREV_GOAL_MULTIPLER
            prevnode = prevnode.previous
        if player.train_col < node.col:
            # Compute points available to move the train
            points = maxcost - node.distance
            # See how far we can move the train
            train_dest = player.train_col
            while (points_needed :=
                   config.TRAIN_COSTS[train_dest + 1]) <= points:
                points -= points_needed
                train_dest += 1
            # Increase the score for each column we can move the train.
            cols = train_dest - player.train_col
            score += cols * config.TRAIN_COLUMN_MULTIPLIER
        scores.append((node, score))
    scores.sort(key=lambda x: x[1])
    if _verbose >= 3:
        # slist = [(str(s[0]), s[1]) for s in scores]
        slist = ", ".join(["(" + str(s[0]) + ", " + str(s[1]) + ")" for s in scores])
        trace(3, 'scores={}', slist)
    trace(2, '{}->{}', truck_node, scores[-1][0])
    return scores[-1][0]  # return the node with the highest score


def build_oilrig(player: Player):
    """

    @param player:
    @return:
    """
    truck_node = player.truck_node
    if not truck_node.goal or not player.free_oil_rigs:
        return
    sites = [n for n in truck_node.adjacent if n.wells and not n.derrick]
    # Since node is a goal, at least one neighbor must have wells.
    assert sites
    # todo: Add heuristic for choosing site. For now just choose the first.
    # then decide if we want to build based on how many sites we have, the
    # position of our train, the price of oil, the availability of space in
    # our tanks.
    site: Node = sites[0]
    cost = config.BUILDING_COST[site.wells]
    if cost > player.cash:
        return
    player.cash -= cost
    player.rigs_in_use.append(site)
    player.free_oil_rigs -= 1
    site.add_derrick()
    trace(2, 'player {}: {}, oil reserve: {}, cash now: {}, free rigs: {} ',
          player, site, site.oil_reserve, player.cash, player.free_oil_rigs)


def transport_oil(player: Player, game: Game):
    """
    All players have a tank at each company. During Action 6 they remove
    one oil marker from each rig and transport it to one of the tanks.

    """

    def transport_available() -> bool:
        """
        Determine if a train is available to transport the oil. If my train
        can do it, just return True. If the black train or an opponent's train
        is available, pay them if the cash is available, otherwise return False

        @return: True if a train is available, false otherwise
        """
        if node.col <= player.train_col:
            return True
        # I can't use my train. Try the black train and the opponents' trains
        if player.cash < config.TRANSPORT_COST:
            return False
        farthest_players = []
        farthest_col = -1
        for opponent in game.players:
            if opponent.id == player.id:
                continue
            if opponent.train_col > farthest_col:
                farthest_players = [opponent]
                farthest_col = opponent.train_col
            elif opponent.train_col == farthest_col:
                farthest_players.append(opponent)
        if game.black_train_col > farthest_col:
            if node.col > game.black_train_col:
                return False
            player.cash -= config.TRANSPORT_COST
            return True
        # The black train column is <= the farthest opponent
        if farthest_col < node.col:
            return False
        player.cash -= config.TRANSPORT_COST
        # Payment goes in equal measure to the opponents who were most advanced.
        # In the rare case that the black train is just as advanced as the
        # farthest player, the Baron gets a share.
        total_transporters = len(farthest_players)
        if game.black_train_col == farthest_col:
            total_transporters += 1
        payment = config.TRANSPORT_COST / total_transporters
        for opponent in farthest_players:
            opponent.cash += payment
        return True

    def remove_marker_from_rig():
        node.oil_reserve -= 1
        if node.oil_reserve == 0:
            player.rigs_in_use.remove(node)
            player.free_oil_rigs += 1
            node.remove_derrick()

    for node in player.rigs_in_use:
        assert node.oil_reserve > 0  # sanity check
        # Select the tank with the least oil
        if not transport_available():
            # Return the marker to the stockpile
            remove_marker_from_rig()
            game.oil_marker_stockpile += 1
            continue
        leastmarkers = sys.maxsize
        emptiest_tank = -1  # avoid pycharm warning
        for tankn in range(config.NCOMPANIES):
            if (markers := player.storage_tanks[tankn]) < leastmarkers:
                leastmarkers = markers
                emptiest_tank = tankn
        # Move one oil marker to my tank at the selected oil company
        remove_marker_from_rig()
        player.storage_tanks[emptiest_tank] += 1
    trace(2, 'Action 6: player {}, rigs, reserve {}', player.id,
          [(str(n), n.oil_reserve) for n in player.rigs_in_use])


def surrender_licenses(player: Player, required: int, game: Game):
    """
    @param player:
    @param required: Number of licenses required
    @param game:
    @return:
    """

    def one_license(licenses):
        license_card = licenses.pop()
        game.license_discards.append(license_card)

    if game.licenses_exhausted:
        trace(2, 'Licenses not exhausted.')
        game.licenses_exhausted = False
    total_surrendered = required
    trace(3, 'required = {}', required)
    if required % 2 == 1:  # if odd number of licenses needed
        if player.single_licenses:
            one_license(player.single_licenses)
            required -= 1
        else:
            # There are no single licenses so must use a double card
            required += 1
            total_surrendered += 1
    assert player.nlicenses >= required
    # dv: the value of the licenses on the double license cards
    if (dv := len(player.double_licenses) * 2) >= required:
        for n in range(required // 2):
            one_license(player.double_licenses)
    else:
        while player.double_licenses:
            one_license(player.double_licenses)
        required -= dv
        # still need some from the single pile
        for n in range(required):
            one_license(player.single_licenses)
    player.nlicenses -= total_surrendered
    assert player.nlicenses == (len(player.single_licenses)
                                + 2 * len(player.double_licenses))


def sell_oil(company: int, game: Game, player_list: list[Player]):
    """
    This isn't like a normal auction where bids are made in turn. Here, each
    player names their maximum bid and the highest bidder pays 1 more than
    the next highest. The exception is if there is a tie, then the winner
    pays the amount bid. If there is a tie, the winner is the first player
    in the list, which starts with the current player.
    testing: if # of players == 1, next highest bid is zero, so the number of
    licenses bid will always be 1.

    @param company:
    @param game:
    @param player_list:
    @return:
    """
    def compute_bid():
        """
        Compute the maximum bid for a player. Things to consider:
        # of licenses I have
        # of oil units in the oil tank at all companies
        current selling price

        If there are more than 2 units in this oil tank, I will have to sell
        them for $1000.

        @return:
        """
        # Heuristic: my max bid is the percent of my licenses corresponding to
        # the percent profit to be made by selling at this company.
        licenses = player.nlicenses
        profit = [game.selling_price[c] * player.storage_tanks[c]
                  for c in range(config.NCOMPANIES)]
        tot_profit = sum(profit[company:])  # only look at companies in play
        if tot_profit != 0:
            mybid = licenses * profit[company] // tot_profit
        else:
            mybid = None
        return mybid

    Bid = NamedTuple('Bid', [('player', Player), ('value', int)])
    bids: list = []
    storage = []
    for player in player_list:
        storage.append(player.storage_tanks[company])
    trace(2, 'company {}, storage: {}', company, storage)
    for player in player_list:
        bid = Bid(player, compute_bid())
        trace(2, 'player {}, single/double licenses: {}/{}, '
                 'total: {} bid: {}, price: ${}',
              player.id, len(player.single_licenses),
              len(player.double_licenses), player.nlicenses, bid.value,
              game.selling_price[company])
        if bid.value:
            bids.append(bid)
    # Find the highest bid (tie goes to first found)
    highest = 0
    winner = None
    for bid in bids:
        if bid.value > highest:
            winner = bid
            highest = bid.value
    # The winner pays 1 more than the next highest bidder
    if winner:
        player = winner.player
        bids.remove(winner)
        next_highest = 0
        for bid in bids:
            if bid.value > next_highest:
                next_highest = bid.value
        if highest > next_highest:
            next_highest += 1
        surrender_licenses(player, next_highest, game)
        # Get paid
        oil_units = player.storage_tanks[company]
        price = (game.selling_price[company] * oil_units)
        trace(2, '    player {} sells {} units to company {} for ${}',
              player.id, oil_units, company, price)
        trace(2, '     licenses used: {}, {} remaining ', next_highest,
              player.nlicenses)
        player.cash += price
        player.storage_tanks[company] = 0


def one_turn(turn: int, playerlist: list[Player], game: Game):
    """
    @param turn: for debug
    @param playerlist:
    @param game:
    @return: True if game ended else None
    """

    # Action 1: Change the selling price
    for company in range(config.NCOMPANIES):
        oil_price.set_price(game.selling_price, company)

    # Action 2: Take action cards
    action_cards = []
    red_card = draw_card(game.red_action_cards, game.red_discards)
    action_cards.append(red_card)

    # Action 2a: Move black train
    if game.move_black_train(red_card.black_loco):
        return True  # game ended
    for i in range(len(game.players)):
        beige_card = draw_card(game.beige_action_cards, game.beige_discards)
        action_cards.append(beige_card)

    # Each player selects one action card, starting with starting_player
    trace(config.TR_ACTION_CARDS, 'Turn: {}, players {}, price: {}, black train col: {} ',
          turn, playerlist, game.selling_price, game.black_train_col)
    for player in playerlist:

        # todo: Heuristic needed to select the best action card.
        cardn = random.randrange(len(action_cards))
        card = action_cards[cardn]

        if type(card) == config.RedActionCard:  # Selected the red card
            nlicenses = red_card.nlicenses
            movement = red_card.movement
            markers = red_card.markers
            backwards = red_card.backwards
            oilprice = 0
            game.red_discards.append(card)
        else:  # Selected one of the beige cards
            card = action_cards[cardn]
            nlicenses = card.nlicenses
            movement = card.movement
            oilprice = card.oilprice
            markers = backwards = 0
            game.beige_discards.append(card)
        del action_cards[cardn]
        player.set_actions(nlicenses, movement, markers, backwards, oilprice)

    # Action 3: Hand out licenses
    for player in game.players:
        deal_licenses(player, game)

    # Action 4 Move the truck and locomotive and do special actions

    for player in playerlist:
        nextnode: Node = choose_goal(player, game.graph)
        trace(2, 'Action 4: player {}, truck_node: {} —> {} {}, licenses: '
              '{}, cash: ${}',
              player, player.truck_node, str(nextnode),
              player.actions, player.nlicenses, player.cash)
        if nextnode.goal:
            nextnode.goal_reached = True
        # todo: Examine goal nodes en route to this node
        # 4a: Placing and moving trucks
        player.truck_node.truck = None
        nextnode.truck = player
        player.truck_node = nextnode
        player.truck_hist.append(str(nextnode))

        # 4b: Searching for Oil
        # This is handled in choose_goal() which peeks at sites if allowed

        # 4c: Moving your own locomotive
        if nextnode.distance < player.actions.movement:
            player.advance_train(_verbose)

        trace(2, '          traincol: {}, goal: {}, truck@{}',
              player.train_col, nextnode.goal, nextnode)

    # Action 5: Building Oilrigs
    for player in playerlist:
        build_oilrig(player)

    # Action 6: Drilling and transporting the oil
    for player in playerlist:
        transport_oil(player, game)

    # Action 7: Selling oil
    for company in range(config.NCOMPANIES):
        sell_oil(company, game, playerlist)

    # Action 8: Storage tank limitations
    for player in playerlist:
        storage_tanks: list = player.storage_tanks
        for n in range(len(storage_tanks)):
            if storage_tanks[n] > 2:
                units_to_sell = storage_tanks[n] - 2
                storage_tanks[n] = 2
                player.cash += units_to_sell * config.FORCED_SALE_PRICE

    # Discard unused action cards
    for card in action_cards:
        if type(card) == config.RedActionCard:  # Selected the red card
            game.red_discards.append(card)
        else:
            game.beige_discards.append(card)
    trace(config.TR_ACTION_CARDS, 'beige cards/discards: {}/{}', len(game.beige_action_cards),
          len(game.beige_discards))
    if _args.short:
        return True


def compute_score(playerlist: list[Player]):
    """
    Award money to players based on the number of oil rigs on the board.
    Determine the price paid based on a score, $5k, $4k, $3k, $2k paid to
    players in descending order according to the following:
    1. The most significant decider is the placement of the player's loco.
       The furthest along (to the right) is the highest score.
    2. If there is a tie, then the player with the highest number of existing
       licenses is the highest.
    3. If still a tie, the player closest to the starting player wins.


    @param playerlist:
    @return:
    """
    loco_order = []
    playerorder = len(playerlist)
    for player in playerlist:
        playerorder -= 1  # starting player gets the highest score and so on
        loco_order.append((player.train_col, player.nlicenses, playerorder,
                           player))
    loco_order.sort(reverse=True)
    pricex = 0
    for _, _, _, player in loco_order:
        price = config.GAME_END_RIG_PRICE[pricex]
        pricex += 1
        rigs = len(player.rigs_in_use)
        player.cash += price * rigs
        # Count oil markers
        oil_reserve = 0
        for node in player.rigs_in_use:
            oil_reserve += node.oil_reserve
        for tank in player.storage_tanks:
            oil_reserve += tank
        player.cash += config.GAME_END_MARKER_PRICE * oil_reserve
        trace(config.TR_COMPUTE_SCORE,
              'player {}: rigs: {}, oil reserve: {}, '
              'train col: {}, cash: ${}', player.id,
              rigs, oil_reserve, player.train_col, player.cash)


def play_game(game):
    game_ended = False
    turn = 0
    playerlist = []
    starttime = time.process_time()
    while not game_ended:
        turn += 1
        for starting_player in game.players:
            playern = starting_player.id
            playerlist = []
            for n in range(game.nplayers):
                playerlist.append(game.players[playern])
                playern += 1
                if playern >= game.nplayers:
                    playern = 0
            game_ended = one_turn(turn, playerlist, game)
            if _verbose >= 2:
                game.audit_licenses()
            if game_ended:
                break
        if turn >= _args.turns:
            return
    elapsed = time.process_time() - starttime
    compute_score(playerlist)
    scores = [p.cash for p in game.players]
    max_score = max(scores)
    winners = [p for p, score in enumerate(scores) if score == max_score]
    trace(config.TR_FINAL_PATH,
          f'Game ended. Elapsed: {elapsed:5.4f} seconds, '
          f'{game.black_train_col=}, {winners=}')
    for player in game.players:
        trace(config.TR_FINAL_PATH,
              'Player {} cash = ${}, path = {}',
              player.id, player.cash, player.truck_hist)
    return winners


def main():
    rawboard = read_board(_args.incsv)
    graph = Graph(rawboard, _args.nplayers)
    if _args.dumprawboard:
        graph.dump_raw_board(_args.dumprawboard)
    if _verbose >= 3:
        graph.dump_board()
    nrows, ncols = graph.get_rows_cols()
    if _verbose >= 1:
        m = _args.maxcost
        print(f'root: <{_args.row},{_args.column}> {nrows=} {ncols=}'
              f' maxcost: {str(m) if m < sys.maxsize else "∞"}')
    if _args.timeit:
        time_dijkstra(graph, dijkstra, _args)
    elif _args.dijkstra:
        one_dijkstra(graph, dijkstra, _args, _verbose)
        # print("*** returned from one_dijkstra")
    else:
        winners = [0 for _n in range(_args.nplayers)]
        ties = 0
        random.seed(config.RANDOM_SEED)
        starttime = time.process_time()
        for ngame in range(_args.games):
            trace(3, "game # {}", ngame)
            graph = Graph(rawboard, _args.nplayers)
            game = Game(graph, _nplayers)
            winnerlist = play_game(game)
            for w in winnerlist:
                winners[w] += 1
            if len(winnerlist) > 1:
                ties += 1
            # print(f'{winnerlist=}')

        elapsed = time.process_time() - starttime
        print(f'{ties=}, {winners=}, {elapsed=:6.3f}')
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
    Start column. For testing.
    ''')
    parser.add_argument('--dumprawboard', help='''
    Specify the file to dump the raw board to. Useful if the input is by
    columns. The output raw board is by rows.
    ''')
    parser.add_argument('-g', '--games', type=int, default=1,
                        help='''
    Number of games to play. Default is 1.
    ''')
    parser.add_argument('-k', '--dijkstra', action='store_true', help='''
    Do one run of dijkstra. Implies -p. For testing.
    ''')
    parser.add_argument('-m', '--maxcost', type=int, default=sys.maxsize,
                        help='''
    Maximum distance of interest. For testing.
    ''')
    parser.add_argument('-n', '--nplayers', default=4, type=int, help='''
    Specify the number of players; the default is 4.
    ''')
    parser.add_argument('-p', '--print', action='store_true', help='''
    Print the finished board with distances.
    ''')
    parser.add_argument('-r', '--row', type=int, default=0, help='''
    Start row. For testing.
    ''')
    parser.add_argument('-s', '--short', action='store_true', help='''
    Stop after one turn.
    ''')
    parser.add_argument('--timeit', type=int, help='''
    Time the dijkstra function with this number of iterations.
    ''')
    parser.add_argument('-t', '--turns', type=int, default=sys.maxsize, help='''
    Stop the game after this many turns.
    ''')
    parser.add_argument('-v', '--verbose', default=1, type=int, help='''
    Modify verbosity.
    ''')
    args = parser.parse_args()
    if args.dijkstra:
        args.print = True
    return args


if __name__ == '__main__':
    module_name = os.path.basename(__file__)
    assert sys.version_info >= (3, 8)
    _args = getargs()
    _maxcost = _args.maxcost
    _verbose = _args.verbose
    _nplayers = _args.nplayers
    if _verbose > 1:
        print(f'verbosity: {_args.verbose}')
    main()
    print('End giganten.')
