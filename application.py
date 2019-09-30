import argparse
import logging
import os
import sys

import json
import subscriptions
from report import doreport
import downloader
from filesystem import FileSystem

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen 

def main():
    '''
    Entry point of application examines command arguments
    and routes execution accordingly
    '''

    basedir = init_config()
    p = argparse.ArgumentParser()
    p.add_argument('-v', '--verbose', action='store_true')
    p.add_argument('-p', '--program', dest='program',
                        action='store',help='program x')
    p.add_argument('-lr', '--limit-rate', dest='limitrate',
                        action='store', help='limitrate')
    p.add_argument('-d', '--debug',  action='store_true')
    p.add_argument('-r', '--report', action='store_true')
    p.add_argument('-f', '--refresh', action='store_true')
    p.add_argument('-sp', '--strict-parsing',
                        action='store_true',  default=True,
                        help = """
                        Allow blank lines to appear in header of RSS file
                        """)
    p.add_argument('-s', '--search', dest='search', action='store',help='Search iTunes for a podcast')
    p.add_argument('-x', '--subscribe', dest='subscribe', action='store',help='Subscribe to a podcast')
    p.add_argument('-c', '--config', dest='configfile', action='store',help='Set alternate config file ')

    args = p.parse_args(sys.argv[1:])
    dlr = downloader.Downloader(**vars(args))
    dlr.fs = FileSystem()
    if args.report:
        doreport(basedir)
    elif args.refresh:
        dorefresh(basedir)
    elif args.search:
        dosearch(basedir, args.search)
    elif args.subscribe:
        dosubscribe(basedir, dlr, **vars(args)) 
    else:
        dodownload(basedir, dlr, **vars(args))

    if 'verbose' in args:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)


def init_config():
    if 'PODCASTROOT' in os.environ:
        return os.environ['PODCASTROOT']
    else:
        return os.path.expanduser('~/podcasts')

def podcastquery(searchterm):
    url = 'https://itunes.apple.com/search?term=%s&limit=25&entity=podcast' % searchterm
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def dosearch(basedir, searchterm):
    results = podcastquery(searchterm)
    print "\n\n"
    i = 1
    for p in results[r'results']:
        print "%d. [%s] %s " % ( i, p[r'artistName'], p[r'collectionName'])
        i=i+1

def dosubscribe(basedir, dlr, **args):
    searchterm = args['subscribe'].split(',')[0]
    results = podcastquery(searchterm)
    index = int(args['subscribe'].split(',')[-1]) - 1 
    feedurl = results[r'results'][index][r'feedUrl']
    
    subs = subscriptions.Subscriptions(dlr, basedir, **args )
    s = subscriptions.Subscription(subs, searchterm, feedurl, 3, dlr )
    subs.add(s, index, results)

def dorefresh(basedir):
    dlr = downloader.Downloader()
    dlr.fs = FileSystem()
    for sub in get_list_of_subscriptions(basedir, dlr):
        sub.refresh(dlr)

def dodownload(basedir, downloader, **args):
    '''
    Download files
    '''
    for sub in get_list_of_subscriptions(basedir, downloader, **args):
        sub.refresh(downloader)
        sub.dodownload(basedir)

def get_list_of_subscriptions(basedir, downloader, **args):
    subs = []
    subs = subscriptions.Subscriptions(downloader, basedir, **args )
    return subs.items

def get_latest_episodes(sub):
    episodes = subscriptions.get_sorted_list_of_episodes(sub, True)
    new = episodes[:sub.maxeps]
    return new

def appdir():
    path = init_config()
    return path

if __name__ == '__main__':
    main()
