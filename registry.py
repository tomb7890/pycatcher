from prefs import DEFAULTCONFIGFILE

from subscription import rss_file_name_from_text, DEFAULT_MAXEPS
from configparser import ConfigParser, DuplicateSectionError


class Registry:
    def __init__(self):
        pass

    def register(self, feedurl, title):
        try:
            self._setup_config(feedurl, title)
        except DuplicateSectionError as e:
            print("Error adding %s: %s. " % (title, e))

    def _setup_config(self, feedurl, title):
        cp = ConfigParser()
        cp.read(DEFAULTCONFIGFILE)
        section = title

        cp.add_section(section)
        cp.set(section, "url", feedurl)
        cp.set(section, "rssfile", rss_file_name_from_text(title))
        cp.set(section, "maxeps", str(DEFAULT_MAXEPS))
        cp.write(open(DEFAULTCONFIGFILE, "w"))


class FakeRegistry(Registry):
    def __init__(self):
        Registry.__init__(self)

    def register(self, foo, bar):
        pass


if __name__ == "__main__":
    pass
