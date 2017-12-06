import xml
import os
import logging
import StringIO
import subscriptions
import episode
from downloader import FakeDownloader


def doreport(basedir):
    text = make_report_text(basedir)
    filename = os.path.join(basedir, 'report.html')
    write_report_file(filename, text)


def make_report_text(basedir):
    '''
    Collect all episodes from all subscriptions and sort them
    in reverse chronological order,  make an html report.
    '''
    alleps = []
    downloader = FakeDownloader()
    
    subs = subscriptions.Subscriptions(downloader, basedir)
    for sub in subs.items:
        try:
            episodes = sub.get_all_episodes()
            if episodes != None:
                for ep in episodes:
                    if os.path.exists(ep.localfile()):
                        alleps.append(ep)
        except xml.etree.ElementTree.ParseError, e:
            logging.warning("minidom parsing error:"+repr(e) +
                       'with subscription ' + repr(sub.get_rss_path()))

    episode.sort_rev_chron(alleps)
    return make_report_from_eps(alleps)


def write_report_file(filename, text):
    f = open(filename, 'w')
    f.write(text)
    f.close()


def make_report_from_eps(alleps):
    template = "<HTML>\n_BODY\n</HTML>"
    report = template
    f = StringIO.StringIO()
    for e in alleps:
        write_episode_to_report(f, e)
    report = report.replace("_BODY", f.getvalue())
    return report


def write_episode_to_report(f, ep):
    f.write("<H2>%s</H2>\n" % ep.subscription.title.encode('ascii', 'ignore'))
    f.write("<H4>%s</H4>\n" % ep.title.encode('ascii', 'ignore'))
    f.write("<DIV>%s</DIV>\n" % ep.pubDate)
    if ep.description:
        desc = ep.description
        adesc = desc.encode('ascii', 'ignore')
        f.write("<DIV>%s</DIV>\n" % adesc)
