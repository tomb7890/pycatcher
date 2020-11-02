import argparser

import logging
import sys
import urllib

from main import play_episode, list_episodes, list_subscriptions, podcastquery
from lib import (
    find_subscription_by_index,
    initialize_subscription,
    get_all_subscriptions,
)

from downloader import Downloader
from downloader import fetch
from filesystem import FileSystem
from prefs import get_subscription_names


from register import register
from report import doreport
from subscription import Subscription

from mediaplayer import MediaPlayer


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
    results = podcastquery(args.search)
    print("\n\n")
    i = 1
    for p in results[r"results"]:
        print("%d. [%s] %s " % (i, p[r"artistName"], p[r"collectionName"]))
        i = i + 1


def dosubscribe(args):
    searchterm = args.subscribe[0]
    index = int(args.subscribe[1]) - 1
    results = podcastquery(searchterm)
    feedurl = results[r"results"][index][r"feedUrl"]
    collectionname = results[r"results"][index][r"collectionName"]
    register(feedurl, collectionname)


def doplay(args):
    fs = FileSystem()
    player = MediaPlayer()
    subs = get_all_subscriptions()
    print(play_episode(fs, player, args, subs))


def dolistepisodes(args):
    i = int(args.listepisodes) - 1
    sub = find_subscription_by_index(i)
    fs = FileSystem()
    print(list_episodes(sub, fs))


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
    try:
        names = get_subscription_names()
        if args.download[0] == "all":
            for name in names:
                download_subscription_by_name(name, args)
        else:
            i = int(args.download[0]) - 1
            name = names[i]
            download_subscription_by_name(name, args)

    except urllib.error.URLError as x:
        print(x)


def download_subscription_by_name(name, args):
    subscription = download_rss_file(name, args)
    db = subscription.get_db()
    fs = FileSystem()
    dl = Downloader(fs, subscription, args)
    dl.dodownload(db)


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
