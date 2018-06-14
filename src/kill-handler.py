import signal

# Handles SIGTERM (15)
class KillHandler():
    killed = False
    
    def __init__(self):
        signal.signal(signal.SIGTERM, self.kill)
        
    def kill(self):
        killed = True
