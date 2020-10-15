
import re
import logging
import os
from parser import Parser

DEFAULT_MAXEPS=3

logger = logging.getLogger()

def rss_file_name_from_text(text):
    # return os.path.join(re.sub(r'\W', '', text ), '.rss' )
    return re.sub(r'\W', '', text ) + '.rss' 

class Subscription:
    def __init__(self, feedurl=None, title=None, maxeps=3, rssfile=None):

        self.parser = Parser()

        # A subscription object is constructed primarily following
        # using itunes to search for a podcast.  The three attributes
        # below come from the results object that follows searching
        # itunes, and are used for writing to an RSS file.

        # The feedurl is the internet source for the RSS file, and
        # will be used as an attribute in the config file entry, as is
        # the maxeps attribute.

        self.feedurl = feedurl
        self.title = title 
        logging.info("Subscription.__init_ is now setting title to be [%s]" % self.title)

        self.maxeps = maxeps
        self.rssfile = rssfile
        
    def parse_rss_file(self, filename=None):
        if filename is None:
            filename = self.rssfile

        return self.parser.parse_rss_file(filename)

    def title(self):
        return self.title
        
    def filesystem_safe_sub_title(self):
        return re.sub(r'\W', '', self.title)

    def rss_file_name_from_title_attribute(self):
        return self.filesystem_safe_sub_title() + '.rss'

    # def full_path_to_rss_file_name(self):
    #     filename = self.rss_file_name_from_title_attribute()
    #     os.path.join(dir, filename)

    # def full_path_to_index_file_name(self):
    #     filename = self.index_file_name_from_title_attribute()
    #     os.path.join(dir, filename)

    def base_podcasts_dir(self):
        return os.path.expanduser("~/podcasts")

    def _sub_dir(self):
        return re.sub(r'\W', '', self.title )
    
    def podcasts_subdir(self): 
        return os.path.join( self.base_podcasts_dir(), 
                            self._sub_dir())
    
if __name__ == '__main__':
    pass


