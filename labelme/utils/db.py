import sqlite3

from ..config import get_config

def open_db(path=None):

    config = get_config()

    if path is None:
        path = config["db_name"]

    conn = sqlite3.connect(path)
    c = conn.cursor()

    return conn, c
