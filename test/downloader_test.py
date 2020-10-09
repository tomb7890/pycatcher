import pytest
from subscription import Subscription
from filesystem import FakeFileSystem
from downloader import FakeDownloader
from index import FakeIndex


@pytest.fixture()
def sub():
    sub = Subscription(None, "The Agenda with Steve Paikin (Video)")
    sub.maxeps = 6
    yield sub


@pytest.fixture()
def ffs():
    yield FakeFileSystem()


@pytest.fixture()
def fdl(ffs, sub):
    yield FakeDownloader(ffs, sub)


@pytest.fixture()
def dbfile():
    yield FakeIndex()


def set_expectations_for_first_download(sub):
    sub.rssfile = "test/data/TheAgendawithStevePaikinVideo/012820.rss"
    return """Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4
Meeting Canadas Greenhouse Gas Targets.mp4
Infrastructure Challenges in Ontario.mp4
New Supports for Northern Farmers.mp4
Conservative Leadership Race Begins.mp4""".splitlines()


def set_expectations_for_second_download(sub):
    sub.rssfile = "test/data/TheAgendawithStevePaikinVideo/013020.rss"
    return """Old Age The Secret to Happiness.mp4
Daniel Levitin How to Age Well.mp4
Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4
Meeting Canadas Greenhouse Gas Targets.mp4
Infrastructure Challenges in Ontario.mp4""".splitlines()


def set_expectations_for_third_download(sub):
    sub.rssfile = "test/data/TheAgendawithStevePaikinVideo/013120.rss"
    return """Passing on Political Leadership.mp4
Forgery Morrisseau and Indigenous Art.mp4
Old Age The Secret to Happiness.mp4
Daniel Levitin How to Age Well.mp4
Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4""".splitlines()


def test_downloading(sub, fdl, ffs, dbfile):
    e = set_expectations_for_first_download(sub)
    download_and_test(sub, ffs, fdl, dbfile, e)
    e = set_expectations_for_second_download(sub)
    download_and_test(sub, ffs, fdl, dbfile, e)
    e = set_expectations_for_third_download(sub)
    download_and_test(sub, ffs, fdl, dbfile, e)


def download_and_test(sub, ffs, fdl, dbfile, expected_files):
    fdl.dodownload(dbfile)
    n = len(ffs.listdir(sub.podcasts_subdir()))
    assert sub.maxeps == n

    for f in expected_files:
        t = ffs.path_join(
            sub.podcasts_subdir(),
            f,
        )
    assert ffs.path_exists(t)


def test_downloading_after_mischievously_deleting_an_episode_disk_file(
    sub, ffs, fdl, dbfile
):
    e = set_expectations_for_first_download(sub)
    download_and_test(sub, ffs, fdl, dbfile, e)

    fourth_file = ffs.path_join(sub.podcasts_subdir(), e[3])
    assert "Ontario" in fourth_file
    assert ffs.path_exists(fourth_file)
    ffs.prune_file(fourth_file)
    assert not ffs.path_exists(fourth_file)

    e = set_expectations_for_second_download(sub)
    download_and_test(sub, ffs, fdl, dbfile, e)


def test_downloading_after_micheievously_deleting_an_episode_registry_key(
    sub, ffs, fdl, dbfile
):
    e = set_expectations_for_first_download(sub)
    download_and_test(sub, ffs, fdl, dbfile, e)

    e = set_expectations_for_second_download(sub)
    download_and_test(sub, ffs, fdl, dbfile, e)

    dbfile.remove_entry(
        "http://podcasts.tvo.org/theagenda/video/2597629_12001291615.mp4"
    )
    assert len(dbfile.records()) == 5

    download_and_test(sub, ffs, fdl, dbfile, e)
    assert len(dbfile.records()) == 6

    e = set_expectations_for_third_download(sub)
    download_and_test(sub, ffs, fdl, dbfile, e)
