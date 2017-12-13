class Options:
    def __init__(self):
        self._dict = {}

    def add_option(self, name, value):
        self._dict[name] = value
