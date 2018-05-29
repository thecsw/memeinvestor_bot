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
                name VARCHAR(20),
                amount INTEGER,
                time INT DEFAULT (unix_timestamp(current_Date())),
                done BIT DEFAULT 0,
                response CHAR(11),
                success BIT DEFAULT 0
            )
        """)
        self._dbconn.commit()

    def done(self):
        self._exec("SELECT * FROM {table} WHERE (unix_timestamp(current_Date()) - time) > 14400 AND done = 0")
        return self._db.fetchall()

    def invested_coins(self):
        return self._exec("SELECT SUM(amount) FROM {table} WHERE done = 0").fetchone()[0]
