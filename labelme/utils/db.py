import sqlite3

def open_db(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    return conn, c
