import math

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

import formula

def main():
    old = 3
    deltas = range(500)
    render_graph(old, deltas, 'paper_figure_1.png')

    old = 500
    deltas = range(500)
    render_graph(old, deltas, 'paper_figure_2.png')

def render_graph(old, deltas, filename):
    fig = plt.figure(figsize=(6,4), dpi=300)

    ax = plt.subplot(111)

    x = []
    y = []
    for d in deltas:
        x.append(d)
        y.append(formula.calculate(old+d, old))

    plt.plot(x, y)

    ax.grid(color='k', alpha=0.15, which='major')
    ax.set_ylim([0, 3])

    plt.xlabel('Upvotes gained')
    plt.ylabel('Investment return factor')
    plt.tight_layout()

    fig.savefig(filename)

if __name__ == "__main__":
    main()
