import xml.etree.ElementTree as ET
import logging
from episode import Episode
import re
import time


class Parser:

    def __init__(self):
        # this may be obsolete.
        self.strict = True

    def channel_image(self, filename):
        tree = ET.parse(filename)
        x = tree.findall(".//image//url")
        if len(x) > 0:
            return x[0].text

    def items(self, filename):
        yahoo_ns = {"media": "http://search.yahoo.com/mrss/"}
        itunes_ns = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}

        episodes = []
        root = self._fetch_root(filename)
        elements = root.findall("./channel/item")

        for el in elements:
            episode = Episode()
            self._pubdate_to_timestamp(el.find("pubDate").text, episode)
            episode.title = el.find("title").text
            episode.guid = el.find("guid").text
            episode.description = el.find("description").text
            episode.image = self._set_episode_image(episode, el, itunes_ns, yahoo_ns)

            e = el.find("enclosure")
            if e is not None:
                episode.url = e.get("url")
                episode.enclosure_length = e.get("length")

            if (
                episode.pubDate
                and hasattr(episode, "url")
                and episode.title
                and episode.guid
            ):
                episodes.append(episode)

        return episodes

    def _set_episode_image(self, episode, el, itunes_ns, yahoo_ns):
        x = None
        elements = el.findall("itunes:image", itunes_ns)
        if len(elements) > 0:
            x = elements[0].get("href")
        else:
            elements = el.findall("media:thumbnail", yahoo_ns)
            if len(elements) > 0:
                x = elements[0].get("url")
        return x

    def _fetch_root(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        return root

    def _pubdate_to_timestamp(self, timestamp, episode):
        try:
            fmtstring = r"%a, %d %b %Y %H:%M:%S"
            trimmed = self._trim_tzinfo(timestamp)
            pd = time.strptime(trimmed, fmtstring)
            episode.mktime = time.mktime(pd)  # seconds since the epoch
            episode.pubDate = timestamp
        except ValueError as e:

            logging.warning(
                "pubdate parsing failed: \
                %s using data %s from %s"
                % (e, timestamp, episode.title)
            )

    def _trim_tzinfo(self, t):

        # [Sat, 29 Apr 2006 20:38:00]
        # [Sat, 27 Feb 2010 06:00:00 EST]
        # [Fri, 13 June 2008 22:00:00]
        timezoneinfo = [
            r"\s[+-]\d\d\d\d$",
            r"\sGMT$",
            r"\sEDT$",
            r"\sCST$",
            r"\sPST$",
            r"\sEST$",
            r"\s+PDT$",
        ]

        for j in timezoneinfo:
            t = re.sub(j, "", t)
        return t


def dumpx(filepath):
    p = Parser()
    eps = p.items(filepath)
    for e in eps[0:200]:
        print(e.basename())


if __name__ == "__main__":
    pass
