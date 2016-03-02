import os
import re
import time
import xml.etree.ElementTree as ET
import xml
from ConfigParser import ConfigParser
from Episode import Episode, sort_rev_chron
import Library
import Command


class Subscription:
    '''A Subscription class encapsulates an RSS Feed.

    Attributes:
    subscriptions: a pointer to the subscriptions object
    rssfile: path to the RSS file on the local file system
    url: internet address of RSS file
    maxeps: number of episodes to store on local disk
    rssfile:'''

    def __init__(self, s):
        self.subscriptions = s
        self.rssfile = None
        self.url = None
        self.maxeps = None

    def queue(self):
        '''The queue method returns pending episodes.

        Enumerate all episodes from a given RSS file, sorts  by
        publication date, and then filter the most recent N episodes
        for which there is not downloaded media, where N is from maxeps.
        '''

        allepisodes = self.get_all_episodes(self.get_rss_path())
        sort_rev_chron(allepisodes)
        queue = []
        for ep in allepisodes[:self.maxeps]:
            if not os.path.exists(ep.localfile()):
                queue.append(ep.localfile())
        return queue

    def refresh(self, downloader):
        print 'refresh'
        '''Download and store the most recent RSS file '''
        self.download_rss_file(downloader)

    def _data_sub_dir(self):
        return self.rssfile.replace('.xml', '')

    def get_rss_dir(self):
        '''Returns the full path of the RSS subdirectory.

        The rss subdirectory is where the RSS files for the
        subscriptions are stored.

        '''
        rssdir = os.path.join(self.subscriptions.basedir, "rss")
        return rssdir

    def get_rss_path(self):
        ''' Returns the full path of an RSS file.  '''
        filename = os.path.join(self.get_rss_dir(), self.rssfile)
        return filename

    def download_rss_file(self, downloader):
        ''' Downloads an RSS file. '''
        filename = self.get_rss_path()

        if not os.path.exists(self.get_rss_dir()):
            os.mkdir(self.get_rss_dir())

        downloader.addoption('--output-document', filename)
        downloader.url = self.url
        downloader.execute()
        Library.vprint(downloader.getCmd())

    def get_all_ep(self):
        filename = self.get_rss_path()
        # get the rss Document from a filename
        self.minidom_parse(filename)
        # make episode objects from a RSS Doucment

    def get_all_episodes(self, rssfile= None):
        '''This function has too many responsibilities. '''
        if rssfile == None:
            rssfile= self.get_rss_path()
        print 'calling get_all_episodes with rss file' + repr(rssfile)
        episodes = self.process_dom_object(rssfile)
        return episodes

    def dir(self):
        return os.path.join(self.subscriptions._data_base_dir(),
                            self._data_sub_dir())

    def prepare_directories_for_downloaing(self):
        ''' make the data directory if need be. '''
        if not os.path.exists(self.subscriptions._data_base_dir()):
            if not Command.Args().parser.debug:
                os.mkdir(self.subscriptions._data_base_dir())

        if not os.path.exists(self.dir()):
            if not Command.Args().parser.debug:
                os.mkdir(self.dir())

    def minidom_parse(self, filename):
        self._remove_blank_from_head_of_rss_file(filename)
        doc = None
        f = open(filename, 'r')
        doc = xml.etree.ElementTree.parse(f)
        return

    def _remove_blank_from_head_of_rss_file(self, xfile):
        # for some reason the toronto vegetarian association
        # publishes an rss file with blank first line. This
        # otherwise good xmlfile wreaks havoc on minidom parsing
        if self._blank_at_head(xfile):
            lines = self._linesfromfile(xfile)
            f = open(xfile, 'w')
            lines2 = '\n'.join(lines[1:])
            f.write(lines2)
            f.close()

    def _blank_at_head(self, xfile):
        lines = self._linesfromfile(xfile)
        if '' == lines[0]:
            return True
        return False

    def _linesfromfile(self, xfile):
        f = open(xfile, 'r')
        d = f.read()
        lines = d.split('\n')
        return lines

    def pubdate_to_timestamp(self, x, episode):
        try:
            fmtstring = r'%a, %d %b %Y %H:%M:%S'
            # timestamp = n.firstChild.nodeValue
            timestamp = x
            trimmed = trim_tzinfo(timestamp)
            pd = time.strptime(trimmed, fmtstring)
            episode.mktime = time.mktime(pd)  # seconds since the epoch
            episode.pubDate = timestamp
        except ValueError, e:
            if Command.Args().parser.verbose and Command.Args().parser.debug:
                print "pubdate parsing failed: \
                %s using data %s from %s" % \
                    (e, timestamp, filename)

    def process_dom_object(self, filename):
        episodes = []
        tree = ET.parse(filename)
        root = tree.getroot()
        self.title = (root.findall("./channel/title")[0].text)
        elements = root.findall("./channel/item")
        for el in elements:
            episode = Episode(self)
            self.pubdate_to_timestamp(el.findall('pubDate')[0].text, episode)
            episode.title = el.findall('title')[0].text
            episode.description = el.findall('description')[0].text
            e = episode.url = el.findall('enclosure')
            if e and len(e) > 0:
                episode.url = e[0].get('url')
            if episode.pubDate and episode.url and episode.title:
                episodes.append(episode)

        return episodes

