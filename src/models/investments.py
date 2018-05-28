from models.base import BaseTable


class Investments(BaseTable):
    _primkey = "id"
    _primkey_auto = True

    def __init__(self, db):
        super().__init__(db)
        # FOREIGN KEY(name) REFERENCES Investors(name) maybe?
        self._exec("""
            CREATE TABLE IF NOT EXISTS {table} (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                post CHAR(11),
                upvotes INTEGER,
                comment CHAR(11),
                name TEXT,
                amount INTEGER,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                done BIT DEFAULT 0,
                response CHAR(11),
                success BIT DEFAULT 0
            )
        """)
        self._dbconn.commit()

    def done(self):
        self._exec("SELECT * FROM {table} WHERE CURRENT_TIMESTAMP - time > 14400 AND Done = 0")
        return self._db.fetchall()

    def undone(self):
        self._exec("SELECT * FROM {table} WHERE done = 0")
        return self._db.fetchall()

    def invested_coins(self):
        return self._exec("SELECT SUM(amount) FROM {table} WHERE done = 0")
