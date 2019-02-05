import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import Investor
import config

def main():
    engine = create_engine(config.DB, pool_recycle=60, pool_pre_ping=True)
    session_maker = scoped_session(sessionmaker(bind=engine))
    sess = session_maker()

    users = []
    with open(sys.argv[1], 'r') as r:
        users = [x.replace('\n', '') for x in r.readlines()]

    counter = 0
    for user in users:
        sess.add(Investor(name=user))
        print(f"{counter}. Added {user}")
        counter += 1
    sess.commit()

if __name__ == '__main__':
    main()
