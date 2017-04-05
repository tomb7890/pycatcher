"""Index

For a given RSS Subscription, tell us what absolute file path where
the hard link will be found. Methods are included for serializing to
and from storage.

"""

import json
import os


def file_extension():
    return "idx"


class Index:
    def __init__(self, filepath):
        self.fp = filepath
        self.table = {}

    def load(self):
        if os.path.exists(self.fp):
            text = open(self.fp, 'r').read()
            self.table = json.loads(text)

    def remove_entry(self, key):
        if key in self.table:
            del self.table[key]

    def save(self):
        if len(self.table.keys()) > 1:
            s = json.dumps(self.table)
            f = open(self.fp, 'w')
            f.write(s)
            f.close


class FakeIndex(Index):
    def __init__(self):
        Index.__init__(self, None)

    def load(self):
        # override
        pass

    def save(self):
        # override
        pass


if __name__ == '__main__':
    pass
