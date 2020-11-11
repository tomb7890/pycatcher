from prefs import get_subscription_names, lookup_int, lookup_string
from subscription import Subscription
from index import Index
import os 


def find_subscription_by_index(index):
    names = get_subscription_names()
    section = names[index]
    subscription = Subscription()
    initialize_subscription(subscription, section)
    return subscription


def initialize_subscription(subscription, name):
    subscription.set_title(name)
    subscription.set_feedurl(lookup_string(name, "url")) 
    subscription.set_maxeps(lookup_int(name, "maxeps") )
    subscription.set_rssfile(lookup_string(name, "rssfile"))
    initialize_database(subscription)

def initialize_database(subscription):
    fullpath = subscription.full_path_to_index_file()
    subscription.database = Index(fullpath)
    if os.path.exists(fullpath):
        subscription.database.load()


def get_all_subscriptions():
    names = get_subscription_names()
    a = []
    for n in names:
        s = Subscription()
        initialize_subscription(s, n)
        a.append(s)
    return a
