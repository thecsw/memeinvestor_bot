# Standard scripts
import time
from threading import Thread

# Third-party library
import praw

# Our own scripts and files
import config
from investor import *
import message
import utils

# Reddit instance initialization
reddit = praw.Reddit(client_id=config.client_id,
                     client_secret=config.client_secret,
                     username=config.username,
                     password=config.password,
                     user_agent=config.user_agent)

# Subreddit initialization
subreddit_name = "pewds_test"
subreddit = reddit.subreddit(subreddit_name)

commands = ["!create", "!invest", "!balance", "!help", "!broke"]
starter = 1000

users = utils.read_investors()

print(list(users.keys()))
print(list(users.values())[-1].get())
done = []
awaiting = []

def help(comment):
    comment.reply(message.help_org)

def create(comment, author):
    users[author] = Investor(author, starter)
    comment.reply(message.modify_create(author, users[author].get_balance()))
    utils.write_investors(users)
    
def invest(comment, author, text):
    post = comment.submission
    upvotes = post.ups
    investor = users[author]
    
    # If it can't extract the invest amount, abandon the operation
    try:
        invest = int(float(text.replace("!invest", "").replace(" ", "")))
    except ValueError as ve:
        return False
    
    # Returns false if there is not enough money
    new_investment = investor.invest(post, upvotes, invest)
    
    if (new_investment):
        comment.reply(message.modify_invest(invest, investor.get_balance()))
    else:
        comment.reply(message.insuff_org)

def balance(comment, author):
    investor = users[author] 
    balance = investor.get_balance()
    comment.reply(message.modify_balance(balance))

def broke(comment, author):
    investor = users[author]
    balance = investor.get_balance()
    active = investor.get_active()

    if (balance < 100):
        if (active == 0):
            comment.reply(message.broke_org)
        else:
            comment.reply(message.modify_broke_active(active))
    else:
        comment.reply(message.modify_broke_money(balance))
            
def comment_thread():

    for comment in subreddit.stream.comments():
        author = comment.author.name.lower()
        if ("bot" in author):
            continue
        
        text = comment.body.lower()
        exist = author in list(users.keys())
        print("Author - {}\nText - {}\nExist? - {}\n\n".format(author, text, exist))

        if ("!help" in text):
            help(comment)
            continue
        
        # The !create command
        if (("!create" in text) and (not exist)):
            create(comment, author)
            continue
        
        # The !invest command
        if ("!invest" in text):
            if (exist):
                invest(comment, author, text)
                continue
            else:
                comment.reply(message.no_account_org)

        if ("!balance" in text):
            if (exist):
                balance()
                continue
            else:
                comment.reply(message.no_account_org)

        if ("!broke" in text):
            if (exist):
                broke(comment, author)
                continue
            else:
                comment.reply(message.no_account_org)

        time.sleep(20)

def check_investments():
    time.sleep(60)
    investment = awaiting[0]
    investor_id = investment.name
    investor = users[investor_id]
    post = investment.post.get_ID()
    upvotes = reddit.submission(post).ups

    if (investment.check()):
        investor.calculate(investment, upvotes)
        done.append(awaiting.pop(0))

def monitor_investments():

    for investment in awating:
        post = investment.post.get_ID()
        upvotes = reddit.submission(post).ups
        prev = investment.get_head()
        investment.set_head(upvotes)
        change = upvotes - prev
        investment.growth.append(change)

    time.sleep(60)

def threads():
    Thread(name="Comments", target=comment_thread).start()

if __name__ == "__main__":
    threads()
