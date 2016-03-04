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

        trim_querystring_from_filename(src, sub)

        dest = e.locallink()

        if os.path.exists(src):
            disksize = os.path.getsize(src)
            if int(disksize) != int(e.enclosure_length ):
                vprint("!!!! episdode %s's length is %d, expected to be %d " %
                       (src, disksize, int(e.enclosure_length)))

        vprint("making link from %s to  %s " % (src, dest))
        if True == link_creation_test(src, dest):
            os.link(src, dest)


def trim_querystring_from_filename(filename, subscription):
    '''
    Rename file on disk from the actual file name (sometimes with a
    query string appended by the file downloader) to the expected
    name taken from the url of the RSS enclosure.
    '''

    QUERY_STRING_MARKER = '?'
    WILDCARD = '*'

    fileptrn = filename + QUERY_STRING_MARKER + WILDCARD
    g = glob.glob(fileptrn)
    x = "trim_querystring_from_filename: %s using fileptrn %s" % (filename, fileptrn)
    vprint(x)
    if len(g) > 0:
        actual = g[0]
        if actual:
            vprint("[%s], [%s] " % (actual, filename))
            if not os.path.exists(filename):
                os.rename(actual, filename)


def vprint(msg):
    # parser = Command.get_sorted_list_of_episodes
    if True: # parser.args:
        if Command.Args().parser.verbose:
            print msg

if __name__ == '__main__':
    main()
