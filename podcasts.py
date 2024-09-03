import urllib
import json
from urllib.request import urlopen


class PodcastsAPI:
    def __init__(self):
        pass

    def search(self, searchterm):
        self._results = _podcastquery(searchterm)
        return self._results

    def feed_url(self, index):
        return self._results[r"results"][index][r"feedUrl"]

    def collection_name(self, index):
        return self._results[r"results"][index][r"collectionName"]


class FakePodcastsAPI(PodcastsAPI):
    def __init__(self):
        self.fp = "test/data/terminator.json"
        PodcastsAPI.__init__(self)

    def search(self, searchterm):
        with open(self.fp, "r") as f:
            text = f.read()
            self._results = json.loads(text)
            return self._results


def search_for_podcast_and_decorate_results(term):
    results = _podcastquery(term)
    return decorate_results(results)


def _podcastquery(searchterm):
    url = (
        "https://itunes.apple.com/search?term=%s&limit=25&entity=podcast"
        % urllib.parse.quote_plus(searchterm)
    )
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


def decorate_results(results):
    s = "\n\n"
    i = 1
    for p in results[r"results"]:
        s = s + ("%d. [%s] %s " % (i, p[r"artistName"], p[r"collectionName"]))
        i = i + 1
        s = s + "\n"
    return s
