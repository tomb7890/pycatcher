import os

class Subscription:
    def __init__(self, s):
        self.subscriptions = s 
        self.xmlfile = None
        self.url = None
        self.maxeps = None
        self.dir = None

class Subscriptions: 
    def __init__(self, b=None):
        """A subscriptions file ("podcasts.ini") is a user defined file,
        it allows the specification of the podcast programs to be downloaded. 

        Each line in the file describes a podcast subscription. Each line
        is made up of fields separated by commas. 

        The first field is the filename of a program's downloaded RSS
        (XML) file to be parsed. The second field is the URL for updates. 
        The third is an integer that stores how many episodes of a given program
        to keep at a time.

        """

        self.items = []
        self.doomed = []
        self.basedir=b

        self.parse_file()

    def parse_file (self ):
        """ Parse a podcasts.ini file into lines """
        try:
            f = open(os.path.join(self.basedir, 'podcasts.ini'), 'r')
        except IOError, err:
            # print "can't find subscriptions file"
            raise err
        data = f.read()
        self.lines = data.split('\n')
        for l in self.lines:
            fields = l.split(',')
            if ( len( fields ) > 1 ):
                pc = self.parse_line(fields)
                if pc != None:
                    self.items.append( pc )

    def parse_line(self, fields):
        """ parse_line decodes a filename, a subscription url, and a maximum number of episodes """
        xmlfile = fields[0].strip()
        if xmlfile.startswith("#"):
            return None
        if xmlfile.endswith(".xml"):
            dir = xmlfile[:-4]
        url = fields[1].strip()
        maxeps=3 # default to 3 
        if ( len ( fields ) > 2 ):
            n = fields[2].strip()
            maxeps = n
        pc = Subscription(self)
        pc.xmlfile = xmlfile
        pc.url = url
        pc.dir = dir
        pc.maxeps = int(maxeps)
        return pc

    def numtokeep( self, program ):
        for pc in self.items:
            if pc.dir == program:
                return pc.maxeps
        return None

    def prunedir( self, d, maxeps ):
        bdir = os.path.join(self.basedir, d )
        mask = os.path.join( bdir, '*.*' )
        l = [(os.stat(i).st_mtime, i) for i in glob.glob(mask)]
        l.sort()
        files = [i[1] for i in l]

        # files =  glob.glob("/tmp/*lash*")
        # video = files[ len( files ) - 1 ]
        # ommandline = video + ' ' + commandline

        # print "of full list \n" + '\n'.join( files ) 
        # print "deleteing all but three will leave \n" + '\n'.join( files[-3:] )

        nmaxeps = - int( maxeps )
        for f in files[:nmaxeps]:
            self.doomed.append( f )

    def prunestuff(self):
        # also clean up wnur/thisishell, even though its not in podcasts.ini
        # TODO: FIX This-> self.dirs.append('wnur') <- no longer fits

        for p in self.items:
            self.prunedir( p.dir, p.maxeps )
