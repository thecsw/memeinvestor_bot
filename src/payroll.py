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

            # 50% of remaining firm coins are paid out
            payout_amount = int(0.5 * firm.balance)
            if payout_amount == 0:
                # handle broke firms
                firm.last_payout = now
                continue

            # 30% paid to board members (CEO, COO, CFO) (30% of total payroll)
            board_total = payout_amount * 0.3
            board_members = 1 + firm.coo + firm.cfo
            board_amount = int(board_total / board_members)

            remaining_amount = payout_amount - board_total

            # 40% of remaining paid to executives (28% of total payroll)
            exec_amount = 0
            exec_total = 0
            if firm.execs > 0:
                exec_total = remaining_amount * 0.4
                exec_amount = int(exec_total / firm.execs)
                remaining_amount -= exec_total

            # 50% of remaining paid to associates (21% of total payroll)
            assoc_amount = 0
            assoc_total = 0
            if firm.assocs > 0:
                assoc_total = remaining_amount * 0.5
                assoc_amount = int(assoc_total / firm.assocs)
                remaining_amount -= assoc_total

            # 100% of remaining paid to associates (21% of total payroll)
            trader_total = remaining_amount
            tradernbr = firm.size - firm.execs - firm.assocs - 1 - firm.cfo - firm.coo
            trader_amount = int(trader_total / max(tradernbr, 1))

            logging.info(" -- firm '%s': paying out %s each to %s trader(s), %s each to %s associate(s), %s each to %s executive(s), and %s each to %s board member(s)",\
                firm.name, trader_amount, tradernbr, assoc_amount, firm.assocs, exec_amount, firm.execs, board_amount, board_members)

            employees = sess.query(Investor).\
                filter(Investor.firm == firm.id).\
                all()
            for employee in employees:
                if employee.firm_role == "":
                    employee.balance += trader_amount
                elif employee.firm_role == "assoc":
                    employee.balance += assoc_amount
                elif employee.firm_role == "exec":
                    employee.balance += exec_amount
                elif employee.firm_role == "cfo":
                    employee.balance += board_amount
                elif employee.firm_role == "coo":
                    employee.balance += board_amount
                elif employee.firm_role == "ceo":
                    employee.balance += board_amount

            firm.balance -= payout_amount
            firm.last_payout = now

        sess.commit()
        sess.close()

        time.sleep(10 * 60)

if __name__ == "__main__":
    main()
