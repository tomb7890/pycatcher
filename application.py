import os
import subscriptions
from report import doreport
import downloader
import sys
from filesystem import FileSystem
import argparse
import logging 

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

    args = p.parse_args(sys.argv[1:])
    dlr = downloader.Downloader(**vars(args))
    dlr.fs = FileSystem()
    if args.report:
        doreport(basedir)
    elif args.refresh:
        dorefresh(basedir)
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
