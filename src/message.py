import datetime
import time

import config
import utils

INVESTMENT_DURATION_VAR = utils.investment_duration_string(config.INVESTMENT_DURATION)

# This message will be sent if an account has been
# successfully created
CREATE_ORG = """
*Account created!*

Thank you %USERNAME% for creating a bank account in r/MemeEconomy!

Your starting balance is **%BALANCE% MemeCoins**.
"""

def modify_create(username, balance):
    return CREATE_ORG.\
        replace("%USERNAME%", str(username)).\
        replace("%BALANCE%", format(balance, ",d"))

# This message will be sent if a user tries to create an account but already
# has one.
CREATE_EXISTS_ORG = """
I love the enthusiasm, but you've already got an account!
"""

# This message will be sent when an investment
# was successful

INVEST_ORG = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

Your investment is active. I'll evaluate your return in %TIME%and update this comment. Stay tuned!

Your current balance is **%BALANCE% MemeCoins**.
""".replace("%TIME%", INVESTMENT_DURATION_VAR).\
    replace("%UPVOTES_WORD%", utils.upvote_string())

def modify_invest(amount, initial_upvotes, new_balance):
    return INVEST_ORG.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%BALANCE%", format(new_balance, ",d"))

INVEST_WIN_ORG = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Your investment has matured. It was successful! You profited %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins returned @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Your new balance is **%BALANCE% MemeCoins**.

^(formula v3)
""".replace("%UPVOTES_WORD%", utils.upvote_string())

INVEST_LOSE_ORG = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Your investment has matured. It was unsuccessful! You lost %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins returned @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Your new balance is **%BALANCE% MemeCoins**.

^(formula v3)
""".replace("%UPVOTES_WORD%", utils.upvote_string())

INVEST_BREAK_EVEN_ORG = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Your investment has matured. It broke even! You profited %PROFIT% MemeCoins (%PERCENT%).

*%RETURNED% MemeCoins returned @ %FINAL_UPVOTES% %UPVOTES_WORD%*

Your new balance is **%BALANCE% MemeCoins**.

^(formula v3)
""".replace("%UPVOTES_WORD%", utils.upvote_string())

def modify_invest_return(amount, initial_upvotes,
                         final_upvotes, returned,
                         profit, percent_str, new_balance):
    if profit > 0:
        original = INVEST_WIN_ORG
    elif profit < 0:
        original = INVEST_LOSE_ORG
        profit *= -1
    else:
        original = INVEST_BREAK_EVEN_ORG

    return original.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%FINAL_UPVOTES%", format(final_upvotes, ",d")).\
        replace("%RETURNED%", format(returned, ",d")).\
        replace("%PROFIT%", format(profit, ",d")).\
        replace("%PERCENT%", format(percent_str)).\
        replace("%BALANCE%", format(new_balance, ",d"))

INVEST_CAPPED_ORG = """
*%AMOUNT% MemeCoins invested @ %INITIAL_UPVOTES% %UPVOTES_WORD%*

UPDATE: Your investment has matured at %FINAL_UPVOTES% %UPVOTES_WORD%, profiting %PROFIT% MemeCoins (%PERCENT%).

**Congratulations,** you've reached the maximum balance! You've triumphed over your competition in the
meme marketplace, and your wealth is inconceivable! Indeed, future generations shall remember you as a titan
of meme industry.

*"And Alexander wept, for there were no more worlds to conquer."* (...yet)

Your current balance is **%BALANCE% MemeCoins** (the maximum balance).

^(formula v3)
""".replace("%UPVOTES_WORD%", utils.upvote_string())

def modify_invest_capped(amount, initial_upvotes,
                         final_upvotes, returned,
                         profit, percent_str, new_balance):
    return INVEST_CAPPED_ORG.\
        replace("%AMOUNT%", format(amount, ",d")).\
        replace("%INITIAL_UPVOTES%", format(initial_upvotes, ",d")).\
        replace("%FINAL_UPVOTES%", format(final_upvotes, ",d")).\
        replace("%PROFIT%", format(profit, ",d")).\
        replace("%PERCENT%", str(percent_str)).\
        replace("%BALANCE%", format(new_balance, ",d"))

# If funds are insufficient to make an investment
# say that
INSUFF_ORG = """
You do not have enough MemeCoins to make that investment.

Your current balance is **%BALANCE% MemeCoins**.

If you have less than 100 MemeCoins and no active investments, try running `!broke`!
"""

def modify_insuff(balance_t):
    return INSUFF_ORG.\
        replace("%BALANCE%", format(balance_t, ",d"))

# Message if you are broke
BROKE_ORG = """
Welp, you are broke.

Your balance has been reset to 100 MemeCoins. Be careful next time.

You have gone bankrupt %NUMBER% time(s).
"""

def modify_broke(times):
    return BROKE_ORG.\
        replace("%NUMBER%", str(times))

