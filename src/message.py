import datetime
import time

import config

# This message will be sent if an account has been
# successfully created
create_org = """
*Account created!*

Thank you %USERNAME% for creating a bank account in r/MemeEconomy!

Your starting balance is %BALANCE% MemeCoins.
"""

def modify_create(username, balance):
    return create_org.\
        replace("%USERNAME%", str(username)).\
        replace("%BALANCE%", format(balance, ",d"))

# This message will be sent if a user tries to create an account but already
# has one.
create_exists_org = """
I love the enthusiasm, but you've already got an account!
"""

# This message will be sent when an investment
# was successful

invest_org = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% upvotes*

Your investment is active. I'll evaluate your return in 4 hours and update this comment. Stay tuned!

Your current balance is %BALANCE% MemeCoins.
"""

def modify_invest(amount, initial_upvotes, new_balance):
    return invest_org.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%BALANCE%", format(new_balance, ",d"))

invest_win_org = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% upvotes*

UPDATE: Your investment has matured. It was successful! You profited %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins returned @ %FINAL_UPVOTES% upvotes*

Your new balance is %BALANCE% MemeCoins.

^(formula v3)
"""

invest_lose_org = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% upvotes*

UPDATE: Your investment has matured. It was unsuccessful! You lost %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins returned @ %FINAL_UPVOTES% upvotes*

Your new balance is %BALANCE% MemeCoins.

^(formula v3)
"""

invest_break_even_org = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% upvotes*

UPDATE: Your investment has matured. It broke even! You profited %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins returned @ %FINAL_UPVOTES% upvotes*

Your new balance is %BALANCE% MemeCoins.

^(formula v3)
"""

def modify_invest_return(amount, initial_upvotes, final_upvotes, returned, profit, percent_str, new_balance):
    if profit > 0:
        original = invest_win_org
    elif profit < 0:
        original = invest_lose_org
        profit *= -1
    else:
        original = invest_break_even_org

    return original.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%FINAL_UPVOTES%", format(final_upvotes, ",d")).\
        replace("%RETURNED%", format(returned, ",d")).\
        replace("%PROFIT%", format(profit, ",d")).\
        replace("%PERCENT%", format(percent_str)).\
        replace("%BALANCE%", format(new_balance, ",d"))

invest_capped_org = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% upvotes*

UPDATE: Your investment has matured at %FINAL_UPVOTES% upvotes, profiting %PROFIT% MemeCoins (%PERCENT%).

**Congratulations,** you've reached the maximum balance! You've triumphed over your competition in the
meme marketplace, and your wealth is inconceivable! Indeed, future generations shall remember you as a titan
of meme industry.

*"And Alexander wept, for there were no more worlds to conquer."* (...yet)

Your current balance is %BALANCE% MemeCoins (the maximum balance).

^(formula v3)
"""

def modify_invest_capped(amount, initial_upvotes, final_upvotes, returned, profit, percent_str, new_balance):
    return invest_capped_org.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%FINAL_UPVOTES%", format(final_upvotes, ",d")).\
        replace("%PROFIT%", format(profit, ",d")).\
        replace("%PERCENT%", str(percent_str)).\
        replace("%BALANCE%", format(new_balance, ",d"))

# If funds are insufficient to make an investment
# say that
insuff_org = """
You do not have enough MemeCoins to make that investment.

Your current balance is %BALANCE% MemeCoins.
"""

def modify_insuff(balance_t):
    return insuff_org.\
        replace("%BALANCE%", format(balance_t, ",d"))

# Message if you are broke
broke_org = """
Welp, you are broke.

Your balance has been reset to 100 MemeCoins. Be careful next time.

You have gone bankrupt %NUMBER% time(s).
"""

def modify_broke(times):
    return broke_org.\
        replace("%NUMBER%", str(times))

# Message if you are broke and have active investments
broke_active_org = """
You still have %ACTIVE% investment(s).

You need to wait until they are fully evaluated.
"""

def modify_broke_active(active):
    return broke_active_org.\
        replace("%ACTIVE%", str(active))
    
# Message if you are broke and have more than 100 MemeCoins
broke_money_org = """
You are not broke. You still have %AMOUNT% MemeCoins.
"""

def modify_broke_money(amount):
    return broke_money_org.\
        replace("%AMOUNT%", format(amount, ",d"))
    
help_org = """
*Welcome to MemeInvestment!*

I am a bot that will help you invest in memes and make a fortune out of it!

Here is a list of commands that summon me:

1. !create - creates a bank account for you with a new balance of 1000 MemeCoins.

2. !invest AMOUNT - invests AMOUNT in the meme (post). 4 hours after the investment, the meme growth will be evaluated and your investment can profit you or make you bankrupt. Minimum possible investment is 100 MemeCoins.

3. !balance - returns your current balance.

4. !active - returns a list of your active investments.

5. !broke - only if your balance is less than 100 MemeCoins and you do not have any active investments, declares bankruptcy on your account and sets your balance to 100 MemeCoins (minimum possible investment).

6. !market - gives an overview for the whole Meme market.

7. !top - gives a list of the users with the largest account balances.

8. !ignore - ignores the whole message.

9. !help - returns this help message.

For market stats and more information, visit [memes.market](https://memes.market).

You can help improve me by contributing to my source code on [GitHub](https://github.com/MemeInvestor/memeinvestor_bot).
"""

balance_org = """
Currently, your account balance is %BALANCE% MemeCoins.
"""

def modify_balance(balance):
    return balance_org.\
        replace("%BALANCE%", format(balance, ",d"))

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

    return active_org.\
        replace("%NUMBER%", str(len(active_investments))).\
        replace("%INVESTMENTS_LIST%", investments_list)

min_invest_org = """
The minimum possible investment is 100 MemeCoins.
"""

market_org = """
The market has %NUMBER% active investments.

All investors currently possess %MONEY% MemeCoins.

There are %HODL% MemeCoins detained in investments.
"""

def modify_market(inves, cap, invs_cap):
    return market_org.\
        replace("%NUMBER%", format(int(inves), ",d")).\
        replace("%MONEY%", format(int(cap), ",d")).\
        replace("%HODL%", format(int(invs_cap), ",d"))

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
**INVESTMENTS GO HERE - ONLY DIRECT REPLIES TO ME WILL BE PROCESSED**

To prevent thread spam and other natural disasters, I only respond to direct replies. Other commands will be ignored and may be penalized. Let's keep our marketplace clean!

---

- Visit [memes.market](https://memes.market) for help, market statistics, and investor profiles.

- Visit /r/MemeInvestor_bot for questions or suggestions about me.
"""

inside_trading_org = """
You can't invest in your own memes, insider trading is not allowed!
"""

def modify_grant_success(grantee, badge):
    return f"Successfully granted badge `{badge}` to {grantee}!"

def modify_grant_failure(failure_message):
    return f"Oops, I couldn't grant that badge ({failure_message})"
