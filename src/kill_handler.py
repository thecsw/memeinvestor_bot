import signal

# Handles SIGTERM (15)
class KillHandler():    
    def __init__(self):
        self.killed = False
        signal.signal(signal.SIGTERM, self.kill)
        
    def kill(self, signum, frame):
        self.killed = True
