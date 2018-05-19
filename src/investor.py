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

    """
    This is a class Investor where 1 instance stores data
    on one individual meme investor.
    The following attributes are defined when Investor
    class instance is created:

    1. name - this is the user's unique subreddit name
    or in common, the reddit user id. u/

    2. balance - the amount of memecoins the user 
    currently has in his bank.

    3. completed - the number of completed investments.
    Doesn't matter, successfull or unseccussfull.

    4. invests - is the array of Investment class
    instances that holds every data on every investment
    that the user made.

    For each attribute there is an appropriate GET method.
    """
    
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
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

