
# This is the general bot description, used in
# every message
bot_desc = """
_______________________
^(I am a MemeInvestor. I help you invest in memes. Improve me by contributing to source code!)

[Source code](https://github.com/thecsw/memeinvestor_bot)
"""

help_mess = """
^(For more information type !help)
"""

# This message will be sent if an account has been
# successfully created
create_org = """
*Account created!*

Thank you %USERNAME% for creating a bank account in r/MemeEconomy!

Your current balance is %BALANCE% MemeCoins.

%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

def modify_create(username, balance):
    create = create_org
    create = create.replace("%USERNAME%", str(username))
    create = create.replace("%BALANCE%", str(balance))
    return create

# This message will be sent when an investment
# was successful

invest_org = """
*%AMOUNT% MemeCoins were successfully invested!*

You bought in at %ENTRY% upvotes

Your new balance is %BALANCE% MemeCoins

In 4 hours your investment will be evaluated and I will update this comment. Stay tuned!

%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

def modify_invest(amount, entry, balance):
    invest = invest_org
    invest = invest.replace("%AMOUNT%", str(amount))
    invest = invest.replace("%ENTRY%", str(entry))
    invest = invest.replace("%BALANCE%", str(balance))
    return invest

invest_return_org = """
%INVESTMENT%

UPDATE: Your investment was successful!

This investment has brought you %WIN% MemeCoins. 

%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

def modify_invest_return(text, win):
    invest_return = invest_return_org
    invest_return = invest_return.replace("%INVESTMENT%", str(text))
    invest_return = invest_return.replace("%WIN%", str(win))
    return invest_return
    
invest_lose_org = """
%INVESTMENT%

UPDATE: Your investment was unsuccessful!

%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

def modify_invest_lose(text):
    invest_lose = invest_lose_org
    invest_lose = invest_lose.replace("%INVESTMENT%", str(text))
    return invest_lose
    
# If funds are insufficient to make an investment
# say that
insuff_org = """
You do not have enough MemeCoins to make the investment.

%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

# Message if you are broke
broke_org = """
Welp, you are broke.

Your balance has been reset to 100 MemeCoins. Be careful next time.

%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

# Message if you are broke and have active investments
broke_active_org = """
You still have %ACTIVE% investment(s).

You need to wait until they are fully evaluated.

%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

def modify_broke_active(active):
    broke_active = broke_active_org
    broke_active = broke_active.replace("%ACTIVE%", str(active))
    return broke_active
    
# Message if you are broke and have more than 100 MemeCoins
broke_money_org = """
You are not broke. You still have %AMOUNT% MemeCoins.

%DESCRIPTION%
""".replace("%DESCRIPTION%", help_mess)

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

7. !ignore - ignores the whole message.

8. !help - returns this help message.

%DESCRIPTION% 
""".replace("%DESCRIPTION%", bot_desc)

no_account_org = """
You do not have permission to make this operation.

Please create an account with !create command.

%DESCRIPTION% 
""".replace("%DESCRIPTION%", help_mess)

balance_org = """
Currently, your account balance is %BALANCE% MemeCoins.

%DESCRIPTION% 
""".replace("%DESCRIPTION%", help_mess)

def modify_balance(balance):
    balance_t = balance_org
    balance_t = balance_t.replace("%BALANCE%", str(balance))
    return balance_t

active_org = """
Currently, you have %NUMBER% active investments.

%DESCRIPTION% 
""".replace("%DESCRIPTION%", help_mess)

def modify_active(active):
    active_t = active_org
    active_t = active_t.replace("%NUMBER%", str(active))
    return active_t

min_invest_org = """
The minimum possible investment is 100 MemeCoins.

%DESCRIPTION% 
""".replace("%DESCRIPTION%", help_mess)

market_org = """
The market has %NUMBER% active investments.

All investors currently possess %MONEY% MemeCoins.

There are %HODL% MemeCoins detained in investments.

%DESCRIPTION% 
""".replace("%DESCRIPTION%", help_mess)

def modify_market(inves, cap, invs_cap):
    market = market_org
    market = market.replace("%NUMBER%", str(inves))
    market = market.replace("%MONEY%", str(cap))
    market = market.replace("%HODL%", str(invs_cap))
    return market

deleted_comment_org = """
Where did he go?

Whatever, investment is lost.
%DESCRIPTION% 
""".replace("%DESCRIPTION%", help_mess)
