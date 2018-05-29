from models.base import BaseTable, paginated


class Investors(BaseTable):
    _primkey = "name"

    def __init__(self, db):
        super().__init__(db)
        self._exec("""
            CREATE TABLE IF NOT EXISTS {table} (
                name VARCHAR(20) PRIMARY KEY,
                balance INTEGER DEFAULT 1000,
                active INTEGER DEFAULT 0,
                completed INTEGER DEFAULT 0,
                broke INTEGER DEFAULT 0
            )
        """)
        self._dbconn.commit()

    def total_coins(self):
        self._exec("SELECT COALESCE(SUM(balance),0) FROM {table}")
        return self._db.fetchone()[self._primkey]

    @paginated
    def top(self, order, qlimit):
        if not order in ["balance", "active", "completed", "broke"]:
            return []

        self._exec("SELECT * FROM {table} ORDER BY {order} DESC {limit}", fmt={
            "limit": qlimit,
            "order": order
        })
        return self._db.fetchall()
