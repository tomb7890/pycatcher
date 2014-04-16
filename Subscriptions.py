import os

class Subscription:
    def __init__(self):
        self.xmlfile = None
        self.dir = None
        self.url = None
        self.maxeps = None

class Subscriptions: 
    def __init__(self, b=None):
        # open an ini file and parse into lines 

        self.basedir=b
        f = open(os.path.join(self.basedir, 'podcasts.ini'), 'r')
        data = f.read()
        self.lines = data.split('\n')

        # the directory of the target podcast (not full/absolute) 
        self.items = []
        self.doomed = []

        for l in self.lines:
            dir = ''
            chunks = l.split(',')
            if ( len( chunks ) > 1 ):
                x = ''
                d = ''
                k = 3
                url = ''

                xmlfile = chunks[0].strip()
                if xmlfile.startswith("#"):
                    continue
                if xmlfile.endswith(".xml"):
                    d = xmlfile[:-4]

                url = chunks[1].strip()

                if ( len ( chunks ) > 2 ):
                    n = chunks[2].strip()
                    k = n

                pc = Subscription()
                pc.dir = d 
                pc.xmlfile = xmlfile
                pc.maxeps = int(k)
                pc.url = url
                self.items.append( pc )

    
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
