
if __name__ == '__main__':
    """
        Helper script to convert the manually-entered action card data
        to Python executable text.
        Create a temporary beige.py file with a reformated beige.csv.
        Manually copy beige.py into this file, replacing beige_action_cards.
    """
    beigecsv = open('data/beige.csv')
    beigepy = open('src/beige.py', 'w')
    print('BEIGE_ACTION_CARDS = (', file=beigepy)
    for card in beigecsv:
        if card.startswith('#'):
            continue
        c = card.split()
        if len(c) == 2:
            c += [0]
        print(f'    ({c[0]}, {c[1]}, {c[2]}),', file=beigepy)
    print(')', file=beigepy)
