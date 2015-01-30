import argparse
import glob
import os
import StringIO
import Subscriptions
import Episode
import Download
import Command

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

def vprint(msg):
    if Command.args:
        if Command.args.verbose:
            print msg 

def trim_junk_from_filename(filename, subscription):
    '''
    Rename file on disk from the actual file name (sometimes with a
    query string appended by the file downloader) to the expected 
    name taken from the url of the RSS enclosure. 
    '''
    fileptrn = filename + '?*' # extra junk 
    g = glob.glob(fileptrn)
    if len(g) > 0: 
        actual = g[0]
        # print "[%s], [%s] " % (actual, episode.localfile())
        if not os.path.exists(filename):
            os.rename(actual, filename)
    
def create_links( episodes, sub ):
    for e in episodes:

        src = e.localfile( )
        trim_junk_from_filename(src,sub)
        pd = sub.subscriptions.podcastsdir()
        if not os.path.exists(pd):
            os.mkdir(pd)
        subdir = os.path.join(pd, sub.dir)
        if not os.path.exists(subdir):
            os.mkdir(subdir)
        dest = e.locallink()

        vprint( "making link from %s to  %s " % ( src, dest ))
        if True == link_creation_test(src, dest):
            os.link( src, dest )

def link_creation_test( src, dst ):
    if os.path.exists( src ) and not os.path.exists ( dst ):
        return True
    return False

def dodownload(basedir):
    '''
    Download files
    '''
    subs = Subscriptions.Subscriptions(basedir)
    for sub in subs.items:
        if Command.args and Command.args.program:
            if -1 == sub.dir.find(Command.args.program):
                continue
        filename = sub.get_rss_file(Command.args.localrss)
        episodes = get_all_ep(filename, sub)
        Episode.sort_rev_chron(episodes)
        saved = episodes[:sub.maxeps]
        expired = episodes[sub.maxeps:]
        if None == saved:
            continue
        Download.download_new_files(sub, saved, basedir)
        create_links(saved, sub)
        prunefiles(expired)

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

