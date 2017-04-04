import os
import Command
import logging

class Wget:
    def __init__(self):
        self.reset()

    def reset(self):
        self.url = None
        self.cmd = 'wget'
        self.options = {}

    def verbose(self):
        if Command.Args().parser.verbose:
            return True
        return False

    def addoption(self, opt, val):
        self.options[opt] = val

    def getCmd(self):

        if self.verbose():
            self.cmd = self.cmd + " --verbose"
            print "Wget.execute()"
        else:
            self.cmd = self.cmd + " --quiet"

        for o in self.options:
            self.cmd = self.cmd + " %s='%s'" % (o, self.options[o])

        fullcmd = "%s  '%s' " % (self.cmd, self.url)
        if Command.Args().parser.verbose:
            print fullcmd

        return fullcmd

    def execute(self):
        fullcmd = self.getCmd()
        os.system(fullcmd)

class MockWget (Wget):
    def __init__(self):
        Wget.__init__(self)
        self.url = ''
        self.history = []

    def execute(self):
        logging.info( 'MockWget.execute: %s' % self.getCmd())
        self.history.append(self.url)








if __name__ == '__main__':
    pass
