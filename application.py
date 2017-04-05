import os
import Subscriptions
from Report import doreport
import wget
import Command
import sys


def main():
    '''
    Entry point of application examines command arguments
    and routes execution accordingly
    '''

    basedir = init_config()

    Command.Args().parse(sys.argv[1:])
    downloader = wget.Wget()
    if Command.Args().parser.report:
        doreport(basedir)
    elif Command.Args().parser.refresh:
        dorefresh(basedir)
    else:
        dodownload(basedir, downloader)


def init_config():
    if 'PODCASTROOT' in os.environ:
        return os.environ['PODCASTROOT']
    else:
        return os.path.expanduser('~/podcasts')


def dorefresh(basedir):
    downloader = wget.Wget()
    for sub in get_list_of_subscriptions_production(basedir):
        downloader.reset()
        sub.refresh(downloader)


def localrss_conditions(local_rssfile_exists, localrss_flag_is_set):
    if localrss_flag_is_set:
        if local_rssfile_exists:
            return False
    return True


def dodownload(basedir, downloader):
    '''
    Download files
    '''
    for sub in get_list_of_subscriptions_production(basedir):
        downloader.reset()
        if localrss_conditions(os.path.exists(sub.get_rss_path()),
                               Command.Args().parser.localrss):
            sub.refresh(downloader)
        downloader.reset()
        sub.dodownload(basedir, downloader)

def get_list_of_subscriptions_production(basedir):
    match = None
    if Command.Args().parser.program:
        match = Command.Args().parser.program
    return get_list_of_subscriptions(basedir, match)


def get_list_of_subscriptions(basedir, match=None):
    subs = []
    subs = Subscriptions.Subscriptions(basedir, match)
    return subs.items

def get_latest_episodes(sub):
    episodes = get_sorted_list_of_episodes(sub, True)
    new = episodes[:sub.maxeps]
    return new

def appdir():
    path = init_config()
    return path

if __name__ == '__main__':
    main()
