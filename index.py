"""Index

For a given RSS Subscription, tell us what absolute file path where
the hard link will be found. Methods are included for serializing to
and from storage.

"""

import json
import os


FILE_EXTENSION = "idx"

class Index:
    
    def __init__(self, filepath):
        self.fp = filepath
        self.table = {}
        

    def load(self):
        if os.path.exists(self.fp):
            with open(self.fp,'r') as f:
                text = f.read()
                self.table = json.loads(text)

    def remove_entry(self, key):
        if key in self.table:
            del self.table[key]

    def save(self):
        s = json.dumps(self.table)
        with open(self.fp,'w') as f:
            f.write(s)
            f.close

    def dump(self):
        for k in self.table.keys():
            print("key: [%s], \t\t\t value: [%s]." % ( k, self.table[k]))


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
