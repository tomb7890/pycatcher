import logging
import os
import sys

import json
import subscriptions
from report import doreport
import downloader
from filesystem import FileSystem

import argparser 


try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen 


def main():
    '''
    Entry point of application examines command arguments
    and routes execution accordingly
    '''
    p = argparser.argparser()
    basedir = init_config()

    args = p.parse_args(sys.argv[1:])
    dlr = downloader.Downloader(args)
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
        dodownload(basedir, dlr, args) 

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

def dodownload(basedir, downloader, args=None):
    '''
    Download files
    '''
    for sub in get_list_of_subscriptions(basedir, downloader, args):
        sub.refresh(downloader)
        sub.dodownload(basedir)

def get_list_of_subscriptions(basedir, downloader, args):
    subs = []
    subs = subscriptions.Subscriptions(args, downloader, basedir)
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
