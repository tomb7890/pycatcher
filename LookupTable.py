"""Lookup Table

For a given RSS Subscription, tell us what absolute file path where
the hard link will be found. Methods are included for serializing to
and from storage.

"""

import json, os

def file_extension():
    return "idx"

class LookupTable:
    def __init__(self, filepath):
        self.fp = filepath
        self.table = {}

    def load(self):
        if os.path.exists(self.fp):
            text = open(self.fp, 'r').read()
            self.table = json.loads(text)

    def save(self):
        if len(self.table.keys()) > 1:
            s = json.dumps(self.table)
            f = open(self.fp, 'w')
            f.write(s)
            f.close


class FakeLookupTable(LookupTable):
    def __init__(self):
        LookupTable.__init__(self, None)

    def load(self):
        pass
    def save(self):
        pass




if __name__ == '__main__':
    pass
