#!/usr/bin/env python


# In this file: overimpose several xy plots of similar magnitudes.


import matplotlib.pyplot as plt
import numpy as np
import sys


COLORS = ['r-', 'g-', 'b-']
MAX = 6e-4


def read_file(fname):
    print('FNAME', fname)
    with open(fname) as file:
        ret = [float(line) for line in file if line != '\n']
    return ret


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth


def plot_file(fname, color='r-', ymax=0):
    y = read_file(fname)[50:]  # Drop outliers.
    x = range(len(y))

    if ymax > 0:
        plt.gca().set_ylim([0, ymax])

    # plt.plot(x, y, 'o')
    plt.plot(x, smooth(y, int(1e3)), color, label=fname)


if __name__ == '__main__':
    for index, fname in enumerate(sys.argv[1:]):
        plot_file(fname, color=COLORS[index%len(COLORS)], ymax=MAX)
    plt.legend()
    plt.show()
