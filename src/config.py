"""

"""
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
TRAIN_MOVEMENT_COSTS:
How much it costs to move a player's train one column.
"""
BLACK_TRAIN_COSTS = [0] + [1] * 9 + [2] * 7 + [3] * 3

INITIAL_CASH = 15_000
INITIAL_OIL_RIGS = 5

"""
    Define the contents of the card decks.
"""

"""
black loco: Advance the black locomotive.
licenses: Deal green license cards.
movement: Advance the player's loco or truck.
markers: Take one crude oil marker.
backwards: Move all opponents locos backwards.
"""

RED_ACTION_CARDS = (
    (3, 3, 4, 1, 0),
    (2, 4, 8, 0, 2),
    (2, 3, 6, 0, 3),
    (2, 2, 6, 1, 0),
    (1, 4, 2, 1, 0),
    (3, 2, 4, 0, 5),
    (2, 2, 6, 0, 4),
    (3, 3, 4, 1, 0),
    (1, 2, 8, 0, 3),
    (2, 2, 6, 1, 0),
    (3, 2, 6, 0, 4),
    (2, 3, 2, 0, 5),
)

"""
licenses
movement
oilprice: Change any oil price up or down. 
"""
BEIGE_ACTION_CARDS = (
    (2, 10, 2),
    (7, 4, 0),
    (5, 8, 0),
    (5, 5, 3),
    (4, 10, 0),
    (5, 8, 0),
    (4, 5, 4),
    (4, 10, 0),
    (4, 6, 3),
    (5, 8, 0),
    (5, 8, 0),
    (2, 10, 2),
    (3, 8, 3),
    (6, 6, 0),
    (3, 12, 0),
    (5, 8, 0),
    (4, 10, 0),
    (3, 12, 0),
    (6, 6, 0),
    (5, 8, 0),
    (7, 4, 0),
    (4, 5, 4),
    (6, 6, 0),
    (8, 3, 0),
    (4, 5, 4),
    (6, 6, 0),
    (3, 12, 0),
    (4, 10, 0),
    (6, 4, 2),
    (4, 10, 0),
)