# Message if you are broke and have active investments
BROKE_ACTIVE_ORG = """
You still have %ACTIVE% investment(s).

You need to wait until they are fully evaluated.
"""

def modify_broke_active(active):
    return BROKE_ACTIVE_ORG.\
        replace("%ACTIVE%", str(active))

# Message if you are broke and have more than 100 MemeCoins
BROKE_MONEY_ORG = """
You are not broke. You still have **%AMOUNT% MemeCoins**.
"""

def modify_broke_money(amount):
    return BROKE_MONEY_ORG.\
        replace("%AMOUNT%", format(amount, ",d"))

HELP_ORG = """
*Welcome to MemeInvestment!*

I am a bot that will help you invest in memes and make a fortune out of it!

Here is a list of commands that summon me:

1. `!create` - creates a bank account for you with a new balance of 1000 MemeCoins.

2. `!invest AMOUNT` - invests AMOUNT in the meme (post). 4 hours after the investment, the meme growth will be evaluated and your investment can profit you or make you bankrupt. Minimum possible investment is 100 MemeCoins.

3. `!balance` - returns your current balance.

4. `!active` - returns a list of your active investments.

5. `!broke` - only if your balance is less than 100 MemeCoins and you do not have any active investments, declares bankruptcy on your account and sets your balance to 100 MemeCoins (minimum possible investment).

6. `!market` - gives an overview for the whole Meme market.

7. `!top` - gives a list of the users with the largest account balances.

8. `!ignore` - ignores the whole message.

9. `!help` - returns this help message.

For market stats and more information, visit [memes.market](https://memes.market).

You can help improve me by contributing to my source code on [GitHub](https://github.com/MemeInvestor/memeinvestor_bot).
"""

BALANCE_ORG = """
Currently, your account balance is **%BALANCE% MemeCoins**.
"""

def modify_balance(balance):
    return BALANCE_ORG.\
        replace("%BALANCE%", format(balance, ",d"))

ACTIVE_ORG = """
You have %NUMBER% active investments:

%INVESTMENTS_LIST%
"""

def modify_active(active_investments):
    if not active_investments:
        return "You don't have any active investments right now."

    investments_strings = []
    i = 1
    for inv in active_investments:
        seconds_remaining = inv.time + config.INVESTMENT_DURATION - time.time()
        if seconds_remaining > 0:
            td = datetime.timedelta(seconds=seconds_remaining)
            remaining_string = str(td).split(".")[0] + " remaining"
        else:
            remaining_string = "processing"
        post_url = f"https://www.reddit.com/r/MemeEconomy/comments/{inv.post}"
        inv_string = f"[#{i}]({post_url}): {inv.amount} M¢ @ {inv.upvotes} %UPVOTES_WORD% ({remaining_string})"\
            .replace("%UPVOTES_WORD%", utils.upvote_string())
        investments_strings.append(inv_string)
        i += 1
    investments_list = "\n\n".join(investments_strings)

    return ACTIVE_ORG.\
        replace("%NUMBER%", str(len(active_investments))).\
        replace("%INVESTMENTS_LIST%", investments_list)

MIN_INVEST_ORG = """
The minimum possible investment is 100 MemeCoins.
"""

MARKET_ORG = """
The market has **%NUMBER%** active investments.

All investors currently possess **%MONEY% MemeCoins**.

There are %HODL% MemeCoins** detained in investments.
"""

def modify_market(inves, cap, invs_cap):
    return MARKET_ORG.\
        replace("%NUMBER%", format(int(inves), ",d")).\
        replace("%MONEY%", format(int(cap), ",d")).\
        replace("%HODL%", format(int(invs_cap), ",d"))

# Message used for !top command
TOP_ORG = """
Investors with the highest net worth (balance + active investments):

%TOP_STRING%
"""

def modify_top(leaders):
    top_string = ""
    for leader in leaders:
        top_string = f"{top_string}\n\n{leader.name}: {int(leader.networth)} MemeCoins"

    top_response = TOP_ORG
    top_response = top_response.replace("%TOP_STRING%", top_string)
    return top_response

DELETED_COMMENT_ORG = """
Where did he go?

Whatever, investment is lost.
"""

INVEST_PLACE_HERE_NO_FEE = """
**INVESTMENTS GO HERE - ONLY DIRECT REPLIES TO ME WILL BE PROCESSED**

To prevent thread spam and other natural disasters, I only respond to direct replies. Other commands will be ignored and may be penalized. Let's keep our marketplace clean!

---

- Visit [memes.market](https://memes.market) for help, market statistics, and investor profiles.

- Visit /r/MemeInvestor_bot for questions or suggestions about me.
"""

INVEST_PLACE_HERE = """
**INVESTMENTS GO HERE - ONLY DIRECT REPLIES TO ME WILL BE PROCESSED**

To prevent thread spam and other natural disasters, I only respond to direct replies. Other commands will be ignored and may be penalized. Let's keep our marketplace clean!

The author of this post paid **%MEMECOIN% MemeCoins** to post this.

---

- Visit [memes.market](https://memes.market) for help, market statistics, and investor profiles.

- Visit /r/MemeInvestor_bot for questions or suggestions about me.
"""

