from lxml import html
from subscription import Subscription
from report import (
    make_report_from_sorted_data,
    write_report_file,
    ReportDatum,
    enumerate_all_downloaded_episodes,
)
import tempfile
import parser
import pytest


XPATH_SELECTION_OF_DATE_COLUMN = './/div[@class="col-sm-3 date-column"]'
EXPECTED_DATE_OF_REPORT = "Thu, 01 Oct 2020 03:30:00 GMT"


def gather_all_subscriptions():
    maximum_episodes_to_keep = 3
    subs = [
        Subscription(
            None,
            "The Rich Roll Podcast",
            maximum_episodes_to_keep,
            "test/data/TheRichRollPodcast/100120.rss",
        ),
        Subscription(
            None,
            "Beat Your Genes",
            maximum_episodes_to_keep,
            "test/data/BeatYourGenes/100120.rss",
        ),
        Subscription(
            None,
            "Freakonomics",
            maximum_episodes_to_keep,
            "test/data/FreakonomicsRadio/100120.rss",
        ),
        Subscription(
            None,
            "Nutrition Facts",
            maximum_episodes_to_keep,
            "test/data/NutritionFactswithDrGreger/100120.rss",
        ),
        Subscription(
            None,
            "The Exam Room",
            maximum_episodes_to_keep,
            "test/data/TheExamRoom/100120.rss",
        ),
    ]
    return subs


def test_making_report():

    with tempfile.NamedTemporaryFile("r") as f:
        subs = gather_all_subscriptions()
        data = []

        for s in subs:
            p = parser.Parser()
            channel_image = p.channel_image(s.rssfile)
            episodes = p.items(s.rssfile)
            for e in episodes:
                d = ReportDatum(e, s, channel_image)
                data.append(d)

        text = make_report_from_sorted_data(data)
        write_report_file(f.name, text)

        text = f.read()
        assert "Rich Roll" in text

        tree = html.fromstring(text)
        date_of_third_row = tree.xpath(XPATH_SELECTION_OF_DATE_COLUMN)[3]
        assert date_of_third_row.text == EXPECTED_DATE_OF_REPORT


def test_making_report_with_no_episode_data():

    with tempfile.NamedTemporaryFile("r") as f:
        datas = []

        text = make_report_from_sorted_data(datas)
        write_report_file(f.name, text)

        tree = html.fromstring(f.read())
        assert 0 == len(tree.xpath(XPATH_SELECTION_OF_DATE_COLUMN))


def test_making_report_with_one_episode_datum():

    with tempfile.NamedTemporaryFile("r") as f:
        subs = gather_all_subscriptions()
        datas = []

        for s in subs:
            episodes = s.episodes()
            for e in episodes:
                channel_image = None
                d = ReportDatum(e, s, channel_image)
                datas.append(d)

        text = make_report_from_sorted_data(datas[:1])
        write_report_file(f.name, text)

        tree = html.fromstring(f.read())
        assert 1 == len(tree.xpath(XPATH_SELECTION_OF_DATE_COLUMN))


@pytest.mark.parametrize("num_downloaded_episodes", [0, 1, 2])
def test_enumerate_all_downloaded_episodes(num_downloaded_episodes):
    class MyFakeIndex:
        def __init__(self):
            self.count = 0

        def find(self, guid):
            self.count = self.count + 1
            if self.count <= num_downloaded_episodes:
                return True
            return False

    subscriptions = gather_all_subscriptions()
    for s in subscriptions:
        db = MyFakeIndex()
        s.database = db

        reportdata = []
        enumerate_all_downloaded_episodes(s, reportdata)
        assert len(reportdata) == num_downloaded_episodes
