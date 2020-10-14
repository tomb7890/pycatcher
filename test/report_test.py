from lxml import html
from subscription import Subscription
from report import make_report_from_sorted_data, write_report_file, ReportDatum
import tempfile


XPATH_SELECTION_OF_DATE_COLUMN = './/div[@class="col-sm-3 date-column"]'
EXPECTED_DATE_OF_REPORT = "Thu, 01 Oct 2020 03:30:00 GMT"


def gather_all_subscriptions():
    maximum_episodes_to_keep = 3
    subs = [
        Subscription(
            None,
            "The Agenda with Steve Paikin (Video)",
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
            episodes = s.parse_rss_file()
            for e in episodes:
                d = ReportDatum(e, s)
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
            episodes = s.parse_rss_file()
            for e in episodes:
                d = ReportDatum(e, s)
                datas.append(d)

        text = make_report_from_sorted_data(datas[:1])
        write_report_file(f.name, text)

        tree = html.fromstring(f.read())
        assert 1 == len(tree.xpath(XPATH_SELECTION_OF_DATE_COLUMN))
