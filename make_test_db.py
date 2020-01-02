import sqlite3
import os
import sys

# ------------------------------------------------
# ------------------------------------------------
# ------------------------------------------------

# FROM: https://pynative.com/python-sqlite-blob-insert-and-retrieve-digital-data/
def convert_to_blob(filename):
    with open(filename, 'rb') as file:
        return file.read()

examples_path = "examples/semantic_segmentation/data_annotated"

example_names = [
  "2011_000099",
  "2011_000003",
  "2011_000006",
  "2011_000025"
]

def insert_example_data(n_batches):
    for batch in range(n_batches):
        for example_name in example_names:
            query = """
            INSERT INTO labels (image_path, labels) values (?, ?)
            """

            image_path = f"{examples_path}/{example_name}.jpg"
            label_path = f"{examples_path}/{example_name}.json"

            data_tuple = (image_path, convert_to_blob(label_path))

            c.execute(query, data_tuple)

            conn.commit()
    pass

# ================================================
# MAIN ===========================================
# ================================================
if os.path.exists("labels.db"):
    print("fatal: labels.db already exists. Remove it first.")
    sys.exit(1)

conn = sqlite3.connect("labels.db")

c = conn.cursor()

c.execute("""
CREATE TABLE labels (
    id INTEGER PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    image_path TEXT,
    labels BLOB
)
""")

insert_example_data(10)

