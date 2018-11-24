"""
signal library allows us to send UNIX signals
"""
import signal

# Handles SIGTERM (15)
class KillHandler():
    """
    This class allows us to gracefully handle received SIGTERMs
    """
    def __init__(self):
        self.killed = False
        signal.signal(signal.SIGTERM, self.kill)

    def kill(self, signum, frame):
        self.killed = True
