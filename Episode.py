import os, re, string


def sort_rev_chron(episodes):

    """
    Reverse chronological sorting is something we want to ensure
    most recent things appear at the top.
    """

    if episodes is None:
        return None
    episodes.sort(key = lambda x: x.mktime, reverse=True )


class Episode:
    def __init__(self, s):
        self.subscription = s
        self.pubDate = None
        self.url = None
        self.title = None
        self.mktime = None
        self.description = ""

    def localfile(self):
        '''
        Provide an absolute filename for the downloaded media. It is
        taken by removing the last component of the enclosure url from
        an rss file.
        '''
        filename = self._filename_from_url()
        subdir = self.subscription.dir()
        absfile = os.path.join(subdir, filename)
        filename = self._clean_up_filename(absfile)
        filename = filename.replace("%20",  " ")
        return filename

    def locallink(self):
        '''
        Provide an absolute filename for the symbolic link to be made
        to the local media file.  The link name is created using the
        filesystem-safe characters from the episodes's RSS title
        attribute; the link's extension is taken from the pointed-to
        filename, so as to preserve the media type.
        '''
        prettyname = self.title + self._file_extension()
        validchars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        prettyname = ''.join(c for c in prettyname if c in validchars)

        dir = self.subscription.subscriptions.podcastsdir()
        subdir = os.path.join(dir, self.subscription.dir())
        filename = os.path.join( subdir, prettyname )
        return filename

    def prune_file(self):
        filename = self.localfile()
        if os.path.exists( filename ):
            os.unlink( filename )

    def prune_link(self):
        link = self.locallink()
        if os.path.exists( link ):
            os.unlink( link )

    def _file_extension(self):
        src = self.localfile( )
        thedot = src.rfind(".")
        extension = src[thedot:]
        return extension

    def _filename_from_url(self): # , url ):
        lastslash = self.url.rfind("/") + 1
        filename = self.url[lastslash:]
        return filename

    def _clean_up_filename( self, xfile ):
        ptrn = re.compile(r'(.*\.\w{2,3})\?.+$')
        m = ptrn.match( xfile )
        if m:
            cleaned = m.group(1)
            return cleaned
        return xfile



if __name__ == '__main__':
    pass
