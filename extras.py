import argparse
from parser import Parser
import sys

from lxml.html import document_fromstring


from podcasts import PodcastsAPI


def argparser(x=None):
    p = argparse.ArgumentParser()
    p.add_argument(
        "-f",
        "--feedurl",
        nargs=2,
        dest="feedurl",
        action="store",
        help="Show a feed URL for a given podcast search",
    )
    p.add_argument(
        "-s",
        "--scan",
        nargs=2,
        dest="scan",
        action="store",
        help="scan an RSS file for text strings",
    )
    p.add_argument(
        "-u",
        "--urlof",
        nargs=2,
        dest="urlof",
        action="store",
        help="print out URL of episode given its RSS file and guid",
    )

    if x:
        return p.parse_args(x.split())
    else:
        return p


def dofeedurl(args):
    """Do an itunes search for podcast subscriptions, and instead of subscribing, simply print the URL of the feed"""
    searchterm = args.feedurl[0]
    index = int(args.feedurl[1]) - 1
    podcastsdb = PodcastsAPI()
    podcastsdb.search(searchterm)
    feedurl = podcastsdb.feed_url(index)
    print(feedurl)


def doscan(args):
    """
    Take the arbitrary RSS filename given at command line and a text string, print out IDs of episodes that have a partial match of the given text.
    """
    # filename from user
    filename = args.scan[0]

    # string from user
    userstring = args.scan[1]

    items = scan(filename, userstring)

    for i in items:
        print(i)


def dourlof(args):
    """Given an ID of a podcast episode, print out the URL"""
    filename = args.urlof[0]
    guid = args.urlof[1]
    print("urlof [%s], [%s]" % (filename, guid))
    p = Parser()
    episodes = p.items(filename)
    for e in episodes:
        if guid == e.guid:
            print(e.url)


def scan(filename, userstring):
    "Search in an RSS file for an episode that has text in its string and print out its ID (guid) and text"
    p = Parser()
    p.parse(filename)
    episodes = p.episodes()
    items = []
    for e in episodes:
        if userstring in (e.description):
            html = e.description
            doc = document_fromstring(html)
            i = {}
            i["guid"] = e.guid
            i["text"] = doc.text_content()
            items.append(i)
    return items


if __name__ == "__main__":
    p = argparser()
    args = p.parse_args(sys.argv[1:])
    if args.urlof:
        dourlof(args)
    elif args.feedurl:
        dofeedurl(args)
    elif args.scan:
        doscan(args)
