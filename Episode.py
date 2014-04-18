import os, re, string

class Episode:
    def __init__(self, s):
        self.subscription = s
        self.pubDate = None
        self.url = None
        self.title = None
        self.mktime = None
        self.description = ""

    def localfile( self ): # episode, subscription ):
        filename = self._filename_from_url()
        subdir = os.path.join( self.subscription.subscriptions.basedir, self.subscription.dir )
        absfile = os.path.join( self.subscription.dir, filename )
        filename = self._clean_up_filename( absfile )
        filename = filename.replace("%20",  " ")
        return filename

    def locallink( self, linkdir  ):
        src = self.localfile( )

        thedot = src.rfind(".")
        extension = src[thedot:]
        prettyname = self.title + extension 

        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        prettyname = ''.join(c for c in prettyname if c in valid_chars)
        dest = os.path.join( linkdir, prettyname )
        # print "Prettyname is : [%s] " % prettyname
        return dest

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


def link_creation_test( src, dst ):
    if os.path.exists( src ) and not os.path.exists ( dst ):
        return True
    return False

if __name__ == '__main__':
    pass




