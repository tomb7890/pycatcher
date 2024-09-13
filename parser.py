import xml.etree.ElementTree as ET
import logging
from episode import Episode
from dateutil import parser as dateutil_parser


class Parser:

    def __init__(self):
        # this may be obsolete.
        self.strict = True

    def parse(self, filename):
        self.filename = filename
        try:
            self.tree = ET.parse(self.filename)
        except ET.ParseError as pe:
            logging.info(f"Can't parse file {self.filename} : {pe}")

    def channel_image(self): 
        x = self.tree.findall(".//image//url")
        if len(x) > 0:
            return x[0].text

    def episodes(self):
        yahoo_ns = {"media": "http://search.yahoo.com/mrss/"}
        itunes_ns = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}

        episodes = []

        root = self._fetch_root()
        elements = root.findall("./channel/item")

        for el in elements:
            episode = Episode()
            self._pubdate_to_timestamp(el.find("pubDate").text, episode)
            episode.title = el.find("title").text
            episode.guid = el.find("guid").text
            episode.description = el.find("description").text
            episode.image = self._set_episode_image(el, itunes_ns, yahoo_ns)

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

    def _set_episode_image(self, el, itunes_ns, yahoo_ns):
        x = None
        elements = el.findall("itunes:image", itunes_ns)
        if len(elements) > 0:
            x = elements[0].get("href")
        else:
            elements = el.findall("media:thumbnail", yahoo_ns)
            if len(elements) > 0:
                x = elements[0].get("url")
        return x

    def _fetch_root(self):
        root = self.tree.getroot()
        return root

    def _pubdate_to_timestamp(self, timestamp, episode):
        try:
            # For the time being, I will ignore time zone -- it is
            # more trouble than it would be worth.  The utility of
            # these timestamps in this application is limited to the
            # ordering of the web report into a rough chrono order,
            # and podcasts aren't published so frequently as to make
            # this kind of precision necessary.

            episode.mktime = dateutil_parser.parse(timestamp, ignoretz=True)
            episode.pubDate = timestamp
        except ValueError as e:

            logging.warning(
                "pubdate parsing failed: \
                %s using data %s from %s"
                % (e, timestamp, episode.title)
            )


def dumpx(filepath):
    p = Parser()
    p.parse(filepath)
    eps = p.episodes
    for e in eps[0:200]:
        print(e.basename())


if __name__ == "__main__":
    pass
