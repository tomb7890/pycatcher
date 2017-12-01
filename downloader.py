import os
import command
import logging
from filesystem import FakeFileSystem


class Downloader:
    def __init__(self):
        self.reset()

    def reset(self):
        self.url = None
        self.cmd = 'wget'
        self.options = {}

    def verbose(self):
        if command.Args().parser.verbose:
            logger=logging.getLogger()
            logger.setLevel(logging.INFO)
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

    def execute(self, queue):
        logging.info('Downloader.execute: %s' % self.getCmd())
        inputfile = 'urls.dat'
        self.addoption('--input-file', inputfile)
        
        f = open(inputfile, 'w')

        f.write('%s\n' % ('\n'.join([x.url for  x in queue])))
        f.close()

        self.execute_main()

        if os.path.exists(inputfile):
            os.unlink(inputfile)

    def execute_main(self):
        logging.info( 'Downloader.execute_main: %s' % self.getCmd())
        fullcmd = self.getCmd()
        os.system(fullcmd)


class FakeDownloader(Downloader):
    def __init__(self):
        Downloader.__init__(self)
        self.url = ''
        self.history = []
        self.fs = FakeFileSystem()

    def execute(self, queue):
        logging.info( 'FakeDownloader.execute: %s' % self.getCmd())
        self.history.append(self.url)

        for episode in queue:
            datadir = self.options['--directory-prefix']
            self.fs.touch(datadir, episode._filename_from_url())
 
if __name__ == '__main__':
    pass
