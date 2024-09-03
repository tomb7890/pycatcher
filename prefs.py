from configparser import ConfigParser
import os

DEFAULTCONFIGFILE = "prefs.conf"


def get_subscription_names():
    cp = ConfigParser()
    cp.read(DEFAULTCONFIGFILE)
    sections = cp.sections()
    return sections


def lookup_string(name, element):
    cp = ConfigParser()
    cp.read(DEFAULTCONFIGFILE)
    return cp.get(name, element)


def lookup_int(name, element):
    cp = ConfigParser()
    cp.read(DEFAULTCONFIGFILE)
    return cp.getint(name, element)


def prefs_dirs_podcasts():
    return os.path.expanduser("~/podcasts")


def prefs_dirs_data():
    return os.path.expanduser("~/.podcasts-data/")


def prefs_dirs_rss():
    return os.path.join(prefs_dirs_data(), "rss")
