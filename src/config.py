"""

"""
from collections import namedtuple
import sys

# TILES: This dict defines the cardboard pieces that cover the squares
#        containing wells.
#        The key is the number of oil wells, the value is a list of the
#        number of oil markers to be allocated when a derrick is built.
#        This list will be copied, shuffled and allocated to the nodes
#        according to the number of wells on that node. When a player builds
#        a derrick, the number of oil markers corresponding to the tile's
#        value are allocated to the node.
# TODO: Handle the maximum of 60 oil markers in the game.
TILES = {
    1: [2] * 4 + [3] * 4 + [4] * 4,
    2: [2] * 6 + [5] * 6,
    3: [4] * 4 + [5] * 4 + [6] * 4
}
"""
TRAIN_COSTS:
How much it costs to move a player's train one column. Appending maxsize to the
end prevents train movement past the board.
"""
TRAIN_COSTS = [0] + [1] * 9 + [2] * 7 + [3] * 3 + [sys.maxsize]

INITIAL_CASH = 15_000
INITIAL_PRICE = 5000
INITIAL_OIL_RIGS = 5
INITIAL_OIL_MARKERS = 60
# the rows in the first column to place the trucks at the start of the game
TRUCK_INIT_ROWS = [1, 5, 7, 9]

NCOMPANIES = 3

# For Action 8, Storage Tank Limitations, any crude markers in storage tanks
# above the limit must be sold to the bank for $1000 each.
STORAGE_TANK_LIMIT = 2
FORCED_SALE_PRICE = 1000

# Cost to build a derrick. The index is the number of wells on a site.
BUILDING_COST = [0, 4000, 6000, 8000]

# Cost to transport oil on the black train or on an opponent's train
TRANSPORT_COST = 3000

# The price paid for oilrigs at the end of the game
GAME_END_RIG_PRICE = (5000, 4000, 3000, 2000)
GAME_END_MARKER_PRICE = 1000
"""
    Define the contents of the red card deck.

    black loco: Advance the black locomotive.
    nlicenses: Number of green license cards to deal
    movement: Advance the player's loco or truck.
    markers: Take one crude oil marker.
    backwards: Move all opponents locos backwards.
"""
RedActionCard = namedtuple('RedActionCard', 'black_loco nlicenses movement'
                                            ' markers backwards')
RED_ACTION_CARDS = [
    RedActionCard(3, 3, 4, 1, 0),
    RedActionCard(2, 4, 8, 0, 2),
    RedActionCard(2, 3, 6, 0, 3),
    RedActionCard(2, 2, 6, 1, 0),
    RedActionCard(1, 4, 2, 1, 0),
    RedActionCard(3, 2, 4, 0, 5),
    RedActionCard(2, 2, 6, 0, 4),
    RedActionCard(3, 3, 4, 1, 0),
    RedActionCard(1, 2, 8, 0, 3),
    RedActionCard(2, 2, 6, 1, 0),
    RedActionCard(3, 2, 6, 0, 4),
    RedActionCard(2, 3, 2, 0, 5),
]

"""
    Define the contents of the beige card deck.

    nlicenses
    movement
    oilprice: Change any oil price up or down. 
"""
BeigeActionCard = namedtuple('BeigeActionCard', 'nlicenses movement oilprice')
BEIGE_ACTION_CARDS = [
    BeigeActionCard(2, 10, 2),
    BeigeActionCard(7, 4, 0),
    BeigeActionCard(5, 8, 0),
    BeigeActionCard(5, 5, 3),
    BeigeActionCard(4, 10, 0),
    BeigeActionCard(5, 8, 0),
    BeigeActionCard(4, 5, 4),
    BeigeActionCard(4, 10, 0),
    BeigeActionCard(4, 6, 3),
    BeigeActionCard(5, 8, 0),
    BeigeActionCard(5, 8, 0),
    BeigeActionCard(2, 10, 2),
    BeigeActionCard(3, 8, 3),
    BeigeActionCard(6, 6, 0),
    BeigeActionCard(3, 12, 0),
    BeigeActionCard(5, 8, 0),
    BeigeActionCard(4, 10, 0),
    BeigeActionCard(3, 12, 0),
    BeigeActionCard(6, 6, 0),
    BeigeActionCard(5, 8, 0),
    BeigeActionCard(7, 4, 0),
    BeigeActionCard(4, 5, 4),
    BeigeActionCard(6, 6, 0),
    BeigeActionCard(8, 3, 0),
    BeigeActionCard(4, 5, 4),
    BeigeActionCard(6, 6, 0),
    BeigeActionCard(3, 12, 0),
    BeigeActionCard(4, 10, 0),
    BeigeActionCard(6, 4, 2),
    BeigeActionCard(4, 10, 0),
]
LicenseCard = namedtuple('LicenseCard', 'num_licenses')
LICENSE_CARDS = [LicenseCard(1)] * 39 + [LicenseCard(2)] * 39
TOTAL_LICENSES = 117  # 39 + 39 * 2
RANDOM_SEED = None

"""
    Heuristics for choosing a truck destination
"""
GOAL_MULTIPLIER = 2
TRUCK_COLUMN_MULTIPLIER = 1
PREV_GOAL_MULTIPLER = 1
TRAIN_COLUMN_MULTIPLIER = 1

"""
    Define trace levels
"""
TR_ACTION_CARDS = 2
TR_COMPUTE_SCORE = 2
TR_FINAL_PATH = 2
