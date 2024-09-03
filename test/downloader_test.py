import pytest
from subscription import Subscription
from filesystem import FakeFileSystem
from downloader import FakeDownloader
from index import FakeIndex


@pytest.fixture()
def sub():
    sub = Subscription(None, "The Agenda with Steve Paikin (Video)")
    sub.maxeps = 6
    return sub


@pytest.fixture()
def ffs():
    return FakeFileSystem()


@pytest.fixture()
def fdl(ffs, sub):
    return FakeDownloader(ffs, sub)


@pytest.fixture()
def db():
    return FakeIndex()


def set_expectations_for_first_download(sub, n):
    sub.rssfile = "test/data/TheAgendawithStevePaikinVideo/012820.rss"
    return """Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4
Meeting Canadas Greenhouse Gas Targets.mp4
Infrastructure Challenges in Ontario.mp4
New Supports for Northern Farmers.mp4
Conservative Leadership Race Begins.mp4""".splitlines()[
        0:n
    ]


def set_expectations_for_second_download(sub, n):
    sub.rssfile = "test/data/TheAgendawithStevePaikinVideo/013020.rss"
    return """Old Age The Secret to Happiness.mp4
Daniel Levitin How to Age Well.mp4
Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4
Meeting Canadas Greenhouse Gas Targets.mp4
Infrastructure Challenges in Ontario.mp4""".splitlines()[
        0:n
    ]


def set_expectations_for_third_download(sub, n):
    sub.rssfile = "test/data/TheAgendawithStevePaikinVideo/013120.rss"
    return """Passing on Political Leadership.mp4
Forgery Morrisseau and Indigenous Art.mp4
Old Age The Secret to Happiness.mp4
Daniel Levitin How to Age Well.mp4
Mistakes Bad Decisions and Fallout.mp4
Success Through Failure.mp4""".splitlines()[
        0:n
    ]


def test_downloading(sub, fdl, ffs, db):
    for n in range(0, 7):
        ffs.reset()
        e = set_expectations_for_first_download(sub, n)
        download_and_test(sub, ffs, fdl, db, e)
        e = set_expectations_for_second_download(sub, n)
        download_and_test(sub, ffs, fdl, db, e)
        e = set_expectations_for_third_download(sub, n)
        download_and_test(sub, ffs, fdl, db, e)


def download_and_test(sub, ffs, fdl, db, expected_files):
    fdl.dodownload(db)
    n = len(ffs.listdir(sub.podcasts_subdir()))
    assert sub.maxeps == n

    for f in expected_files:
        t = ffs.path_join(
            sub.podcasts_subdir(),
            f,
        )
        assert ffs.path_exists(t)
        assert db.has(t)


def test_downloading_after_mischievously_deleting_an_episode_disk_file(
    sub, ffs, fdl, db
):
    n = 6
    e = set_expectations_for_first_download(sub, n)
    download_and_test(sub, ffs, fdl, db, e)

    fourth_file = ffs.path_join(sub.podcasts_subdir(), e[3])
    assert "Ontario" in fourth_file
    assert ffs.path_exists(fourth_file)
    ffs.unlink(fourth_file)
    assert not ffs.path_exists(fourth_file)

    e = set_expectations_for_second_download(sub, n)
    download_and_test(sub, ffs, fdl, db, e)


def test_downloading_after_micheievously_deleting_an_episode_registry_key(
    sub, ffs, fdl, db
):
    n = 6
    e = set_expectations_for_first_download(sub, n)
    download_and_test(sub, ffs, fdl, db, e)

    e = set_expectations_for_second_download(sub, n)
    download_and_test(sub, ffs, fdl, db, e)

    db.delete("http://podcasts.tvo.org/theagenda/video/2597629_12001291615.mp4")
    assert len(db.records()) == 5

    download_and_test(sub, ffs, fdl, db, e)
    assert len(db.records()) == 6

    e = set_expectations_for_third_download(sub, n)
    download_and_test(sub, ffs, fdl, db, e)
