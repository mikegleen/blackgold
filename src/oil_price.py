"""
This program compares two rules for adjusting the price of oil in Giganten.

Rule 1 is the standard as defined in the game rules.
    You role a die with numbers 2, 3, and 4, each in blue and red.
    If the old price is in the red zone, then ignore the die color and increase
        the price according to the number thrown.
    Similarly, if the old price is in the blue zone, decreased it.
    If the old price is in the white zone (the middle), increase the price if
        the color of the die is blue, decreased otherwise.

Rule 2 changes the rule so that the die color always controls whether the price
    increases or decreases, only limited by the minimum and maximum price.
"""
import math
import numpy as np
import matplotlib.pyplot as plt
import random

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
        if newprice < 1500.:
            newprice = 1500.
    else:                     # dice color is blue
        newprice = oldprice + deltaprice
        if newprice > 9000.:
            newprice = 9000.
    if debug:
        print(f'{value}{colors[color]} ${oldprice} -> ${newprice}')
    return newprice


def next_price(oldprice):
    ix = random.randint(0, 5)
    return next_price_1(oldprice, ix)


def game(moves):
    price1 = price2 = 5000.
    prices1 = np.zeros(moves)
    prices2 = np.zeros(moves)
    for t in range(moves):
        ix = random.randint(0, 5)
        price1 = next_price_1(price1, ix)
        prices1[t] = price1
        count1[price1] += 1
        price2 = next_price_2(price2, ix)
        prices2[t] = price2
        count2[price2] += 1
    mean1 = np.mean(prices1)
    stddev1 = math.sqrt(np.var(prices1, ddof=1))
    # print(from_node'algorithm 1: {mean1=} {stddev1= }')
    mean2 = np.mean(prices2)
    stddev2 = math.sqrt(np.var(prices2, ddof=1))
    # print(from_node'algorithm 2: {mean2=} {stddev2= }')
    return mean1, mean2, stddev1, stddev2


def stats(an, mm, ss, count, lbl, color):
    print(f'Algorithm {an}:')
    meanm = np.mean(mm)
    stddevm = math.sqrt(np.var(mm, ddof=1))
    means = np.mean(ss)
    stddevs = math.sqrt(np.var(ss, ddof=1))
    print(f'{meanm=:.2f}, {stddevm=:.2f}, {means=:.2f}, {stddevs=:.2f}')
    plt.plot(list(count), list(count.values()), '-ok', label=lbl, color=color)


if __name__ == '__main__':
    games = 500
    moves_per_game = 100
    print(f'{games=}, moves per games: {moves_per_game}')
    mm1 = np.zeros(games)
    mm2 = np.zeros(games)
    ss1 = np.zeros(games)
    ss2 = np.zeros(games)
    count1 = {float(x): 0.0 for x in range(1500, 9001, 500)}
    count2 = {float(x): 0.0 for x in range(1500, 9001, 500)}

    for n in range(games):
        m1, m2, s1, s2 = game(moves_per_game)
        mm1[n] = m1
        mm2[n] = m2
        ss1[n] = s1
        ss2[n] = s2

    plt.xlabel('Oil Price')
    plt.ylabel(f'Occurences in {games} games, each of {moves_per_game} moves')
    stats(1, mm1, ss1, count1, "Original Algorithm", 'blue')
    stats(2, mm2, ss2, count2, "Modified Algorithm", 'red')
    plt.legend()
    plt.show()
