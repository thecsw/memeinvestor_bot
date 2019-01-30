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
/r/BancaDelMeme è un posto dove si puoi comprare, vendere, condividere, fare e investire sui meme liberamente.

*****

**Migliori utenti:**

%TOP_USERS%

**Migliori società:**

%TOP_FIRMS%


&nbsp;

^(Questo sub non è ***solo*** per templates. È rivolto a tutti i meme (in italiano), il tutto arricchito con un po' di sano gioco dei mercati)

###***[Inviaci dei suggerimenti!](https://www.reddit.com/message/compose?to=%2Fr%2FBancaDelMeme)***

***

**La nostra sidebar e le nostre regole sono aggiornate frequentemente, per tenere il passo dei sempre mutabili mercati. Per favore, ogni tanto dai un'occhiata alla sidebar per eventuali aggiornamenti che potresti aver perso.**

***

**Regole:** 

1a. Post e titoli devono essere legati alla meme economy.
**Per esempio:** "Ho trovato questa pic" non è OK. "Ho trovato questa pic, che faccio compro o vendo?" è già meglio. "Questo meme sarà il top trend nel terzo trimestre 2019, comprate" è l'ideale. Ingegnatevi! 
Potete prendere spunto dal dizionario del Sole24Ore [Investopedia Financial Dictionary](https://finanza-mercati.ilsole24ore.com/strumenti/glossario/glossario.php) se hai bisogno di ispirazione.

1b. I titoli dovrebbero spiegare perché gli utenti dovrebbero investire su quel meme.

2. Per favore, non fare post low effort. E soprattutto, cerca di postare i teplate dei tuoi meme. Post low effort con titoli identici ad altri, contenuti poco rilevanti sono genericamente sconsigliati e soggetti a rimozione.

3. Per favore, porta rispetto agli altri utenti. Non si tollerano attacchi personali. Rimani civile nei commenti. Alla fine siamo qui per divertirci.
***Questo non vuol dire che dovete inviare report ogni volta che qualcuno vi chiama in modo rude oppure ha un opinione differente dalla vostra.***

4. Non si tollerano post, messaggi o nomi utente che rivelano informazioni personali senza il consenso dell'interessato.


5. No repost. I crosspost sono permessi se seguono la regola 1. 

6. Rispetta l'economia. Non inviare false informazioni di mercato (come falsi screenshot), è un crimine ed è soggetto a controlli da parte delle fiamme gialle. 

7. No spam e no autopromozione o pubblicità di ogni tipo.


8. Per favore filtra il materiale NSFW, non adatto a minori o controverso col filtro NSFW.

9. Le regole standard di reddit valgono comunque: [site-wide rules](https://www.reddit.com/help/contentpolicy).

&nbsp;

***

**Subreddit ai quali potresti essere interessato:**

/r/italy

***
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
            limit(5).\
            all()

        top_firms = sess.query(Firm).\
            order_by(Firm.balance.desc()).\
            limit(5).\
            all()

        top_users_text = "Rank|User|Net Worth\n"
        top_users_text += ":-:|:-:|:-:\n"
        for i, user in enumerate(top_users):
            top_users_text += f"{i + 1}|/u/{user.name}|{user.networth} MC\n"

        top_firms_text = "Rank|Firm|Total Assets|Level|Tax Rate\n"
        top_firms_text += ":-:|:-:|:-:|:-:|:-:\n"
        for i, firm in enumerate(top_firms):
            is_private = '(**P**) ' if firm.private else ''
            top_firms_text += f"{i + 1}|{is_private}{firm.name}|{firm.balance} MC|{firm.rank + 1}|{firm.tax}%\n"
            
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

if __name__ == "__main__":
    main()
