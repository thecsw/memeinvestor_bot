import math

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import formula

def main():
    fig = plt.figure(figsize=(15,15))

    # Lay out the figure as a grid of subplots
    gridspec.GridSpec(6, 2)

    # ---GRAPH A---
    # Plotting return curve for different olds

    # Upper left subplot
    ax = plt.subplot2grid((6, 2), (0, 0), rowspan=3, colspan=1)

    olds = [0, 1, 5, 10, 25, 50, 100, 200, 500, 1000, 2500, 5000, 7500, 10000, 15000, 20000]
    news = range(0, 25000)

    xy = []
    for o in olds:
        x = []
        y = []
        for n in news:
            if n > o:
                x.append(n)
                y.append(formula.calculate(n, o))
        xy.append([x,y])

    for (x, y) in xy:
        plt.plot(x, y)

    ax.grid(color='k', alpha=0.15, which='major')
    ax.set_ylim([0, 5.5])

    plt.legend(list(olds))
    plt.title('Return factor')
    plt.xlabel('new')
    plt.ylabel('calculate(new, old)')

    # ---GRAPH B---
    # Plotting return curve for small olds only

    # Bottom left subplot
    ax = plt.subplot2grid((6, 2), (3, 0), rowspan=3, colspan=1)

    olds = [0, 1, 5, 10, 25, 50, 100, 200]
    news = range(0, 500)

    xy = []
    for o in olds:
        x = []
        y = []
        for n in news:
            if n > o:
                x.append(n)
                y.append(formula.calculate(n, o))
        xy.append([x,y])

    for (x, y) in xy:
        plt.plot(x, y)

    ax.grid(color='k', alpha=0.15, which='major')
    ax.set_ylim([0, 5.5])

    plt.legend(list(olds))
    plt.title('Return factor')
    plt.xlabel('new')
    plt.ylabel('calculate(new, old)')

    # ---GRAPH C.1---
    # Plotting sigmoid_max

    # Upper right subplot
    ax = plt.subplot2grid((6, 2), (0, 1), rowspan=1, colspan=1)

    olds = range(0, 25000)

    x = []
    y = []
    for o in olds:
        x.append(o)
        y.append(formula.sigmoid_max(o))

    plt.plot(x, y)

    ax.grid(color='k', alpha=0.15, which='major')
    ax.set_ylim([0, 5.5])

    plt.title('sigmoid_max(old)')
    plt.xlabel('old')

    # ---GRAPH C.2:---
    # Plotting sigmoid_midpoint

    # Upper right subplot
    ax = plt.subplot2grid((6, 2), (1, 1), rowspan=1, colspan=1)

    olds = range(0, 25000)

    x = []
    y = []
    for o in olds:
        x.append(o)
        y.append(formula.sigmoid_midpoint(o))

    plt.plot(x, y)

    ax.grid(color='k', alpha=0.15, which='major')

    plt.title('sigmoid_midpoint(old)')
    plt.xlabel('old')

    # ---GRAPH C.3---
    # Plotting sigmoid_steepness

    # Upper right subplot
    ax = plt.subplot2grid((6, 2), (2, 1), rowspan=1, colspan=1)

    olds = range(0, 25000)

    x = []
    y = []
    for o in olds:
        x.append(o)
        y.append(formula.sigmoid_steepness(o))

    plt.plot(x, y)

    ax.grid(color='k', alpha=0.15, which='major')

    plt.title('sigmoid_steepness(old)')
    plt.xlabel('old')

    # ---GRAPH D---
    # Plotting return multiplier thresholds

    # A recursive function to quickly find the threshold parameter value faster.
    #
    # Given:
    #  - function f(a, b)
    #  - fixed input value b
    #  - range of input values min_a to max_a
    #  - target output value
    #
    # The find_threshold function basically does a binary search from min_a to max_a
    # until it finds a value of 'a' such that f(a, b) ~ 'target'. This corresponds
    # to the threshold value of 'a' where f(a, b) first exceeds 'target' (assuming
    # a monotonically increasing function, like the sigmoid function).
    def find_threshold(f, fixed_b, min_a, max_a, target):
        # print(f"min: {min_a}, max: {max_a}, target: {target}")

        if abs(max_a - min_a) <= 1:
            # print("Reached base case")

            v = f(min_a, fixed_b)
            # print(f"v: {v}")

            if abs(v - target) < 0.01:
                # print("Close enough!")
                return min_a
            else:
                # print("Nope, returning None")
                return None

        mid_a = (max_a + min_a) / 2
        # print(f"mid: {mid_a}")

        v = f(mid_a, fixed_b)
        # print(f"v: {v}")

        if v < target:
            # print("Below the target - guessing higher")
            return find_threshold(f, fixed_b, mid_a, max_a, target)
        else:
            # print("Above the target - guessing lower")
            return find_threshold(f, fixed_b, min_a, mid_a, target)

    # And here's the previous approach, just in case you prefer it or want
    # to compare results against the new version.
    def find_threshold_old(f, fixed_b, min_a, max_a, target):
        for a in range(min_a, max_a, 1):
                if a > fixed_b:
                    multA = formula.calculate(a, fixed_b)
                    multB = formula.calculate(a+1, fixed_b)
                    if multA < target and multB >= target:
                        return a
        return None

    # Bottom right subplot
    ax = plt.subplot2grid((6, 2), (3, 1), rowspan=3, colspan=2)

    olds = range(0, 1000, 1)
    min_n = 0
    max_n = 10000

    xy = []
    x2y2 = []
    mult_threshs = [1, 1.25, 1.5, 2, 3, 4, 5]
    for M in mult_threshs:
        x = []
        y = []
        x2 = []
        y2 = []
        for o in olds:
            # n = find_threshold_old(formula.calculate, o, min_n, max_n, M)
            n = find_threshold(formula.calculate, o, min_n, max_n, M)
            if n:
                x.append(o)
                x2.append(o)
                y.append(n)
                y2.append(n-o)

        xy.append([x,y])
        x2y2.append([x2,y2])

    for (x, y) in x2y2:
        plt.plot(x, y)

    ax.legend(['break-even','1.25x','1.5x','x2','x3','x4','x5'])

    plt.grid(color='k', alpha=0.15, which='major')
    plt.title('1-8 Factor thresholds')
    plt.xlabel('old')
    plt.ylabel('delta')

    plt.tight_layout()
    fig.set_size_inches(18, 18)
    fig.savefig('all_plot.png')
    # plt.show()

if __name__ == "__main__":
    main()
