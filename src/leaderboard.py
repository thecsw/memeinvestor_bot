# TODO: add docstrin here
import time
import logging
import traceback

from sqlalchemy import create_engine, func, desc, and_
from sqlalchemy.orm import sessionmaker
import praw

import config
import utils
import formula
import message
from kill_handler import KillHandler
from models import Investor, Investment, Firm
from stopwatch import Stopwatch

logging.basicConfig(level=logging.INFO)

sidebar_text_org = """

/r/MemeEconomy is a place where individuals can buy, sell, share, make, and invest in memes freely. You'll also get updates on the market and be able to collaborate with other fellow meme traders.

*****

**Top Users:**

%TOP_USERS%

**Top Firms:**

%TOP_FIRMS%


###[Join the **official** Discord!](https://discord.gg/zVgD2M7)

&nbsp;

^(This sub is not ***only*** for templates. It is for memes in general, themed in an economic perspective. )

###***[Please send us your suggestions!](https://www.reddit.com/message/compose?to=%2Fr%2FMemeEconomy)***

***

**Our sidebar and rules are updated frequently to stay up-to-date with the current market. Please check our sidebar often for any edits or additions you might have missed.**

***

**Rules:**

1a. Submissions and submission titles must be related to the meme economy. **For Example:** "I found this meme," is not OK. "I found this meme, should I buy or sell," is OK. All post titles should reference buying or selling at a minimum, and you can browse the [Investopedia Financial Dictionary](https://www.investopedia.com/dictionary/) if you need some inspiration.

1b. Titles should explain why users should invest in the meme.

2. Please invest effort in submissions and post a template for your meme. Posts with low-effort, commonly used titles, and barely-relevant content are strongly frowned upon and are subject to removal.

3. Please be respectful. No personal attacking. Be civil in the comments. ***This does not mean that you should report someone every time they call you a rude name or because they have a differing opinion.***

4. Standard anonymity is required. Posting personal information without consent is not allowed.

5. No reposting (*Within reason*). If a post is clearly shown to be a repost, it will be removed. Crossposting is allowed as long as Rule 1 is followed and the meme is presented in an economic context. If you report a repost please include a link to an earlier post with the same content to make it easier for moderators to verify and remove the repost.

6. Please respect the economy. Sharing false market information (such as sharing fake screenshots) is a crime that is subject to possible punishments based on the severity of the submission.

7. No spamming or advertising.

8. Please keep NSFW, offensive material, and controversial topics to a minimum. Read [rule #8](https://www.reddit.com/r/MemeEconomy/about/rules/) and send a modmail if you have any questions.

9. This is a forum for reputable investors only. Your account must be older than 7 days and have at least 50 comment karma to post.

10. Standard [site-wide rules](https://www.reddit.com/help/contentpolicy) apply.

&nbsp;

*Failure to comply with any of the rules in place may result in post/comment removal or an account ban. All title-related infractions will result in a 3 day ban for the first offense, subsequent offenses will have progressively longer bans. If you need to speak with the moderators directly, please don't be afraid to [message us](https://www.reddit.com/message/compose?to=%2Fr%2FMemeEconomy).*

***

**Subs you might be interested in:**

/r/MemeInvestor_bot

/r/grandayy

/r/WholesomeMemes

/r/hmmm

/r/DankChristianMemes

/r/2meirl4meirl

/r/IncrediblesMemes

/r/Bootleg_Memes

/r/MemeCalendar

[Meme Multireddit](https://www.reddit.com/user/loimprevisto/m/memes/)

***

*Please don't send modmail asking how to buy memes. We have plenty of great users willing to help you in that regard. See [**this explanatory post**](https://www.reddit.com/r/MemeEconomy/comments/5lk964/a_beginners_guide_to_the_memeeconomy_and_meme/?ref=share&ref_source=link) for a small bit of assistance.*

***

*We support community projects such as the [**Meme Insider**](https://memeinsider.co/) and [**Danqex**](https://www.reddit.com/r/danqex/). You might see us occasionally promote posts about them.*

***
"""

# TODO: add docstring
def main():
    logging.info("Starting leaderboard...")
    logging.info("Sleeping for 8 seconds. Waiting for the database to turn on...")
    time.sleep(8)

    killhandler = KillHandler()

    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = sessionmaker(bind=engine)

    reddit = praw.Reddit(client_id=config.CLIENT_ID,
                         client_secret=config.CLIENT_SECRET,
                         username=config.USERNAME,
                         password=config.PASSWORD,
                         user_agent=config.USER_AGENT)

    # We will test our reddit connection here
    if not utils.test_reddit_connection(reddit):
        exit()

    while not killhandler.killed:
        sess = session_maker()

        top_users = sess.query(
                Investor.name,
                func.coalesce(Investor.balance+func.sum(Investment.amount), Investor.balance).label('networth')).\
                outerjoin(Investment, and_(Investor.name == Investment.name, Investment.done == 0)).\
            group_by(Investor.name).\
            order_by(desc('networth')).\
            limit(10).\
            all()

        top_firms = sess.query(Firm).\
            order_by(Firm.balance.desc()).\
            limit(5).\
            all()

        top_users_text = "Rank|User|Net Worth\n"
        top_users_text += ":-:|:-:|:-:\n"
        for i, user in enumerate(top_users):
            top_users_text += f"{i + 1}|/u/{user.name}|{formatNumber(user.networth)} MC\n"

        top_firms_text = "Rank|Firm|Total Assets|Level|Tax Rate\n"
        top_firms_text += ":-:|:-:|:-:|:-:|:-:\n"
        for i, firm in enumerate(top_firms):
            is_private = '(**P**) ' if firm.private else ''
            top_firms_text += f"{i + 1}|{is_private}{firm.name}|{formatNumber(firm.balance)} MC|{firm.rank + 1}|{firm.tax}%\n"

        sidebar_text = sidebar_text_org.\
            replace("%TOP_USERS%", top_users_text).\
            replace("%TOP_FIRMS%", top_firms_text)

        logging.info(" -- Updating sidebar text to:")
        logging.info(sidebar_text)
        for subreddit in config.SUBREDDITS:
            reddit.subreddit(subreddit).mod.update(description=sidebar_text)

        sess.commit()

        # Report the Reddit API call stats
        rem = int(reddit.auth.limits['remaining'])
        res = int(reddit.auth.limits['reset_timestamp'] - time.time())
        logging.info(" -- API calls remaining: %s, resetting in %.2fs", rem, res)

        sess.close()

        time.sleep(config.LEADERBOARD_INTERVAL)

def formatNumber(n):
    suffixes = {
        6: 'M',
        9: 'B',
        12: 'T',
        15: 'Q'
    }
    digits = len(str(n))
    if digits <= 6:
        return '{:,}'.format(n)
    exponent = (digits - 1) - ((digits - 1) % 3)
    mantissa = n / (10 ** exponent)
    suffix = suffixes.get(exponent)
    return '{:.2f}{}'.format(mantissa, suffix)

if __name__ == "__main__":
    main()
