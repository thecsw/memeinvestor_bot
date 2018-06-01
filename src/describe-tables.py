import models, config
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable

engine = create_engine(config.db)
a = CreateTable(models.Investment.__table__).compile(engine)
b = CreateTable(models.Investor.__table__).compile(engine)

print(a,b)
