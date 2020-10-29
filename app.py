import argparser
import json
import logging
import sys
import urllib

from main import scan, play_episode, list_episodes, list_subscriptions
from lib import (
    find_subscription_by_index,
    initialize_subscription,
    get_all_subscriptions,
)

from downloader import Downloader
from downloader import fetch
from filesystem import FileSystem
from prefs import get_subscription_names

from parser import Parser
from register import register
from report import doreport
from subscription import Subscription
from urllib.request import urlopen
from mediaplayer import MediaPlayer


def main():
    p = argparser.argparser()
    args = p.parse_args(sys.argv[1:])

    if args.search:
        dosearch(args)
    elif args.subscribe:
        dosubscribe(args)

    elif args.fetch:
        dofetch(args)

    elif args.scan:
        doscan(args)
    elif args.play:
        doplay(args)

    elif args.update:
        doupdate(args)

    elif args.urlof:
        dourlof(args)
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


def dofetch(args):
    searchterm = args.fetch[0]
    index = int(args.fetch[1]) - 1
    results = podcastquery(searchterm)
    feedurl = results[r"results"][index][r"feedUrl"]
    print(feedurl)


def doscan(args):
    """
    Take the arbitrary RSS filename given at command line and a text string, print out IDs of episodes that match the given file.
    """
    # filename from user
    filename = args.scan[0]

    # string from user
    userstring = args.scan[1]

    items = scan(filename, userstring)

    for i in items:
        print(i)


def dourlof(args):
    filename = args.urlof[0]
    guid = args.urlof[1]
    print("urlof [%s], [%s]" % (filename, guid))

    p = Parser()
    episodes = p.scan_rss_file(filename)

    for e in episodes:
        if guid == e.guid:
            print(e.url)


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


def podcastquery(searchterm):
    url = (
        "https://itunes.apple.com/search?term=%s&limit=25&entity=podcast"
        % urllib.parse.quote_plus(searchterm)
    )
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


def doupdate(args):
    # cp, sections = configsections()
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
