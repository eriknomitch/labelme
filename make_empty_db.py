import sqlite3
conn = sqlite3.connect("labels.db")

c = conn.cursor()

c.execute("""
CREATE TABLE labels (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    image_path TEXT,
    labels BLOB
)
""")

