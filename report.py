from io import StringIO
import prefs
from string import Template
import xml.etree.ElementTree
import parser
from lib import initialize_subscription
from subscription import Subscription
import logging


class ReportDatum:
    def __init__(self, e, s, channel_image):
        if e.image is None:
            self.thumbnail = channel_image
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
    for name in prefs.get_subscription_names():
        try_to_get_episode_data(reportdata, name)
    return reportdata


def try_to_get_episode_data(reportdata, subname):
    subscription = Subscription()
    try:
        initialize_subscription(subscription, subname)
        enumerate_all_downloaded_episodes(subscription, reportdata)

    except FileNotFoundError as e:
        print("Error with subscription %s: %s" % (subscription.title, e))

    except xml.etree.ElementTree.ParseError as e:
        print("Error with subscription %s: %s" % (subscription.title, e))


def make_report_from_sorted_data(reportdata):
    sort_reverse_chronologically(reportdata)
    return generate_podcast_report(reportdata)


def sort_reverse_chronologically(reportdata):
    reportdata.sort(key=lambda x: x.mktime, reverse=True)


def enumerate_all_downloaded_episodes(subscription, reportdata):
    p = parser.Parser()
    inputfile = subscription.rssfile
    try:
        p.parse(inputfile)
        channel_image = p.channel_image()
        episodes = p.episodes()

        for e in episodes:
            if subscription.database.find(e.guid):
                d = ReportDatum(e, subscription, channel_image)
                reportdata.append(d)

    except xml.etree.ElementTree.ParseError as pe:
        logging.info(f"Can't parse file {inputfile} : {pe}")


def episode_href(episode):
    return episode.guid


def generate_podcast_report(episode_data):
    template = open_template_from_template_file("templates/main.html")
    with open("templates/header.html", "r") as f:
        header = f.read()

        # summaries
        summary_table = StringIO()
        for d in episode_data:
            _generate_episode_summary_row(summary_table, d)

        # descriptions
        description_list = StringIO()
        for d in episode_data:
            _generate_episode_description_item(description_list, d)

        return template.substitute(
            header=header,
            episode_summaries=summary_table.getvalue(),
            episode_descriptions=description_list.getvalue(),
        )


def open_template_from_template_file(filename):
    with open(filename, "r") as f:
        templatetext = f.read()
        return Template(templatetext)


def _generate_episode_description_item(f, d):
    template = open_template_from_template_file("templates/panel.html")
    f.write(template.substitute(id=d.href_url, heading=d.textlabel, body=d.description))


def _generate_episode_summary_row(f, d):
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
