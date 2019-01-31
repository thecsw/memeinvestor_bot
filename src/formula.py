import math

from fastnumbers import fast_float

def calculate(new, old):
    new = fast_float(new)
    old = fast_float(old)

    # Treat anything below 0 upvotes as 0 upvotes
    if old < 0:
        old = 0
    if new < 0:
        new = 0

    # Compute gain
    delta = new - old

    # Treat negative gain as no gain
    if delta < 0:
        delta = 0

    # Compute the maximum of the sigmoid
    sig_max = sigmoid_max(old)

    # Compute the midpoint of the sigmoid
    sig_mp = sigmoid_midpoint(old)

    # Compute the steepness of the sigmoid
    sig_stp = sigmoid_steepness(old)

    # Calculate return
    factor = sigmoid(delta, sig_max, sig_mp, sig_stp)

    return factor

def sigmoid(x, maxvalue, midpoint, steepness):
    arg = -(steepness * (x - midpoint))
    y = fast_float(maxvalue) / ( 1 + math.exp(arg) )
    return y

MAX_A = 1.2
MAX_B = 1.4
MAX_C = 7

def sigmoid_max(old):
    return MAX_A + MAX_B / ((old / MAX_C) + 1)

MID_A = 7
MID_B = 500
MID_M = 25000

def sigmoid_midpoint(old):
    return linear_interpolate(old, 0, MID_M, MID_A, MID_B)

STEEP_A = 0.1
STEEP_C = 100

def sigmoid_steepness(old):
    return STEEP_A / ((old / STEEP_C) + 1)

def linear_interpolate(x, x_0, x_1, y_0, y_1):
    m = (y_1 - y_0) / fast_float(x_1 - x_0)
    c = y_0
    y = (m * x) + c
    return y
