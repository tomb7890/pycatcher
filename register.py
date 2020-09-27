import os
from lib import podcasts_directory, data_directory, rss_directory, _media_subdirectory, \
    DEFAULTCONFIGFILE

from subscription import rss_file_name_from_text, DEFAULT_MAXEPS
from configparser import ConfigParser, DuplicateSectionError

def register(feedurl, title):
    try:
        _setup_config(feedurl, title)
        # _create_base_directories()
        # _create_subscription_directories(title)
        # _download_rss_file(feedurl, title)
    except DuplicateSectionError as e:
        print("Error adding %s: %s. " % (title, e))


def _create_base_directories():
    dirs = [podcasts_directory(), data_directory(), rss_directory()]
    for d in dirs:
        if not os.path.exists(d):
            os.mkdir(d)

def _create_subscription_directories(subscription):
    subscription_directories = [
        os.path.join(podcasts_directory(), _media_subdirectory(subscription)),
        os.path.join(data_directory(), _media_subdirectory(subscription))
    ]

    for d in subscription_directories:
        if not os.path.exists(d):
            os.mkdir(d)

def _setup_config(feedurl, title):

    cp = ConfigParser()
    cp.read(DEFAULTCONFIGFILE)
    section = title

    cp.add_section(section)
    cp.set(section, 'url', feedurl)
    cp.set(section, 'rssfile', rss_file_name_from_text(title))
    cp.set(section, 'maxeps', str(DEFAULT_MAXEPS))
    cp.write(open(DEFAULTCONFIGFILE, 'w'))


if __name__ == '__main__':
    pass
