"""
This script just automatically grants badges to all
users from an input file
"""

import json
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import config
from models import Investor

ENGINE = create_engine(config.DB, pool_recycle=60)
SESSION_MAKER = scoped_session(sessionmaker(bind=ENGINE))

def grant(sess, grantee, badge):
    """
    This is how admins can grant badges manually
    """

    investor = sess.query(Investor).\
        filter(Investor.name == grantee).\
        first()

    badge_list = json.loads(investor.badges)
    if badge in badge_list:
        return
    badge_list.append(badge)
    investor.badges = json.dumps(badge_list)
    sess.commit()

def main():
    """
    Dirty main to do the trick
    """
    users = []
    badge = sys.argv[1]
    filename = sys.argv[2]
    with open(filename, 'r') as read_file:
        users = [x.replace('\n', '') for x in read_file.readlines()]
    for user in users:
        grant(SESSION_MAKER, user, badge)
        print(f"Granted {badge} to {user}")

if __name__ == '__main__':
    main()
