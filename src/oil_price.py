"""

"""
import math
import numpy as np

debug = False
maxblue = 9000.
minblue = 7000.
minwhite = 4000.
minred = 1500.

dicevalues = [2, 2, 3, 3, 4, 4]
dicecolors = [0, 1, 0, 1, 0, 1]
red = 0
blue = 1
colors = ('R', 'B')


def next_price_1(oldprice, throw):
    value = dicevalues[throw]
    deltaprice = value * 500.
    color = dicecolors[throw]
    if color == red:
        if oldprice < minwhite:  # in the red zone
            newprice = oldprice + deltaprice
        else:                 # in the white or blue zone
            newprice = oldprice - deltaprice
    else:                     # dice color is blue
        if oldprice >= minblue:
            newprice = oldprice - deltaprice
        else:
            newprice = oldprice + deltaprice
    if debug:
        print(f'{value}{colors[color]} ${oldprice} -> ${newprice}')
    return newprice


def next_price_2(oldprice, throw):
    value = dicevalues[throw]
    deltaprice = value * 500.
    color = dicecolors[throw]
    if color == red:
        newprice = oldprice - deltaprice
        if newprice < 500.:
            newprice = 500.
    else:                     # dice color is blue
        newprice = oldprice + deltaprice
        if newprice > 9000.:
            newprice = 9000.
    if debug:
        print(f'{value}{colors[color]} ${oldprice} -> ${newprice}')
    return newprice


def testnext():
    for price in range(500, 9001, 500):
        for ix in range(6):
            next_price_1(price, ix)


def game(moves):
    price1 = price2 = 5000.
    prices1 = np.zeros(moves)
    prices2 = np.zeros(moves)
    for t in range(moves):
        ix = np.random.randint(6)
        price1 = next_price_1(price1, ix)
        prices1[t] = price1
        price2 = next_price_2(price1, ix)
        prices2[t] = price2
    mean1 = np.mean(prices1)
    stddev1 = math.sqrt(np.var(prices1, ddof=1))
    # print(f'algorithm 1: {mean1=} {stddev1= }')
    mean2 = np.mean(prices2)
    stddev2 = math.sqrt(np.var(prices2, ddof=1))
    # print(f'algorithm 2: {mean2=} {stddev2= }')
    return mean1, mean2, stddev1, stddev2


if __name__ == '__main__':
    iterations = 1000
    mm1 = np.zeros(iterations)
    mm2 = np.zeros(iterations)
    ss1 = np.zeros(iterations)
    ss2 = np.zeros(iterations)
    for n in range(iterations):
        m1, m2, s1, s2 = game(150)
        mm1[n] = m1
        mm2[n] = m2
        ss1[n] = s1
        ss2[n] = s2
    print('Algorithm 1:')
    mean1m = np.mean(mm1)
    stddev1m = math.sqrt(np.var(mm1, ddof=1))
    mean1s = np.mean(ss1)
    stddev1s = math.sqrt(np.var(ss1, ddof=1))
    print(f'{mean1m=:.2f}, {stddev1m=:.2f}, {mean1s=:.2f}, {stddev1s=:.2f}')

    print('Algorithm 2:')
    mean2m = np.mean(mm2)
    stddev2m = math.sqrt(np.var(mm2, ddof=1))
    mean2s = np.mean(ss2)
    stddev2s = math.sqrt(np.var(ss2, ddof=1))
    print(f'{mean2m=:.2f}, {stddev2m=:.2f}, {mean2s=:.2f}, {stddev2s=:.2f}')

    # testnext()
