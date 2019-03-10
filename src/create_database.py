from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable

import models
import config

def main():
    print("Creating the engine...")
    engine = create_engine(config.DB)
    models.Base.metadata.create_all(engine)

if __name__ == '__main__':
    main()
