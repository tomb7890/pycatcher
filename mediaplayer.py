import os
from sys import platform


class MediaPlayer:
    def __init__(self):
        pass

    def play(self, filename):
        cmd = self._play(filename)
        os.system(cmd)
        return cmd

    def _play(self, filename):
        if platform == "linux" or platform == "linux2":
            cmd = "xvlc '%s'" % filename
        elif platform == "darwin":
            cmd = "/Applications/VLC.app/Contents/MacOS/VLC '%s'" % (filename)
        elif platform == "win32":
            pass
        return cmd


class FakeMediaPlayer(MediaPlayer):
    def __init__(self):
        self._played_cmd = None

    def play(self, filename):
        self._played_cmd = self._play(filename)

    def played(self):
        return self._played_cmd
