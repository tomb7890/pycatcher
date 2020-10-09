import os
from configparser import ConfigParser
import index
from parser import Parser
from lxml.html import document_fromstring

from subscription import Subscription, rss_file_name_from_text

DEFAULTCONFIGFILE = "prefs.conf"

def scan(filename, userstring):
    
    p = Parser()
    episodes = p.parse_rss_file(filename)
    items = [] 
    for e in episodes:
        if userstring in (e.description):
            html = e.description
            doc = document_fromstring(html)
            i = {}
            i['guid'] = e.guid
            i['text'] = (doc.text_content())
            items.append(i) 
    return items 

def sort_reverse_chronologically(reportdata):
    reportdata.sort(key=lambda x: x.mktime, reverse=True)

def basename(fullpath):
    segments = fullpath.split("/")
    basename = segments[-1]
    return basename


def db_of_sub(subscription):
    return index.Index(full_path_to_index_file(subscription))

def full_path_to_index_file(subscription):
    return os.path.join(
        data_directory(), 'rss',
        subscription.filesystem_safe_sub_title() + "." + index.FILE_EXTENSION
    )


def get_rss_file(index):
    cp, sections = configsections()
    s = sections[index]
    rssfile = os.path.join(rss_directory(), cp.get(s, 'rssfile'))
    return rssfile

def filename_from_fullpath(fullpath):
    lastslash = fullpath.rfind('/') + 1
    filename = fullpath[lastslash]
    return filename

def get_sub_of_index(index):
    cp = ConfigParser()
    cp.read(DEFAULTCONFIGFILE)
    sections = cp.sections()
    section = sections[index]
    s = Subscription()
    set_sub_from_config(s, cp, section)
    return s

def configsections():
    cp = ConfigParser()
    cp.read(DEFAULTCONFIGFILE)
    return cp, cp.sections()

def set_sub_from_config(sub, cp, section):
    sub.title = section
    sub.feedurl = cp.get(section, 'url')
    sub.maxeps = cp.getint(section, 'maxeps')
    r = cp.get(section, 'rssfile')
    sub.rssfile = os.path.join(rss_directory(), r)

def _media_subdirectory(subscription):
    return rss_file_name_from_text(subscription)

def data_directory():
    return os.path.expanduser("~/.podcasts-data/")

def podcasts_directory():
    return os.path.expanduser('~/podcasts')

def rss_directory():
    return os.path.join(data_directory(), 'rss')

def mediaplay(filename):
    from sys import platform
    if platform == "linux" or platform == "linux2":
        cmd = "xvlc '%s'" % filename
        # linux
    elif platform == "darwin":
        # OS X
        cmd = "/Applications/VLC.app/Contents/MacOS/VLC '%s'" % (filename)
    elif platform == "win32":
        pass
    '''

    See https://wiki.videolan.org/Mac_OS_X/

    /Applications/VLC.app/Contents/MacOS/VLC ~/Desktop/mymovie.mp4 --intf=rc --sout "#transcode{vcodec=VP80,vb=800,scale=1,acodec=vorbis,ab=128,channels=2}:std{access=file,mux="ffmpeg{mux=webm}",dst=my_first_transcoded_movie.webm}"

'''
    os.system(cmd)
    print(cmd)


if __name__ == '__main__':
    pass
