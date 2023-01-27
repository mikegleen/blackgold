from collections import namedtuple
import config
import node

"""
    Actions: The player draws a red or beige action card which defines the
    actions to be taken. 
    
"""
Actions = namedtuple('Actions', 'nlicenses movement markers backwards oilprice')


class Player:

    def __init__(self, playerid: int, truck_node: node.Node):
        self.id: int = playerid
        self.truck_node: node.Node = truck_node
        self.truck_hist: list[str] = [str(truck_node)]
        self.train_col = 0
        self.free_oil_rigs: int = config.INITIAL_OIL_RIGS
        self.rigs_in_use: list[node.Node] = []
        self.cash = config.INITIAL_CASH
        self.storage_tanks: list[int] = [0] * config.NCOMPANIES
        self.actions = None  # to be defined by set_actions()
        self.single_licenses = []
        self.double_licenses = []
        self.nlicenses = 0

    def set_actions(self, nlicenses, movement, markers, backwards, oilprice):
        self.actions: Actions = Actions(nlicenses, movement, markers,
                                        backwards, oilprice)

    def advance_train(self, verbos):
        """
        The same movement points are used for the truck and the train.

        We've already moved the truck. If any movement points are left, advance
        the train.
        """
        old_movement = movement = self.actions.movement  # from action card just drawn
        old_train_col = self.train_col
        movement -= self.truck_node.distance
        # needed: cost to move to next column increases as we advance
        while (needed := config.TRAIN_COSTS[self.train_col + 1]) <= movement:
            movement -= needed
            self.train_col += 1
        if verbos >= 2:
            print(f'advance_train: player {self.id}, movement: {old_movement}->'
                  f'{movement}, train_col {old_train_col} -> {self.train_col}, '
                  f'truck dist = {self.truck_node.distance}')

    def __repr__(self):
        s = f'{self.id}'
        return s