def modify_invest_place_here(amount):
    return INVEST_PLACE_HERE.\
        replace("%MEMECOIN%", format(int(amount), ",d"))

INSIDE_TRADING_ORG = """
You can't invest in your own memes, insider trading is not allowed!
"""

def modify_grant_success(grantee, badge):
    return f"Successfully granted badge `{badge}` to {grantee}!"

def modify_grant_failure(failure_message):
    return f"Oops, I couldn't grant that badge ({failure_message})"

NO_ACCOUNT_POST_ORG = """
You need an account to post a meme. Please reply to one of my comments with `!create`.

For more information please type `!help`
"""

PAY_TO_POST_ORG = """
Due to latest regulations, in order to post a meme you should pay 6% tax with minimum of 250 MemeCoins.

If you can't afford it, your post will be deleted. Nothing personal, kiddo. Only Meme Street business.

When you get enough cash, resubmit your meme with a new post.

Your current balance is **%MEMECOINS% MemeCoins**.
"""

def modify_pay_to_post(balance):
    return PAY_TO_POST_ORG.\
        replace("%MEMECOINS%", str(balance))

MAINTENANCE_ORG = """
**The bot is under maintenance due to technical reasons.**

**Expect it to be back online soon. (Several hours)**

**Sorry for any inconvenience caused.**
"""

firm_none_org = """
You are not in a firm.

You can create a new one with the **!createfirm <FIRM NAME>** command, or request to join one with **!joinfirm <FIRM NAME>**.
"""

firm_org = """
Firm: **%FIRM_NAME%**

Your Rank: **%RANK%**

----

## Members:

*CEO:*
%CEO%

*Executives:*
%EXECS%

*Floor Traders:*
%TRADERS%

----

You can leave this firm with the **!leavefirm** command.
"""

rank_strs = {
    "ceo": "CEO",
    "exec": "Executive",
    "": "Floor Trader"
}

def modify_firm(rank, firm, ceo, execs, traders):
    rank_str = rank_strs[rank]
    return firm_org.\
        replace("%RANK%", rank_str).\
        replace("%FIRM_NAME%", firm.name).\
        replace("%CEO%", ceo).\
        replace("%EXECS%", execs).\
        replace("%TRADERS%", traders)

createfirm_exists_failure_org = """
You are already in a firm: **%FIRM_NAME%**

Please leave this firm using the *!leavefirm* command before creating a new one.
"""

def modify_createfirm_exists_failure(firm_name):
    return createfirm_exists_failure_org.\
        replace("%FIRM_NAME%", firm_name)

createfirm_format_failure_org = """
Firm names must be between 4 and 32 characters long, using only alphanumeric characters, spaces, dashes, and underscores.
"""

createfirm_nametaken_failure_org = """
This firm name is already taken, please try again with a new one.
"""

createfirm_org = """
The new firm has been created successfully.

You are the firm's CEO and you have the ability to
"""

leavefirm_none_failure_org = """
You are not in a firm.
"""

leavefirm_ceo_failure_org = """
You are currently the CEO of your firm, so you are not allowed to leave.

If you really want to leave, you will need to first demote yourself by promoting an executive member to CEO with the **!promote <username>** command.
"""

leavefirm_org = """
You have left your firm.
"""

not_ceo_org = """
Only the CEO can do that.
"""

not_ceo_or_exec_org = """
Only the CEO and executives can do that.
"""

promote_failure_org = """
Couldn't promote user, make sure you used the correct username.
"""

def modify_promote(user):
    rank_str = rank_strs[user.firm_role]
    return promote_org.\
        replace("%NAME%", user.name).\
        replace("%RANK%", rank_str)

promote_org = """
Successfully promoted **/u/%NAME%** to **%RANK%**.
"""

def modify_fire(user):
    return fire_org.\
        replace("%NAME%", user.name)

fire_org = """
Successfully fired **/u/%NAME%** from the firm.
"""

fire_failure_org = """
Couldn't fire user, make sure you used the correct username.
"""

joinfirm_exists_failure_org = """
Can't join a firm because you are already in one. Use the *!leavefirm* command to leave your firm before joining a new one.
"""

joinfirm_failure_org = """
Could not join firm, are you sure you got the name right?
"""

joinfirm_org = """
You are now a floor trader of the firm **%NAME%**. If you'd like to leave, use the *!leavefirm* command.
"""

def modify_joinfirm(firm):
    return joinfirm_org.\
        replace("%NAME%", firm.name)

FIRM_TAX_ORG = """

--

%AMOUNT% MemeCoins were sent to the firm - %NAME%.
"""

def modify_firm_tax(tax_amount, firm_name):
    return FIRM_TAX_ORG.\
        replace("%AMOUNT%", tax_amount).\
        replace("%NAME%", firm_name)
