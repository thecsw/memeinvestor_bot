# TODO: add docstrin here
import time
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
        sess = session_maker()
        now = time.time()

        firms = sess.query(Firm).\
            filter(now - Firm.last_payout >= config.PAYROLL_INTERVAL).\
            all()

        for firm in firms:
            # payouts is more than 1 if some amount of previous payouts never
            # got processed for some reason
            payouts = int((now - firm.last_payout) / config.PAYROLL_INTERVAL)
            payout_ratio = 1 - (0.6 ** payouts)
            payout_amount = int(payout_ratio * firm.balance)
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

        time.sleep(config.PAYROLL_INTERVAL / 2)

if __name__ == "__main__":
    main()
