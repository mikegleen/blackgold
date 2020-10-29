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

red_action_cards = (
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
beige_action_cards = (
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

if __name__ == '__main__':
    """
        Create a temporary beige.py file with a reformated beige.csv.
        Manually copy beige.py into this file, replacing beige_action_cards.
    """
    beigecsv = open('data/beige.csv')
    beigepy = open('src/beige.py', 'w')
    print('beige_action_cards = (', file=beigepy)
    for card in beigecsv:
        c = card.split()
        if len(c) == 2:
            c += [0]
        print(f'    ({c[0]}, {c[1]}, {c[2]}),', file=beigepy)
    print(')', file=beigepy)
