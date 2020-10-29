import pytest

from main import list_episodes, play_episode
from subscription import Subscription
from filesystem import FakeFileSystem
from mediaplayer import FakeMediaPlayer
from index import FakeIndex
from downloader import FakeDownloader
import argparser

@pytest.fixture()
def allsubs():
    maximum_episodes_to_keep = 5
    allsubs = [
        Subscription(
            None,
            "The Rich Roll Podcast",
            maximum_episodes_to_keep,
            "test/data/TheRichRollPodcast/100120.rss",
        ),
        Subscription(
            None,
            "The Agenda with Steve Paikin (Video)",
            maximum_episodes_to_keep,
            "test/data/TheAgendawithStevePaikinVideo/012820.rss"
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

    for s in allsubs:
        s.database = FakeIndex()
        
    return allsubs



@pytest.fixture()
def fdl(ffs, allsubs):
    return FakeDownloader(ffs, allsubs[1])


@pytest.fixture()
def sub():
    sub = Subscription(None, "The Agenda with Steve Paikin (Video)")
    sub.rssfile = "test/data/TheAgendawithStevePaikinVideo/012820.rss"
    sub.maxeps = 7
    return sub


@pytest.fixture()
def ffs():
    return FakeFileSystem()




def test_list_episodes(allsubs, ffs, fdl):

    expected = """>>> 1. Mistakes, Bad Decisions, and Fallout
>>> 2. Success Through Failure
>>> 3. Meeting Canada's Greenhouse Gas Targets
>>> 4. Infrastructure Challenges in Ontario
>>> 5. New Supports for Northern Farmers
>>> 6. Conservative Leadership Race Begins
>>> 7. Ontario's Municipal Finances"""

    subscription = select_subscription_download_and_verify(allsubs, fdl, ffs)
    
    output = list_episodes(subscription, ffs)
    assert output == expected

def select_subscription_download_and_verify(allsubs, fdl, ffs):
    subscription = allsubs[1]
    subscription.maxeps = 7
    fdl.dodownload(subscription.database)
    download_and_test(subscription, ffs, fdl)
    return subscription


def download_and_test(sub, ffs, fdl):
    n = len(ffs.listdir(sub.podcasts_subdir()))
    assert sub.maxeps == n


def test_play_episode_valid_choice(allsubs, ffs, fdl):
    player = FakeMediaPlayer()
    select_subscription_download_and_verify(allsubs, fdl, ffs)
    
    args = argparser.argparser("--play 2 5")
    result = play_episode(ffs, player, args, allsubs)

    assert result.success 
    assert player.played() == "xvlc '/home/tomb/podcasts/TheAgendawithStevePaikinVideo/New Supports for Northern Farmers.mp4'"


def test_play_episode_out_of_bounds_index(allsubs, ffs, fdl):
    player = FakeMediaPlayer()
    select_subscription_download_and_verify(allsubs, fdl, ffs)
    
    args = argparser.argparser("--play 2 999999")
    result = play_episode(ffs, player, args, allsubs)
    
    assert not result.success
    
def test_play_episode_sub_out_of_bounds(allsubs, ffs, fdl):
    player = FakeMediaPlayer()

    select_subscription_download_and_verify(allsubs, fdl, ffs)
    
    args = argparser.argparser(f"--play {len(allsubs) + 1} 1 ")
    result = play_episode(ffs, player, args, allsubs)
    
    assert not result.success

def test_play_episode_with_non_integer_sub_index(allsubs, ffs, fdl):
    player = FakeMediaPlayer()

    select_subscription_download_and_verify(allsubs, fdl, ffs)

    args = argparser.argparser("--play # 1")
    result = play_episode(ffs, player, args, allsubs)

    assert not result.success

def test_play_episode_with_non_integer_ep_index(allsubs, ffs, fdl):
    player = FakeMediaPlayer()

    select_subscription_download_and_verify(allsubs, fdl, ffs)

    args = argparser.argparser("--play 3 # ")
    result = play_episode(ffs, player, args, allsubs)

    assert not result.success
