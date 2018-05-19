import time
        
class Investment:
    
    def __init__(self, post, name, amount):
        self.post = post
        self.name = name
        self.amount = amount
        self.done = False
        self.time = time.time()

    def get_post(self):
        return self.post

    def get_name(self):
        return self.name

    def get_amount(self):
        return self.amount

    def get_done(self):
        return self.done
        
    def get_time(self):
        return self.time

    def get(self):
        return [self.post, self.name, self.amount, self.done, self.time]
    
class Investor:

    def __init__(self, name, balance):
        self.name = name
        self.balance= balance
        self.completed = 0
        self.invests = []

    def invest(self, post, amount):
        self.balance -= amount
        self.invests.append(Investment(post, self.name, amount))

    def profit(self, investment, amount):
        self.balance += amount
        investment.done = True
        self.completed += 1
        
    def get_name(self):
        return self.name
    
    def get_balance(self):
        return self.balance

    def get_completed(self):
        return self.completed
    
    def get_invests(self):
        return self.invests

    def get(self):
        return [self.name, self.balance, self.invests, self.completed]
