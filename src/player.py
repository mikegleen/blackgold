import config
import node


class Player:

    def __init__(self, playerid: int, truck_node: node.Node):
        self.id: int = playerid
        self.truck_node: node.Node = truck_node
        self.train_col = 0
        self.free_oil_rigs = config.INITIAL_OIL_RIGS
        self.rigs_in_use = []  # list of Nodes with drilling rigs
        self.cash = config.INITIAL_CASH
        self.barrels = 0
