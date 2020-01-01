import sqlite3
import json
from contextlib import closing

from ..config import get_config

def get_db_path():
    return get_config()["db_name"]

def connect_db(row_factory=sqlite3.Row):
    conn = sqlite3.connect(get_db_path())

    # SEE: https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
    conn.row_factory = row_factory

    return conn

def open_db():
    conn = connect_db()
    c = conn.cursor()
    return conn, c

# FROM: https://stackoverflow.com/a/46519449
def query(sql, data=()):
    with closing(connect_db()) as con, con,  \
            closing(con.cursor()) as cur:
        cur.execute(sql, data)
        return cur.fetchall()

def dict_to_json_blob(dct):
    return json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')

