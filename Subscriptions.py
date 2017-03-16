import os
import re
import time
import logging
import xml.etree.ElementTree as ET
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

    def __init__(self, s, r, u, m):
        self.subscriptions = s
        self.rssfile = r
        self.url = u
        self.maxeps = m
        self._make_directories()

    def _podcasts_subdir(self): # podcasts/ffrf/
        return os.path.join(self.subscriptions._podcasts_basedir(), self._sub_dir())

    def _data_subdir(self): # eg ~/.podcast-data/ffrf/
        return os.path.join(self.subscriptions._data_basedir(), self._sub_dir())

    def _make_directories(self):
        if not os.path.exists(self._podcasts_subdir()):
            os.mkdir(self._podcasts_subdir())

        if not os.path.exists(self._data_subdir()):
            os.mkdir(self._data_subdir())

    def queue(self):
        '''The queue method returns pending episodes.

        Enumerate all episodes from a given RSS file, sorts  by
        publication date, and then filter the most recent N episodes
        for which there is not downloaded media, where N is from maxeps.
        '''

        allepisodes = self.get_all_episodes()
        sort_rev_chron(allepisodes)
        queue = []
        for ep in allepisodes[:self.maxeps]:
            if not os.path.exists(ep.localfile()):
                queue.append(ep.localfile())
        return queue

    def refresh(self, downloader):
        logging.info( 'refresh')
        '''Download and store the most recent RSS file '''
        self.download_rss_file(downloader)

    def _sub_dir(self):
        # return re.sub(r'\W', '_', self.title).lower()
        return self.rssfile.replace('.xml', '')

    def get_rss_path(self):
        ''' Returns the full path of an RSS file.  '''
        filename = os.path.join(self.subscriptions.get_rss_dir(), self.rssfile)
        return filename

    def download_rss_file(self, downloader):
        ''' Downloads an RSS file. '''
        filename = self.get_rss_path()

        downloader.addoption('--output-document', filename)
        downloader.url = self.url
        downloader.execute()

    def get_all_episodes(self):
        rssfile= self.get_rss_path()
        logging.info( 'calling get_all_episodes with rss file' + repr(rssfile))
        episodes = self.parse_rss_file(rssfile)
        return episodes

    def _remove_blank_from_head_of_rss_file(self, xfile):
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

    def parse_rss_file(self, filename):
        episodes = []
        root = self._fetch_root(filename)
        self.title = (root.findall("./channel/title")[0].text)
        elements = root.findall("./channel/item")
        for el in elements:
            episode = Episode(self)
            self.pubdate_to_timestamp(el.findall('pubDate')[0].text, episode)
            episode.title = el.findall('title')[0].text
            episode.guid = el.findall('guid')[0].text
            episode.description = el.findall('description')[0].text
            e = el.findall('enclosure')
            if e and len(e) > 0:
                episode.url = e[0].get('url')
                episode.enclosure_length = e[0].get('length')
            if episode.pubDate and episode.url and episode.title and episode.guid:
                episodes.append(episode)
        return episodes

    def set_title(self, filename):
        root = self._fetch_root(filename)
        self.title = (root.findall("./channel/title")[0].text)

    def _fetch_root(self, filename):
        if Command.Args().parser.tolerant:
            self._remove_blank_from_head_of_rss_file(filename)
        tree = ET.parse(filename)
        root = tree.getroot()
        return root



def trim_tzinfo(t):
    # [Sat, 29 Apr 2006 20:38:00]
    # [Sat, 27 Feb 2010 06:00:00 EST]
    # [Fri, 13 June 2008 22:00:00]
    timezoneinfo = [r'\s[+-]\d\d\d\d$',
                    r'\sGMT$',
                    r'\sEDT$',
                    r'\sCST$',
                    r'\sPST$',
                    r'\sEST$',
                    r'\s+PDT$'
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
        self._initialize_directories()
        self._initialize_subscriptions(match)
        self._initialize_subscription_titles()

    def _initialize_directories(self):
        self._data_basedir()
        self._podcasts_basedir()
        if not os.path.exists( self._datadir):
            os.mkdir(self._datadir)
        if not os.path.exists( self._podcastdir):
            os.mkdir(self._podcastdir)
        if not os.path.exists( self.get_rss_dir()):
            os.mkdir(self.get_rss_dir())

    def find(self, substr):
        ''' find a matching subscription'''
        for i in self.items:
            if substr in i._sub_dir():
                return i
        return None

    def find_by_title_text(self, substr):
        ''' find a subscription by partial text match of subscription title  '''
        subscription = None
        for i in self.items:
            if substr in i.title:
                subscription = i
        return subscription

    def get_rss_dir(self):
        '''Returns the full path of the RSS subdirectory.

        The RSS subdirectory is where the RSS files for the
        subscriptions are stored.

        '''
        rssdir = os.path.join(self._data_basedir(), "rss/")
        return rssdir

    def _data_basedir(self):
        ''' return the directory used for storing the media data '''
        if not hasattr(self, '_datadir'):
            cf = ConfigParser()
            cf.read(self._get_ini_file_name())
            dir = cf.get('general', 'data-directory', 0)
            self._datadir = os.path.expanduser(dir)
        return self._datadir

    def _podcasts_basedir(self):
        ''' return the directory of podcast shows '''
        if not hasattr(self, '_podcastdir'):
            cf = ConfigParser()
            cf.read(self._get_ini_file_name())
            self._podcastdir = os.path.expanduser(cf.get('general', 'podcasts-directory', 0))
        return self._podcastdir

    def _get_ini_file_name(self):
        basename = 'pycatcher.conf'
        alternative1 = os.path.join(
            os.path.expanduser("~/podcasts/"),
            basename )

        if os.path.exists(basename):
            return basename
        elif  os.path.exists(alternative1):
            return alternative1


    def _get_subs_file_name(self):
        return self._get_ini_file_name()

    def _initialize_subscriptions(self, match):
        config = ConfigParser()
        config.read(self._get_subs_file_name())

        for s in config.sections():
            maxeps = rssfile = url = None
            if config.has_option(s, 'maxeps'):
                maxeps = config.getint(s, 'maxeps')
            if config.has_option(s, 'rssfile'):
                rssfile = config.get(s, 'rssfile')
            if config.has_option(s, 'url'):
                url = config.get(s, 'url')
            if maxeps and rssfile and url:
                sub = Subscription(self, rssfile, url, int(maxeps))

                if match:
                    if match.lower() in repr(s).lower():
                         self.items.append(sub)
                else:
                    self.items.append(sub)

        if match is not None and len(match) > 0:
            if len(self.items) == 0:
                raise ValueError("could not find subscription " + match )

    def _initialize_subscription_titles(self):
        for s in self.items:
            s.set_title(s.get_rss_path())
        return None




if __name__ == '__main__':
    pass
