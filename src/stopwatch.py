import time

class Stopwatch():
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
