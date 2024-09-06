"""Index

For a given RSS Subscription, tell us what absolute file path where
the hard link will be found. Methods are included for serializing to
and from storage.

"""

import json
import os

FILE_EXTENSION = "idx"


def episode_is_registered(db, episode):
    return db.find(episode.guid)


class Index:

    def __init__(self, filepath):
        self.fp = filepath
        self._table = {}

    def exists(self):
        return os.path.exists(self.fp)

    def load(self):
        with open(self.fp, "r") as f:
            text = f.read()
            self._table = json.loads(text)

    def save(self):
        s = json.dumps(self._table)
        with open(self.fp, "w") as f:
            f.write(s)
            f.close

    def find(self, guid):
        return guid in self._table

    def has(self, filename):
        return filename in self._table.values()

    def get(self, episode):
        """Given an episode, return it's filename."""
        return self._table[episode.guid]

    def set(self, episode, fullpath):
        self._table[episode.guid] = fullpath

    def records(self):
        return self._table.keys()

    def delete(self, guid):
        key = guid
        if key in self._table:
            del self._table[key]

    def dump(self):
        for k in self._table.keys():
            print("key: [%s], \t\t\t value: [%s]." % (k, self._table[k]))


class FakeIndex(Index):
    def __init__(self):
        Index.__init__(self, None)

    def exists(self):
        return False

    def load(self):
        # override
        pass

    def save(self):
        # override
        pass


if __name__ == "__main__":
    pass
