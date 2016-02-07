import argparse

import os
import StringIO
import Subscriptions
import Episode
import wget
import Command
import Library

def main():
    global args
    '''
    Entry point of application examines command arguments
    and routes execution accordingly
    '''
    # parser = Command.getparser()
    # args = parser.parse_args()
    Command.init_args()
    basedir = os.environ['PODCASTROOT']
    if Command.args.report:
        doreport(basedir)
    else:
        dodownload(basedir)

def get_all_ep(filename, sub):
    doc = sub.minidom_parse( filename )
    if None == doc:
        return None
    episodes = sub.process_dom_object( doc, filename  )
    return episodes


def dodownload(basedir):
    '''
    Download files
    '''
    for sub in get_list_of_subscriptions_production(basedir):
        try:
            episodes = get_sorted_list_of_episodes(sub, False)
            new = episodes[:sub.maxeps]
            old = episodes[sub.maxeps:]
            get_new_episodes(sub, new, basedir)
            release_old_episodes(old)
        except xml.parsers.expat.ExpatError, e:
            Library.vprint("minidom parsing error:"+repr(e) +
                           'with subscription ' + repr(sub.get_rss_path()))


def get_list_of_subscriptions_production(basedir):
    matchpattern = Command.args.program
    return get_list_of_subscriptions(basedir, matchpattern)


def get_list_of_subscriptions(basedir, match=None):
    subs = []
    subs = Subscriptions.Subscriptions(basedir,  match)
    return subs.items


def release_old_episodes(expired):
    prunefiles(expired)


def get_sorted_list_of_episodes(sub, use_local):
    episodes = sub.get_all_ep(use_local)
    Episode.sort_rev_chron(episodes)
    return episodes


def get_latest_episodes(sub):
    episodes = get_sorted_list_of_episodes(sub, True)
    new = episodes[:sub.maxeps]
    return new


def get_new_episodes(sub, saved, basedir):
    wget.download_new_files(sub, saved, basedir)
    Library.create_links(saved, sub)




def appdir():
    path=os.path.dirname(os.path.realpath(__file__))
    return path

def doreport(basedir):
    '''
    Collect all episodes from all subscriptions and sort them
    in reverse chronological order,  make an html report.
    '''
    alleps = []
    subs = Subscriptions.Subscriptions(basedir)
    for sub in subs.items:
        filename = sub.get_rss_file(True)
        episodes = get_all_ep(filename, sub)
        if episodes != None:
            for ep in episodes:
                if os.path.exists(ep.localfile()):
                    alleps.append(ep)
    Episode.sort_rev_chron(alleps)


    template = os.path.join(appdir(), 'report.html.template' )
    report = open(template, 'r').read()
    f = StringIO.StringIO()
    for e in alleps:
        write_episode_to_report(f, e)
    report = report.replace("_BODY", f.getvalue())
    write_report_file(report)


def write_episode_to_report(f, ep):
    f.write("<H2>%s</H2>\n" % ep.subscription.title.encode('ascii', 'ignore'))
    f.write("<H4>%s</H4>\n" % ep.title.encode('ascii', 'ignore'))
    f.write("<DIV>%s</DIV>\n" % ep.pubDate)
    if ep.description:
        desc = ep.description
        adesc = desc.encode('ascii', 'ignore')
        f.write("<DIV>%s</DIV>\n" % adesc)


def write_report_file(report):
    reportfile = os.path.join(appdir(), 'report.html')
    f = open(reportfile, 'w')
    f.write(report)
    f.close()


def prunefiles(doomedeps):
    for ep in doomedeps:
        ep.prune_file()
        ep.prune_link()


if __name__ == '__main__':
    main()
