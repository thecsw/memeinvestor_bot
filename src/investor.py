import time

class Post:

    """
    This is a Post class that stores information
    on one submission from Investment class instance

    Attributes:
    1. ID - submission id

    2. upvotes - the initial number of upvotes

    """
    
    def __init__(self, ID, upvotes):
        self.ID = ID
        self.upvotes = upvotes

    def get_ID(self):
        return self.ID

    def get_upvotes(self):
        return self.upvotes
        
class Investment:

    """
    This class holds data for only 1 investment.
    The following attributes are:
    
    1. post - is the submission's id
    
    2. upvotes - is the amount of upvotes during 
    the time of object allocation

    3. name - is the name (user id) of the investor
    who owns the following investment

    4. amount = is the amount of memecoint the 
    Investor class instance invested in the post

    """
    
    def __init__(self, post, upvotes, name, amount):
        self.post = Post(post, upvotes)
        self.name = name
        self.amount = amount
        self.done = False
        self.time = time.time()
        self.head = self.post.get_upvotes()
        self.growth = []
        
    def check(self):
        change = time.time() - self.get_time()

        # 6 hours of waiting
        if (change > 6 * 60 * 60):
            return True
        return False
        
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

    def get_head(self):
        return self.head

    def set_head(self, head):
        self.head = head
    
    def get_growth(self):
        return self.growth

    def get_post_upvotes(self):
        return self.post.get_upvotes()
    
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
        self.active = 0
        self.completed = 0
        self.invests = []

    def invest(self, post, upvotes, amount):
        if (self.get_balance() < amount):
            return False
        self.balance -= amount
        self.invests.append(Investment(post, upvotes, self.name, amount))
        self.active += 1
        return True
        
    def calculate(self, investment, upvotes):
        du = upvotes - investment.post.get_upvotes()

        if (du < 1000):
            self.proft(investment, False, 0)
            
        if (du >= 1000 and du < 1500):
            self.profit(investment, True, 1)
            
        if (du >= 1500 and du < 2500):
            self.profit(investment, True, 1.10)

        if (du >= 2500 and du < 5000):
            self.profit(investment, True, 1.25)

        if (du >= 5000 and du < 10000):
            self.profit(investment, True, 1.50)

        if (du >= 10000 and du < 15000):
            self.profit(investment, True, 1.75)

        if (du >= 15000):
            self.proft(investment, True, 2.00)
            
    def profit(self, investment, success, multiplier):
        if (success):
            self.balance += investment.amount
            self.balance *= multiplier
        investment.done = True
        self.completed += 1
        self.active -= 1

    def get_name(self):
        return self.name

    def set_name(self, nam):
        self.name = nam
    
    def get_balance(self):
        return self.balance

    def set_balance(self, balanc):
        self.balance = balanc
    
    def get_active(self):
        return self.active

    def set_active(self, activ):
        self.active = activ
    
    def get_completed(self):
        return self.completed

    def set_completed(self, complete):
        self.completed = complete
    
    def get_invests(self):
        return self.invests
    
    def get(self):
        return [self.name, self.balance, self.invests, self.completed]
