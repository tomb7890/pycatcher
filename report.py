from io import StringIO

from string import Template
import xml.etree.ElementTree
import string


from lib import (
    sort_reverse_chronologically,
    configsections,
    set_sub_from_config,
    db_of_sub,
)


from subscription import Subscription


class ReportDatum:
    thumbnail: string
    textlabel: string
    href_text: string
    href_url: string
    pubdate: string
    mktime: object
    description: string

    def __init__(self, e, s):  
        if e.image is None:
            self.thumbnail = s.subscription_image
        else:
            self.thumbnail = e.image

        self.textlabel = e.title
        self.href_text = s.title
        self.href_url = episode_href(e)
        self.pubdate = e.pubDate
        self.mktime = e.mktime
        self.description = e.description


def doreport(outputfilename):
    text = make_report_text()
    write_report_file(outputfilename, text)


def make_report_text():
    reportdata = gather_episode_data_from_all_downloaded_podcasts()
    return make_report_from_sorted_data(reportdata)


def write_report_file(filename, text):
    if text is not None:
        with open(filename, "w") as f:
            f.write(text)
            f.close()


def gather_episode_data_from_all_downloaded_podcasts():
    reportdata = []
    cp, sections = configsections()
    for section in sections:
        try_to_get_episode_data(reportdata, cp, section)
    return reportdata


def try_to_get_episode_data(reportdata, cp, section):
    subscription = Subscription()
    try:
        set_sub_from_config(subscription, cp, section)
        db = db_of_sub(subscription)
        db.load()
        enumerate_all_downloaded_episodes(subscription, db, section, reportdata)

    except FileNotFoundError as e:
        print("Error with subscription %s: %s" % (subscription.title, e))

    except xml.etree.ElementTree.ParseError as e:
        print("Error with subscription %s: %s" % (subscription.title, e))


def make_report_from_sorted_data(reportdata):
    sort_reverse_chronologically(reportdata)
    return make_report_from_episodes(reportdata)


def enumerate_all_downloaded_episodes(subscription, db, section, reportdata):
    episodes = subscription.parse_rss_file()

    for e in episodes:
        if db.find(e.guid):
            d = ReportDatum(e, subscription)
            reportdata.append(d)


def episode_href(episode):
    return episode.guid


def make_report_from_episodes(reportdata):
    template = open_template_from_template_file("templates/main.html")
    with open("templates/header.html", "r") as f:
        header = f.read()
        buffer = StringIO()
        for d in reportdata:
            write_row_to_container(buffer, d)
        for d in reportdata:
            write_description_to_container(buffer, d)
        return template.substitute(bootstrap=header, body=buffer.getvalue())


def open_template_from_template_file(filename):
    with open(filename, "r") as f:
        templatetext = f.read()
        return Template(templatetext)


def write_description_to_container(f, d):
    template = open_template_from_template_file("templates/panel.html")
    f.write(template.substitute(id=d.href_url, heading=d.textlabel, body=d.description))


def write_row_to_container(f, d):
    template = open_template_from_template_file("templates/row.html")
    f.write(
        template.substitute(
            image=d.thumbnail,
            sub_title=d.href_text,
            href=d.href_url,
            ep_title=d.textlabel,
            pubdate=d.pubdate,
        )
    )
