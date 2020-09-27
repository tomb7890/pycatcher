import argparser
import json
import logging

import sys
import urllib


import index
from urllib.request import urlopen
from register import register 
from subscription import Subscription
from parser import Parser 
from filesystem import FileSystem
from downloader import Downloader
from report import doreport
from downloader import fetch
from lib import mediaplay 

from lib import set_sub_from_config, \
    _get_sub_of_index, \
    full_path_to_index_file, \
    configsections

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
        fs = FileSystem()
        doreport(args, fs, 'report.html')

    if 'verbose' in args:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
    return 

def dosearch(args):
    results = podcastquery(args.search)
    print("\n\n") 
    i = 1
    for p in results[r'results']:
        print("%d. [%s] %s " % ( i, p[r'artistName'], p[r'collectionName'])) 
        i=i+1

def dofetch(args):
    searchterm = args.fetch[0]
    index = int(args.fetch[1])-1
    
    results = podcastquery(searchterm)
    feedurl = results[r'results'][index][r'feedUrl']
    print(feedurl)


def doscan(args):
    filename = (args.scan[0])
    s = (args.scan[1])
    from lxml.html import document_fromstring

    html = open(filename, 'rb').read()
    doc = document_fromstring(html)
    
    myxpath = './/item/description[contains(., "%s")]' % s
    print(myxpath)
    elements=doc.xpath(myxpath)
    print(len(elements))
    for e in elements:
        print(e.xpath("guid"))
    
    p = Parser()
    episodes = p.scan_rss_file(filename)

    for e in episodes:
        if s in (e.itunes['description']):
            html = e.itunes['description']
            doc = document_fromstring(html)
            print(doc.text_content())
            print(e.guid)
            print("\n")
            
def dourlof(args):
    filename = args.urlof[0]
    guid = args.urlof[1]
    print("urlof [%s], [%s]" % ( filename, guid ))

    p = Parser()
    episodes = p.scan_rss_file(filename)

    for e in episodes:
        if guid == e.guid:
            print(e.url)
            

    
def dosubscribe(args):
    searchterm = args.subscribe[0]
    index = int(args.subscribe[1])-1
    results = podcastquery(searchterm)
    feedurl = results[r'results'][index][r'feedUrl']
    collectionname = results[r'results'][index][r'collectionName']
    register(feedurl, collectionname)

def doplay(args):
    i = int(args.play[0]) - 1
    sub = _get_sub_of_index(i)
    selection = int(args.play[1])

    def playhandler(*args):
        episode = args[0]
        n = args[1]
        filename = args[2]
        print("%d: %s" % (n, episode.title ) )
        if ( n == selection ) :
            mediaplay(filename)

    traverse(args, sub, playhandler)

def dolistepisodes(args):
    i = int(args.listepisodes) - 1
    sub = _get_sub_of_index(i)

    def printhandler(*args):
        episode = args[0]
        n = args[1] 
        title = episode.title
        print(">>> %d: %s" % (n, title) )

    traverse(args, sub, printhandler)
    
def traverse(args, sub, handler):
    episodes = sub.parse_rss_file()
    db = index.Index(full_path_to_index_file(sub))
    db.load()

    fs = FileSystem()

    n = 0 
    for e in episodes:
        g = e.guid
        if g in db.table.keys():
            filename = db.table[e.guid]
            if fs.path_exists(filename):
                n = n + 1
                handler(e, n, filename)

def podcastquery(searchterm):
    url = 'https://itunes.apple.com/search?term=%s&limit=25&entity=podcast' % \
        urllib.parse.quote_plus(searchterm)
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def doupdate(args):
    cp, sections = configsections()
    try:
        index = int(args.update) - 1 
        section  = sections[index]
        download_rss_file(cp, section, args)

    except ValueError:
        if args.update == 'all' :
            for section in sections:
                download_rss_file(cp, section, args)

def dolistsubscriptions(args):
    cp, sections = configsections()
    i = 1
    for s in sections:
        print("%d: %s " % ( i, s ))
        i = i + 1

def dodownload(args):
    try:
        cp, sections = configsections()
        if args.download[0] == 'all':
            for section in sections:
                download_section(cp, section, args)
        else:
            i = int(args.download[0]) - 1
            section  = sections[i]
            download_section(cp, section, args)
            
    except urllib.error.URLError as x:
        print(x)

def download_section(cp, section, args):
    sub = download_rss_file(cp, section, args)
    db = index.Index(full_path_to_index_file(sub))
    fs = FileSystem()
    dl = Downloader(fs, sub, args)
    dl.dodownload(db)

def download_rss_file(cp, section, args):
    sub = Subscription()
    set_sub_from_config(sub, cp, section)
    fetch(sub.feedurl, sub.rssfile, sub.title, args)
    return sub 

def print_debug(episodes, subscription, db, rssfile):
    for e in episodes[0:subscription.maxeps]:
        print('guid:' + e.guid) 
        print('url:' +  e.url) 
        print('title:' + e.title) 
        print('basename:' + e.basename()) 
        print("\n\n") 


if __name__ == '__main__':
    main()
