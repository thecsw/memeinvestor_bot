class BaseRow(object):
    _primkey = None
    _dbconn = None
    _table = None
    _db = None

    def __init__(self, dbconn, db, table, primkey, primval):
        self.primval = primval
        self._dbconn = dbconn
        self._db = db
        self._table = table
        self._primkey = primkey

        exist = self._exec("SELECT {pkey} FROM {table} WHERE {pkey} = %s",
                           [self.primval])
        if not exist:
            raise IndexError("Primary value %s does not exist" % primval)

    def __getitem__(self, key):
        rows = self._exec("SELECT {key} FROM {table} WHERE {pkey} = %s",
                   [self.primval], fmt={"key": key})

        # import ipdb; ipdb.set_trace()
        if not rows:
            raise IndexError("Key %s does not exist" % key)

        return self._db.fetchone()[0]

    def __setitem__(self, key, value):
        self._exec("UPDATE {table} SET {key} = %s WHERE {pkey} = %s",
                   (value, self.primval), fmt={"key": key})
        self._dbconn.commit()

    def __str__(self):
        return self.primval

    def _exec(self, query, *args, fmt={}, **kwargs):
        return self._db.execute(query.format(table=self._table,
                                             pkey=self._primkey, **fmt),
                                *args, **kwargs)


class BaseTable(object):
    _primkey_auto = False
    _row_class = BaseRow
    _primkey = None
    _dbconn = None
    _db = None

    def __init__(self, dbconn):
        self._dbconn = dbconn
        self._db = dbconn.cursor()

    def __setitem__(self, key, value):
        if not isinstance(value, (dict, list, tuple)):
            raise TypeError("Expected dict, list or tuple")

        query = "%s," * len(value)
        query = query[:-1]

        if isinstance(value, dict):
            print(value)
            if self._primkey_auto:
                self._exec("INSERT INTO {table}({keys}) VALUES({q})",
                        value.values(),
                        fmt={"keys": ",".join(value.keys()), "q": query})
            else:
                self._exec("INSERT INTO {table}({pkey},{keys}) VALUES(%s,{q})",
                        [key] + value.values(),
                        fmt={"keys": ",".join(value.keys()), "q": query})
        else:
            if self._primkey_auto:
                self._exec("INSERT INTO {table} VALUES({q})",
                           [x for x in value], fmt={"q": query})
            else:
                self._exec("INSERT INTO {table} VALUES(%s, {q})",
                           [key] + [x for x in value], fmt={"q": query})

        self._dbconn.commit()

    def __getitem__(self, key):
        return self._row_class(self._dbconn, self._db, self._table, self._primkey, key)

    def __len__(self):
        return self._exec("SELECT COUNT({key}) FROM {table}", fmt={"key": self._primkey})

    def __del__(self):
        self._db.close()

    def append(self, key=None):
        if self._primkey_auto:
            primkey = None
        else:
            primkey = key

        ret = self._exec("INSERT INTO {table} ({pkey}) VALUES(%s)", [primkey])

        self._dbconn.commit()

        return self[ret]

    @property
    def _table(self):
        return self.__class__.__name__

    def _exec(self, query, *args, fmt={}, **kwargs):
        if fmt:
            print(query.format(table=self._table,
                                             pkey=self._primkey, **fmt))
        return self._db.execute(query.format(table=self._table,
                                             pkey=self._primkey, **fmt),
                                *args, **kwargs)
