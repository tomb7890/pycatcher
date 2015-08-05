import os
import sys

import Library


class Download:
    def __init__(self):
        self.url = None
        self.cmd = 'wget'
        self.options = {}

    def verbose(self):
        if 'verbose' in sys.argv:
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

        # if self.no_clobber :
        #     self.cmd = self.cmd + " --no-clobber "

        # if self.directoryprefix:
        #     self.cmd = self.cmd + " --directory-prefix '%s' " % self.directoryprefix

        # if self.outputdocument:
        #     self.cmd = self.cmd + " --output-document='%s' " % self.outputdocument

        # if self.inputfile:
        #     self.cmd = self.cmd + " --input-file='%s' " % self.inputfile

        for o in self.options:
            self.cmd = self.cmd + " %s='%s'" % (o, self.options[o])

        fullcmd = "%s  '%s' " % (self.cmd, self.url)
        if 'verbose' in sys.argv:
            print fullcmd

        return fullcmd

    def execute(self):
        fullcmd = self.getCmd()
        if not 'debug' in sys.argv:
            os.system(fullcmd)


def download_new_files(subscription, episodes, basedir):
    wget = Download()
    inputfile = 'urls.dat'
    wget.addoption('--input-file', inputfile)
    # wget.addoption('--content-disposition', '1')

    #    `--limit-rate=AMOUNT'

     # with the `m' suffix.  For example, `--limit-rate=20k' will limit
     # the retrieval rate to 20KB/s.  This is useful when, for whatever

    # wget.addoption('--limit-rate', '110k')
    if os.path.exists(inputfile):
        os.unlink(inputfile)
    dirx = os.path.join(basedir, subscription.dir)
    if not os.path.exists(dirx):
        if not 'debug' in sys.argv:
            os.mkdir(dirx)
    wget.addoption('--no-clobber', '1')
    wget.addoption('--directory-prefix', dirx)
    wget.url = subscription.url
    f = open(inputfile, 'w')
    dodownload = False
    for episode in episodes:
        lf = episode.localfile()
        if os.path.exists(lf):
            Library.vprint("file already exists: " + lf)
        else:
            # at least one download required:
            dodownload = True
            Library.vprint("queuing: " + lf)
            f.write('%s\n' % episode.url)
    f.close()
    if dodownload:
        wget.execute()
    if os.path.exists(inputfile):
        os.unlink(inputfile)


if __name__ == '__main__':
    pass
