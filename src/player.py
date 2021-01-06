import node


class Player:

    def __init__(self, playerid, truck_node):
        self.id = playerid  # am enum member
        self.truck_node = truck_node
        self.train_col = None
        self.oilrigs = 0
        self.rigs_in_use = []
        self.cash = 15_000
        self.barrels = 0
