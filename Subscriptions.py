import os
import re
import glob
import time
import logging
import LookupTable
import xml.etree.ElementTree as ET
from ConfigParser import ConfigParser
from Episode import Episode, sort_rev_chron
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
        self.lut = LookupTable.LookupTable(self.get_idx_path())

    def _lookup_table_path(self):
        return os.path.join( self.get_rss_dir(), LookupTable.file_extension() )

    def prepare_queue(self, episodes):
        queue = []
        for episode in episodes:
            lf = episode.localfile()
            if os.path.exists(lf):
                logging.info("file already exists: " + lf)
            else:
                logging.info("queuing: " + lf)
                queue.append(episode.url)
        return queue

    def release_old_and_download_new(self, old, new, basedir, downloader):
        self.release_old_episodes(old)
        episodes = self.get_new_episodes(new, basedir, downloader)
        return episodes

    def download_new_files(self, downloader, episodes):
        logging.info("downloader ")
        queue = self.prepare_queue(episodes)
        if len(queue) > 0 :
            inputfile = 'urls.dat'

            downloader.addoption('--input-file', inputfile)
            downloader.addoption('--directory-prefix', self._data_subdir())
            if Command.Args().parser.limitrate:
                downloader.addoption('--limit-rate', Command.Args().parser.limitrate)

            downloader.url = self.url
            f = open(inputfile, 'w')
            f.write('%s\n' % ('\n'.join(queue)))
            f.close()
            downloader.execute()
            logging.info(downloader.getCmd)
            if os.path.exists(inputfile):
                os.unlink(inputfile)



    def get_new_episodes(self, saved, basedir, downloader):
        self.download_new_files(downloader, saved)
        self.create_links(saved)

    def link_creation_test(self, src, dst):
        if os.path.exists(src) and not os.path.exists(dst):
            return True
        return False

    def create_links(self, episodes):
        for e in episodes:
            src = e.localfile()
            self.trim_querystring_from_filename(src)
            dest = e.locallink()
            if os.path.exists(src):
                disksize = os.path.getsize(src)
                if int(disksize) != int(e.enclosure_length ) and False:
                    logging.warning("episdode %s's length is %d, expected to be %d " %
                                    (src, disksize, int(e.enclosure_length)))

            logging.info("making link from %s to  %s " % (src, dest))
            if True == self.link_creation_test(src, dest):
                os.link(src, dest)

    def trim_querystring_from_filename(self, filename):
        '''
        Rename file on disk from the actual file name (sometimes with a
        query string appended by the file downloader) to the expected
        name taken from the url of the RSS enclosure.
        '''

        QUERY_STRING_MARKER = '?'
        WILDCARD = '*'

        fileptrn = filename + QUERY_STRING_MARKER + WILDCARD
        g = glob.glob(fileptrn)
        x = "trim_querystring_from_filename: %s using fileptrn %s" % (filename,
                                                                      fileptrn)
        if len(g) > 0:
            actual = g[0]
            if actual:
                logging.info("[%s], [%s] " % (actual, filename))
                if not os.path.exists(filename):
                    os.rename(actual, filename)

    def release_old_episodes(self, expired):
        self.prunefiles(expired)

    def prunefiles(self, doomedeps):
        for ep in doomedeps:
            ep.prune_file()
            ep.prune_link()


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

    def get_idx_path(self):
        ''' Returns the full path of an IDX file.  '''

        idxfile = self.rssfile.replace("xml", LookupTable.file_extension())
        filename = os.path.join(self.subscriptions.get_rss_dir(),
                                idxfile )
        return filename

    def download_rss_file(self, downloader):
        ''' Downloads an RSS file. '''
        filename = self.get_rss_path()

        downloader.addoption('--output-document', filename)
        downloader.url = self.url
        downloader.execute()

    def get_all_episodes(self):
        episodes = self.fetch_episodes()
        self._max_episode_count =  len(episodes)
        self.set_linknames(episodes)
        return episodes

    def fetch_episodes(self):
        rssfile= self.get_rss_path()
        logging.info( 'calling get_all_episodes with rss file' + repr(rssfile))
        episodes = self.parse_rss_file(rssfile)
        return episodes

    def max_episode_count(self):
        return self._max_episode_count

    def set_linkname(self, episode):
        if not self.lut.table.has_key(episode.guid):
            link_name = self.generate_link_name(episode)
            self.lut.table[episode.guid] = link_name
            full_link_path = os.path.join(self._podcasts_subdir(), link_name)
            episode._link_name = full_link_path

    def set_linknames(self, episodes):
        for e in episodes:
            self.set_linkname(e)

    def generate_link_name(self, episode):
        ''''
        Generate a new link name that is not yet in use

        A link name is typically a composition of the usable text from
        an episode's TITLE element.  However sometimes there are
        duplicate (repeating) TITLE. In this case a modified version
        must be generated to avoid a collision, using a numerical suffix

        '''
        table = self.lut.table

        count = 1
        # while link name is unavailable...
        proposal = episode.base_sans_extension() + episode._file_extension()
        while True:
            if count > self.max_episode_count():
                raise RuntimeError

            count = count + 1
            if proposal not in table.values():
                break
            proposal = episode.base_sans_extension() \
                       + "-%d" % count + episode._file_extension()

        # return the link name
        return proposal

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
        # self._initialize_subscription_titles()

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
            if substr.lower() in i._sub_dir().lower():
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



class FakeSubscription (Subscription):
    def __init__(self, s, r ):
        Subscription.__init__(self, s, r, None, None)

    def fetch_episodes(self):
        # override fetch_episodes
        return self._fake_episode_list


if __name__ == '__main__':
    pass
