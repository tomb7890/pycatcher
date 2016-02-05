import xml.dom.minidom, os, re, time
from ConfigParser import ConfigParser
from Episode import Episode, sort_rev_chron
import Library
from wget import Wget

class Subscription:
    def __init__(self, s):
        self.subscriptions = s
        self.xmlfile = None
        self.url = None
        self.maxeps = None
        self.dir = None

    def get_xml_dir(self):
        xmldir = os.path.join(self.subscriptions.basedir, "xml")
        return xmldir

    def get_rss_path(self):
        filename = os.path.join(self.get_xml_dir(), self.xmlfile)
        return filename

    def get_rss_file( self, use_local ):
        filename = self.get_rss_path()
        if os.path.exists(filename) and True == use_local:
            return filename
        if not os.path.exists(self.get_xml_dir()):
            os.mkdir ( self.get_xml_dir() )

        wget = Wget()
        wget.addoption('--output-document', filename)
        # wget.addoption('--content-disposition', '1')
        wget.url = self.url
        wget.execute()
        Library.vprint(wget.getCmd())
        return filename

    def minidom_parse( self, filename ):
        # blank lines causes heartburn for omebody
        self._remove_blank_from_head_of_rss_file( filename )
        doc = None
        # minidom parse an rss file
        f = open( filename, 'r' )
        doc = xml.dom.minidom.parse( f )
        return doc

    def _remove_blank_from_head_of_rss_file( self, xfile ):
        # for some reason the toronto vegetarian association
        # publishes an rss file with blank first line. This
        # otherwise good xmlfile wreaks havoc on minidom parsing
        if self._blank_at_head( xfile ):
            lines = self._linesfromfile( xfile )
            f = open( xfile, 'w')
            lines2 = '\n'.join( lines[1:] )
            f.write( lines2 )
            f.close()

    def _blank_at_head( self, xfile ):
        lines = self._linesfromfile( xfile )
        if '' == lines[0]:
            return True
        return False

    def _linesfromfile( self, xfile ):
        f = open( xfile, 'r' )
        d = f.read()
        lines = d.split('\n')
        return lines

    def process_dom_object( self, doc, filename  ):
        episodes = []

        items = doc.getElementsByTagName("channel")
        if None != items:
            for i in items:
                for n in i.childNodes:
                    if n.nodeName == "title":
                        self.title = n.firstChild.nodeValue

        items = doc.getElementsByTagName("item")
        for i in items:
            episode = Episode(self)
            for n in i.childNodes:
                if n.nodeName == "title":
                    if None != n.firstChild:
                        episode.title = n.firstChild.nodeValue

                if n.nodeName == "description":
                    if None != n.firstChild:
                        episode.description = n.firstChild.nodeValue

                if n.nodeName == "pubDate":
                    try:
                        fmtstring = r'%a, %d %b %Y %H:%M:%S'
                        timestamp = n.firstChild.nodeValue
                        trimmed = trim_tzinfo( timestamp )
                        pd = time.strptime(trimmed, fmtstring )
                        episode.mktime = time.mktime(pd) # seconds since the epoch
                        episode.pubDate = timestamp
                    except ValueError, e:
                        if debug and verbose:
                            print "pubdate parsing failed: %s using data %s from %s" % \
                                ( e, timestamp, filename )
                if n.nodeName == "enclosure":
                    uattr = n.getAttribute("url")
                    episode.url = uattr

            if episode.pubDate and episode.url and episode.title:
                episodes.append(episode)

        return episodes

def trim_tzinfo(t):
    # [Sat, 29 Apr 2006 20:38:00]
    # [Sat, 27 Feb 2010 06:00:00 EST]
    # [Fri, 13 June 2008 22:00:00]
    timezoneinfo = [ r'\s[+-]\d\d\d\d$',
                     r'\sGMT$',
                     r'\sEDT$',
                     r'\sCST$',
                     r'\sPST$',
                     r'\sEST$'
                 ]

    for j in timezoneinfo:
        t = re.sub(j, '', t )
    return t

class Subscriptions:
    def __init__(self, b=None):
        """A subscriptions file (podcasts.ini) is a user defined file,
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
        self._parse_file()


    def datadir ( self ):
        cf = ConfigParser()
        cf.read(self._get_ini_file_name())
        dir = cf.get('general', 'data-directory', 0)
        return dir

    def podcastsdir(self):
        if not hasattr(self, '_podcastdir' ):
            cf = ConfigParser()
            cf.read(self._get_ini_file_name())
            self._podcastdir = cf.get('general', 'podcasts-directory', 0)
        return self._podcastdir


    def find(self,substr):
        for i in self.items:
            if substr in i.dir:
                print i.dir
                return i
        return None

    def _get_ini_file_name(self):
        fullpath= os.path.join(self.basedir, 'podcasts.ini')
        return fullpath

    def _get_subs_file_name(self):
        fullpath= os.path.join(self.basedir, 'subscriptions.ini')
        return fullpath

    def _parse_file (self ):
        """ Parse a podcasts.ini file into lines """
        f = None
        try:
            f = open( self._get_subs_file_name(), 'r' )
        except IOError, err:
            # print "can't find subscriptions file"
            raise err
        data = f.read()
        self.lines = data.split('\n')
        for l in self.lines:
            fields = l.split(',')
            if ( len( fields ) > 1 ):
                pc = self._parse_line(fields)
                if pc != None:
                    self.items.append( pc )

    def _parse_line(self, fields):
        """
        Decode a filename, a podcast subscription url, and a maximum number of episodes
        to keep in the local library.
        """
        xmlfile = fields[0].strip()
        if xmlfile.startswith("#"):
            return None
        if xmlfile.endswith(".xml"):
            dir = xmlfile[:-4]
        url = fields[1].strip()

        maxeps=3 # default to 3
        if len(fields) > 2:
            n = fields[2].strip()
            maxeps = n

        sub = Subscription(self)
        sub.xmlfile = xmlfile
        sub.url = url
        sub.dir = dir
        sub.maxeps = int(maxeps)
        return sub

if __name__ == '__main__':
    pass
