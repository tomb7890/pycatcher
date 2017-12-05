import os
import subscriptions
from report import doreport
import downloader
import command
import sys
from filesystem import FileSystem 


def main():
    '''
    Entry point of application examines command arguments
    and routes execution accordingly
    '''

    basedir = init_config()

    command.Args().parse(sys.argv[1:])
    dlr = downloader.Downloader()
    dlr.fs = FileSystem()
    if command.Args().parser.report:
        doreport(basedir)
    elif command.Args().parser.refresh:
        dorefresh(basedir)
    else:
        dodownload(basedir, dlr)


def init_config():
    if 'PODCASTROOT' in os.environ:
        return os.environ['PODCASTROOT']
    else:
        return os.path.expanduser('~/podcasts')


def dorefresh(basedir):
    dlr = downloader.Downloader()
    for sub in get_list_of_subscriptions_production(basedir):
        dlr.reset()
        sub.refresh(dlr)


def dodownload(basedir, downloader, **args):
    '''
    Download files
    '''
    for sub in get_list_of_subscriptions_production(downloader, basedir, **args):
        sub.refresh(downloader)
        sub.dodownload(basedir)

def get_list_of_subscriptions_production(downloader, basedir):
    match = None
    if command.Args().parser.program:
        match = command.Args().parser.program
    return get_list_of_subscriptions(basedir, downloader, match)


def get_list_of_subscriptions(basedir, downloader, match=None):
    subs = []
    subs = subscriptions.Subscriptions(downloader, basedir, match )
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
