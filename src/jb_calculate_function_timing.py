import time
import timeit
from fastnumbers import fast_float

def calculate(new, old):

    # Multiplier is detemined by a power function of the relative change in upvotes
    # since the investment was made.
    # Functional form: y = x^m ;
    #    y = multiplier,
    #    x = relative growth: (change in upvotes) / (upvotes at time of investment),
    #    m = scale factor: allow curtailing high-growth post returns to make the playing field a bit fairer

    new = fast_float(new)
    old = fast_float(old)

    # Scale factor for multiplier
    scale_factor = 1 / fast_float(3)

    # Calculate relative change
    if old != 0:
        rel_change = (new - old) / abs(old)
    # If starting upvotes was zero, avoid dividing by zero
    else:
        rel_change = new

    mult = pow((rel_change+1), scale_factor)

    # Investment must grow by more than a threshold amount to win. Decide if
    # investment was successful and whether you get anything back at all.
    win_threshold = 1.2
    if mult > win_threshold:
        investment_success = True
        return_money = True
    elif mult > 1:
        investment_success = False
        return_money = True
    else:
        investment_success = False
        return_money = False

    # Investor gains money only if investment was successful. If mult
    # was below win_threshold but above 1 return factor is ratio of
    # difference between mult and 1 and difference between win_threshold and 1.
    # Otherwise, if mult was 1 or lower, get back nothing.
    if investment_success:
        factor = mult
    elif return_money:
        factor = (mult - 1)/(win_threshold - 1)
    else:
        factor = 0

    return factor
	
#function wrapper for call to calculate
def wrapped_calculate():
  return calculate(1342,235)

#MAIN
dt = timeit.timeit(wrapped_calculate,number=10000) / fast_float(10000)
print(dt)


