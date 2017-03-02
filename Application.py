import xml
import os
import StringIO
import Subscriptions
import Episode
import wget
import Command
import Library
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
        report = doreport(basedir)
        write_report_file(report)
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
        try:
            episodes = get_sorted_list_of_episodes(sub)
            new = episodes[:sub.maxeps]
            old = episodes[sub.maxeps:]
            get_new_episodes(sub, new, basedir, downloader)
            release_old_episodes(old)
        except xml.etree.ElementTree.ParseError, error:
            Library.vprint("minidom parsing error:"+repr(error) +
                           'with subscription ' + repr(sub.get_rss_path()))


def get_list_of_subscriptions_production(basedir):
    match = None
    if Command.Args().parser.program:
        match = Command.Args().parser.program
    return get_list_of_subscriptions(basedir, match)


def get_list_of_subscriptions(basedir, match=None):
    subs = []
    subs = Subscriptions.Subscriptions(basedir, match)
    return subs.items


def release_old_episodes(expired):
    prunefiles(expired)


def get_sorted_list_of_episodes(sub):
    episodes = sub.get_all_episodes()
    Episode.sort_rev_chron(episodes)
    return episodes


def get_latest_episodes(sub):
    episodes = get_sorted_list_of_episodes(sub, True)
    new = episodes[:sub.maxeps]
    return new


def get_new_episodes(sub, saved, basedir, downloader):
    download_new_files(downloader, sub, saved)
    Library.create_links(saved, sub)


def prepare_queue(episodes):
    queue = []
    for episode in episodes:
        lf = episode.localfile()
        if os.path.exists(lf):
            logging.info("file already exists: " + lf)
        else:
            logging.info("queuing: " + lf)
            queue.append(episode.url)
    return queue


def download_new_files(downloader, subscription, episodes):
    logging.info("downloader ")
    queue = prepare_queue(episodes)
    if len(queue) > 0 :
        inputfile = 'urls.dat'

        downloader.addoption('--input-file', inputfile)
        downloader.addoption('--directory-prefix', subscription._data_subdir())
        if Command.Args().parser.limitrate:
            downloader.addoption('--limit-rate', Command.Args().parser.limitrate)

        downloader.url = subscription.url
        f = open(inputfile, 'w')
        f.write('%s\n' % ('\n'.join(queue)))
        f.close()
        downloader.execute()
        logging.info(downloader.getCmd)
        if os.path.exists(inputfile):
            os.unlink(inputfile)

def appdir():
    path = init_config()
    return path


def doreport(basedir):
    '''
    Collect all episodes from all subscriptions and sort them
    in reverse chronological order,  make an html report.
    '''
    alleps = []
    subs = Subscriptions.Subscriptions(basedir)
    for sub in subs.items:
        try:
            episodes = sub.get_all_episodes()
            if episodes != None:
                for ep in episodes:
                    if os.path.exists(ep.localfile()):
                        alleps.append(ep)
        except xml.etree.ElementTree.ParseError, e:
            if Command.Args().parser.verbose:
                print ("minidom parsing error:"+repr(e) +
                       'with subscription ' + repr(sub.get_rss_path()))

    Episode.sort_rev_chron(alleps)
    return make_report_from_eps(alleps)


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
