import logging
import os
import sys

import subscriptions
from report import doreport
import downloader
from filesystem import FileSystem
import argparser 

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
