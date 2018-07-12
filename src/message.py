import datetime
import time

import config

# This message will be sent if an account has been
# successfully created
create_org = """
*Account created!*

Thank you %USERNAME% for creating a bank account in r/MemeEconomy!

Your current balance is %BALANCE% MemeCoins.
"""

def modify_create(username, balance):
    create = create_org
    create = create.replace("%USERNAME%", str(username))
    create = create.replace("%BALANCE%", str(balance))
    return create

# This message will be sent if a user tries to create an account but already
# has one.
create_exists_org = """
I love the enthusiasm, but you've already got an account!
"""

# This message will be sent when an investment
# was successful

invest_org = """
*%AMOUNT% MemeCoins were successfully invested!*

You bought in at %ENTRY% upvotes.

Your new balance is %BALANCE% MemeCoins.

In 4 hours your investment will be evaluated and I will update this comment. Stay tuned!
"""

def modify_invest(amount, entry, balance):
    invest = invest_org
    invest = invest.replace("%AMOUNT%", str(amount))
    invest = invest.replace("%ENTRY%", str(entry))
    invest = invest.replace("%BALANCE%", str(balance))
    return invest

invest_return_org = """
%INVESTMENT%

UPDATE: Your investment has matured at %UPVOTES_NOW% upvotes. It was successful!

This investment has brought you %WIN% MemeCoins (%PROFIT%).

Your current balance is %BALANCE% MemeCoins.

^(formula v3)
"""

def modify_invest_return(text, upvotes_now, win, profit, balance):
    invest_return = invest_return_org
    invest_return = invest_return.replace("%INVESTMENT%", str(text))
    invest_return = invest_return.replace("%UPVOTES_NOW%", str(upvotes_now))
    invest_return = invest_return.replace("%WIN%", str(win))
    invest_return = invest_return.replace("%PROFIT%", str(profit))
    invest_return = invest_return.replace("%BALANCE%", str(balance))
    return invest_return

invest_break_even_org = """
%INVESTMENT%

UPDATE: Your investment has matured at %UPVOTES_NOW% upvotes. It broke even!

This investment has brought you %NUMBER% MemeCoins (%PROFIT%).

Your current balance is %BALANCE% MemeCoins.

^(formula v3)
"""

def modify_invest_break_even(text, upvotes_now, coins, profit, balance):
    invest_return = invest_break_even_org
    invest_return = invest_return.replace("%INVESTMENT%", str(text))
    invest_return = invest_return.replace("%UPVOTES_NOW%", str(upvotes_now))
    invest_return = invest_return.replace("%NUMBER%", str(coins))
    invest_return = invest_return.replace("%PROFIT%", str(profit))
    invest_return = invest_return.replace("%BALANCE%", str(balance))
    return invest_return

invest_lose_org = """
%INVESTMENT%

UPDATE: Your investment has matured at %UPVOTES_NOW% upvotes. It was unsuccessful!

You lost %NUMBER% MemeCoins (%PROFIT%).

Your current balance is %BALANCE% MemeCoins.

^(formula v3)
"""

def modify_invest_lose(text, upvotes_now, lost, profit, balance):
    invest_lose = invest_lose_org
    invest_lose = invest_lose.replace("%INVESTMENT%", str(text))
    invest_lose = invest_lose.replace("%UPVOTES_NOW%", str(upvotes_now))
    invest_lose = invest_lose.replace("%NUMBER%", str(lost))
    invest_lose = invest_lose.replace("%PROFIT%", str(profit))
    invest_lose = invest_lose.replace("%BALANCE%", str(balance))
    return invest_lose
    
# If funds are insufficient to make an investment
# say that
insuff_org = """
You do not have enough MemeCoins to make the investment.
"""

# Message if you are broke
broke_org = """
Welp, you are broke.

Your balance has been reset to 100 MemeCoins. Be careful next time.

You have gone bankrupt %NUMBER% time(s).
"""

def modify_broke(times):
    broke = broke_org
    broke = broke.replace("%NUMBER%", str(times))
    return broke

# Message if you are broke and have active investments
broke_active_org = """
You still have %ACTIVE% investment(s).

You need to wait until they are fully evaluated.
"""

def modify_broke_active(active):
    broke_active = broke_active_org
    broke_active = broke_active.replace("%ACTIVE%", str(active))
    return broke_active
    
