class DownloadQueue:
    def __init__(self):
        self._queue = []

    def clear(self):
        self._queue.clear()

    def queue(self, episode, filename):
        item = episode, filename
        self._queue.append(item)

    def in_use(self, filename):
        return any(y == filename  for x,y in self._queue)

