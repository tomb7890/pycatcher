import Command
import glob
import os


def link_creation_test(src, dst):
    if os.path.exists(src) and not os.path.exists(dst):
        return True
    return False


def create_links(episodes, sub):
    for e in episodes:
        src = e.localfile()
        trim_junk_from_filename(src, sub)
        pd = sub.subscriptions.podcastsdir()
        if not os.path.exists(pd):
            os.mkdir(pd)
            os.mkdir(os.path.join(pd, 'xml'))

        subdir = os.path.join(pd, sub.dir())
        if not os.path.exists(subdir):
            os.mkdir(subdir)
        dest = e.locallink()

        vprint("making link from %s to  %s " % (src, dest))
        if True == link_creation_test(src, dest):
            os.link(src, dest)


def trim_junk_from_filename(filename, subscription):
    '''
    Rename file on disk from the actual file name (sometimes with a
    query string appended by the file downloader) to the expected
    name taken from the url of the RSS enclosure.
    '''
    fileptrn = filename + '?*'  # question mark is a query string thing
    g = glob.glob(fileptrn)
    x = "trim_junk_from_filename: %s using fileptrn %s" % (filename, fileptrn)
    vprint(x)
    if len(g) > 0:
        actual = g[0]
        if actual:
            vprint("[%s], [%s] " % (actual, filename))
            if not os.path.exists(filename):
                os.rename(actual, filename)


def vprint(msg):
    if Command.args:
        if Command.args.verbose:
            print msg

if __name__ == '__main__':
    main()
