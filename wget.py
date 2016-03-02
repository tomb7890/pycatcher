import os
import Library
import Command


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
        if Command.Args().parser.verbose:
            print fullcmd

        return fullcmd

    def execute(self):
        fullcmd = self.getCmd()
        os.system(fullcmd)




    def download_new_files(self, subscription, episodes, basedir):
        inputfile = 'urls.dat'
        self.addoption('--input-file', inputfile)
        # wget.addoption('--content-disposition', '1')

        #    `--limit-rate=AMOUNT'

         # with the `m' suffix.  For example, `--limit-rate=20k' will limit
         # the retrieval rate to 20KB/s.  This is useful when, for whatever

        # wget.addoption('--limit-rate', '110k')
        if os.path.exists(inputfile):
            os.unlink(inputfile)

        self.addoption('--directory-prefix', subscription.dir())
        self.url = subscription.url
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
            self.execute()
            # Library.vprint(self.getCmd())
        if os.path.exists(inputfile):
            os.unlink(inputfile)

class MockWget (Wget):
    def __init__(self):
        Wget.__init__(self)

    def execute(self):
        Library.vprint( 'MockWget.execute: %s' % self.getCmd())







if __name__ == '__main__':
    pass
