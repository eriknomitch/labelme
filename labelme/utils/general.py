from pathlib import Path

# FROM: https://stackoverflow.com/a/48593823
def path_leaf(path):
    return Path(path).name
