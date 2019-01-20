# TODO: add docstrin here
import time
import datetime
import logging
import traceback

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import utils
import formula
import message
from kill_handler import KillHandler
from models import Investor, Firm
from stopwatch import Stopwatch

logging.basicConfig(level=logging.INFO)

# TODO: add docstring
def main():
    logging.info("Starting payroll...")
    logging.info("Sleeping for 8 seconds. Waiting for the database to turn on...")
    time.sleep(8)

    killhandler = KillHandler()

    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = sessionmaker(bind=engine)

    while not killhandler.killed:
        # only process payouts 5pm - 6pm on Fridays EST (10pm - 11pm UTC)
        now_dt = datetime.datetime.now()
        if now_dt.hour != 22 or now_dt.weekday() != 4:
            time.sleep(10 * 60)
            continue

        sess = session_maker()
        now = time.time()

        # get firms which were not paid out to or created recently (last 3 days)
        firms = sess.query(Firm).\
            filter(now - Firm.last_payout >= (3 * 24 * 60 * 60)).\
            all()

        for firm in firms:
            # 10% of firm coins are burned as a tax
            firm.balance -= int(0.1 * firm.balance)

            payout_amount = int(0.4 * firm.balance)
            if payout_amount == 0:
                # handle broke firms
                firm.last_payout = now
                continue

            exec_amount = 0
            exec_total = 0
            if firm.execs > 0:
                exec_total = payout_amount * 0.4
                exec_amount = int(exec_total / firm.execs)

            trader_total = payout_amount - exec_total
            trader_amount = int(trader_total / (firm.size - firm.execs))

            logging.info(" -- firm '%s': paying out %s each to %s traders, and %s each to %s execs",\
                firm.name, trader_amount, firm.size - firm.execs, exec_amount, firm.execs)

            employees = sess.query(Investor).\
                filter(Investor.firm == firm.id).\
                all()
            for employee in employees:
                if employee.firm_role == "":
                    employee.balance += trader_amount
                elif employee.firm_role == "exec":
                    employee.balance += exec_amount

            firm.balance -= payout_amount
            firm.last_payout = now

        sess.commit()
        sess.close()

        time.sleep(10 * 60)

if __name__ == "__main__":
    main()