def trim_tzinfo(t):
    # [Sat, 29 Apr 2006 20:38:00]
    # [Sat, 27 Feb 2010 06:00:00 EST]
    # [Fri, 13 June 2008 22:00:00]
    timezoneinfo = [r'\s[+-]\d\d\d\d$',
                    r'\sGMT$',
                    r'\sEDT$',
                    r'\sCST$',
                    r'\sPST$',
                    r'\sEST$'
                    ]

    for j in timezoneinfo:
        t = re.sub(j, '', t)
    return t


class Subscriptions:

    def __init__(self, b=None, match=None):
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
        self.basedir = b
        self._initialize_subscriptions(match)

    def find(self, substr):
        ''' find a matching subscription'''
        for i in self.items:
            if substr in i.dir():
                return i
        return None

    def _data_base_dir(self):
        ''' return the directory used for storing the media data '''
        if not hasattr(self, '_datadir'):
            cf = ConfigParser()
            cf.read(self._get_ini_file_name())
            dir = cf.get('general', 'data-directory', 0)
            self._datadir = dir
        return self._datadir

    def podcastsdir(self):
        ''' return the directory of podcast shows '''
        if not hasattr(self, '_podcastdir'):
            cf = ConfigParser()
            cf.read(self._get_ini_file_name())
            self._podcastdir = cf.get('general', 'podcasts-directory', 0)
        return self._podcastdir

    #  private methods

    def _get_ini_file_name(self):
        fullpath = os.path.join(self.basedir, 'podcasts.ini')
        return fullpath

    def _get_subs_file_name(self):
        fullpath = os.path.join(self.basedir, 'subscriptions.ini')
        return fullpath

    def _initialize_subscriptions(self, match):
        """ Parse a subscriptions.ini file into lines """
        f = None
        try:
            f = open(self._get_subs_file_name(), 'r')
        except IOError, err:
            # print "can't find subscriptions file"
            raise err

        data = f.read()
        self.lines = data.split('\n')
        for l in self.lines:
            fields = l.split(',')
            if (len(fields) > 1):
                pc = self._parse_line(fields, match)
                if pc != None:
                    self.items.append(pc)

    def _parse_line(self, fields, match):
        """
        Decode a filename, a podcast subscription url, and a maximum number of episodes
        to keep in the local library. Takes an optional match string.
        """
        rssfile = fields[0].strip()
        if rssfile.startswith("#"):
            return None

        url = fields[1].strip()

        maxeps = 3  # default to 3
        if len(fields) > 2:
            n = fields[2].strip()
            maxeps = n

        sub = Subscription(self)
        sub.rssfile = rssfile
        sub.url = url
        sub.maxeps = int(maxeps)

        if match != None:
            if -1 == sub.dir().find(match):
                return None
        return sub

if __name__ == '__main__':
    pass