# Message if you are broke and have more than 100 MemeCoins
broke_money_org = """
You are not broke. You still have %AMOUNT% MemeCoins.
"""

def modify_broke_money(amount):
    broke_money = broke_money_org
    broke_money = broke_money.replace("%AMOUNT%", str(amount))
    return broke_money
    
help_org = """
*Welcome to MemeInvestment!*

I am a bot that will help you invest in memes and make a fortune out of it!

Here is a list of commands that summon me:

1. !create - creates a bank account for you with a new balance of 1000 MemeCoins.

2. !invest AMOUNT - invests AMOUNT in the meme (post). 4 hours after the investment, the meme growth will be evaluated and your investment can profit you or make you bankrupt. Minimum possible investment is 100 MemeCoins.

3. !balance - returns your current balance.

4. !active - returns a number of active investments.

5. !broke - only if your balance is less than 100 MemeCoins and you do not have any active investments, declares bankruptcy on your account and sets your balance to 100 MemeCoins (minimum possible investment).

6. !market - gives an overview for the whole Meme market.

7. !top - gives a list of the users with the largest account balances.

8. !ignore - ignores the whole message.

9. !help - returns this help message.

For market stats and more information, visit [memes.market](https://memes.market).

You can help improve me by contributing to my source code on [GitHub](https://github.com/MemeInvestor/memeinvestor_bot).
"""

no_account_org = """
You do not have permission to perform this operation.

Please create an account with the !create command.
"""

balance_org = """
Currently, your account balance is %BALANCE% MemeCoins.
"""

def modify_balance(balance):
    balance_t = balance_org
    balance_t = balance_t.replace("%BALANCE%", str(balance))
    return balance_t

active_org = """
You have %NUMBER% active investments:

%INVESTMENTS_LIST%
"""

def modify_active(active_investments):
    if len(active_investments) == 0:
        return "You don't have any active investments right now."

    investments_strings = []
    i = 1
    for inv in active_investments:
        seconds_remaining = inv.time + config.investment_duration - time.time()
        td = datetime.timedelta(seconds=seconds_remaining)
        remaining_string = str(td).split(".")[0]
        post_url = f"https://www.reddit.com/r/MemeEconomy/comments/{inv.post}"
        inv_string = f"[#{i}]({post_url}): {inv.amount} M¢ @ {inv.upvotes} upvotes ({remaining_string} remaining)"
        investments_strings.append(inv_string)
        i += 1
    investments_list = "\n\n".join(investments_strings)

    active_t = active_org
    active_t = active_t.replace("%NUMBER%", str(len(active_investments)))
    active_t = active_t.replace("%INVESTMENTS_LIST%", investments_list)
    return active_t

min_invest_org = """
The minimum possible investment is 100 MemeCoins.
"""

market_org = """
The market has %NUMBER% active investments.

All investors currently possess %MONEY% MemeCoins.

There are %HODL% MemeCoins detained in investments.
"""

def modify_market(inves, cap, invs_cap):
    market = market_org
    market = market.replace("%NUMBER%", str(inves))
    market = market.replace("%MONEY%", str(cap))
    market = market.replace("%HODL%", str(invs_cap))
    return market

# Message used for !top command
top_org = """
Investors with the highest net worth (balance + active investments):

%TOP_STRING%
"""

def modify_top(leaders):
    top_string = ""
    for l in leaders:
        top_string = f"{top_string}\n\n{l.name}: {int(l.networth)} MemeCoins"

    top_response = top_org
    top_response = top_response.replace("%TOP_STRING%", top_string)
    return top_response

deleted_comment_org = """
Where did he go?

Whatever, investment is lost.
"""

invest_place_here = """
**ALL YOUR INVESTMENTS GO HERE**

To prevent thread spam and other natural disasters, please invoke all your commands by replying to this comment.

If you don't invoke your command here, you may receive a penalty or your account may be suspended. We are respected investors, so let's keep our community clean! Reply directly to this comment and not to other investors' comments/commands.

**ONLY DIRECT REPLIES TO THE BOT WILL BE PROCESSED**

For market stats and more information, visit [memes.market](https://memes.market).
"""

inside_trading_org = """
You can't invest in your own memes, insider trading is not allowed!
"""
