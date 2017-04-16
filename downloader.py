import os
import command
import logging

class Downloader:
    def __init__(self):
        self.reset()

    def reset(self):
        self.url = None
        self.cmd = 'wget'
        self.options = {}

    def verbose(self):
        if command.Args().parser.verbose:
            return True
        return False

    def addoption(self, opt, val):
        self.options[opt] = val

    def getCmd(self):

        if self.verbose():
            self.cmd = self.cmd + " --verbose"
            print "Downloader.execute()"
        else:
            self.cmd = self.cmd + " --quiet"

        for o in self.options:
            self.cmd = self.cmd + " %s='%s'" % (o, self.options[o])

        fullcmd = "%s  '%s' " % (self.cmd, self.url)
        if command.Args().parser.verbose:
            print fullcmd

        return fullcmd

    def execute(self):
        fullcmd = self.getCmd()
        os.system(fullcmd)

class FakeDownloader (Downloader):
    def __init__(self):
        Downloader.__init__(self)
        self.url = ''
        self.history = []

    def execute(self):
        logging.info( 'FakeDownloader.execute: %s' % self.getCmd())
        self.history.append(self.url)








if __name__ == '__main__':
    pass
