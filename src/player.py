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
        self.train_col = 0
        self.free_oil_rigs = config.INITIAL_OIL_RIGS
        self.rigs_in_use = []  # list of Nodes with drilling rigs
        self.cash = config.INITIAL_CASH
        self.barrels = 0
        self.actions = None  # to be defined by set_actions()
        self.single_licenses = 0
        self.double_licenses = 0

    def set_actions(self, nlicenses, movement, markers, backwards, oilprice):
        self.actions: Actions = Actions(nlicenses, movement, markers, backwards, oilprice)
