"""
time is used to record time
"""
import time

class Stopwatch():
    """
    The class is pretty self-explanatory. This is a class that
    lets us to record time in a convenient way
    """
    def __init__(self):
        self.reset()
        self.previous_time = -1

    def reset(self):
        self.previous_time = time.perf_counter()

    # Returns the seconds elapsed since the last call to reset or measure
    def measure(self):
        new_time = time.perf_counter()
        elapsed = new_time - self.previous_time
        self.previous_time = new_time
        return elapsed
