import argparser
import logging
import sys
import urllib
import requests

from error import BadUserInputError
from registry import Registry
from main import (
    play_episode,
    list_episodes,
    list_subscriptions,
    subscribe_to_podcast,
    search_for_podcast,
)

from lib import (
    initialize_subscription,
    get_all_subscriptions,
)

from episodesynchronizer import EpisodeSynchronizer
from downloader import Downloader
from downloader import fetch
from filesystem import FileSystem
from prefs import get_subscription_names


from report import doreport
from subscription import Subscription

from mediaplayer import MediaPlayer
from podcasts import PodcastsAPI


def main():
    p = argparser.argparser()
    args = p.parse_args(sys.argv[1:])

    if args.search:
        dosearch(args)
    elif args.subscribe:
        dosubscribe(args)
    elif args.play:
        doplay(args)
    elif args.update:
        doupdate(args)
    elif args.listsubscriptions:
        dolistsubscriptions(args)
    elif args.listepisodes:
        dolistepisodes(args)
    elif args.download:
        dodownload(args)
    elif args.report:
        doreport("report.html")

    if "verbose" in args:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
    return


def dosearch(args):
    print(search_for_podcast(args))


def dosubscribe(args):
    try:
        subscribe_to_podcast(args, Registry(), PodcastsAPI())
    except BadUserInputError as e:
        print(e.msg())


def doplay(args):
    try:
        fs = FileSystem()
        player = MediaPlayer()
        subs = get_all_subscriptions()
        play_episode(fs, player, args, subs)
    except BadUserInputError as e:
        print(e.msg())


def dolistepisodes(args):
    try:
        fs = FileSystem()
        subs = get_all_subscriptions()
        print(list_episodes(fs, args, subs))
    except BadUserInputError as e:
        print(e.msg())


def doupdate(args):
    names = get_subscription_names()
    try:
        index = int(args.update) - 1
        name = names[index]
        download_rss_file(name, args)

    except ValueError:
        if args.update == "all":
            for name in names:
                download_rss_file(name, args)


def dolistsubscriptions(args):
    subs = get_all_subscriptions()
    print(list_subscriptions(subs))


def dodownload(args):
    names = get_subscription_names()
    if args.download[0] == "all":
        for name in names:
            download_subscription_by_name(name, args)
    else:
        i = int(args.download[0]) - 1
        name = names[i]
        download_subscription_by_name(name, args)


def download_subscription_by_name(name, args):
    try:
        subscription = download_rss_file(name, args)
        db = subscription.get_db()
        filesystem = FileSystem()
        downloader = Downloader(filesystem, subscription, args)
        es = EpisodeSynchronizer(filesystem, subscription, downloader)
        es.dodownload(db)
    except urllib.error.URLError as e:
        logging.info("app.py catching URLError: \n %s\n\n" % str(e))

    except requests.exceptions.HTTPError as e:
        logging.info("app.py catching HTTPError: \n %s\n\n" % str(e))

    except requests.exceptions.RequestException as e:
        logging.info("app.py catching RequestException: \n %s\n\n" % str(e))


def download_rss_file(name, args):
    sub = Subscription()
    initialize_subscription(sub, name)
    fetch(sub.feedurl, sub.rssfile, sub.title, args)
    return sub


def print_debug(episodes, subscription, db, rssfile):
    for e in episodes[0 : subscription.maxeps]:
        print("guid:" + e.guid)
        print("url:" + e.url)
        print("title:" + e.title)
        print("basename:" + e.basename())
        print("\n\n")


if __name__ == "__main__":
    main()
