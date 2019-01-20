"""
This script just describes the tables and their columns
in our mysql database
"""
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable

import models
import config

def main():
    engine = create_engine(config.DB)
    a = CreateTable(models.Investment.__table__).compile(engine)
    b = CreateTable(models.Investor.__table__).compile(engine)
    c = CreateTable(models.Firm.__table__).compile(engine)
    d = CreateTable(models.Invite.__table__).compile(engine)
    print(a,b,c,d)

if __name__ == '__main__':
    main()
