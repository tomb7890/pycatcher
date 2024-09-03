import os
import pytest
import random
from filesystem import FakeFileSystem
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


@pytest.fixture()
def hypothetical():
    class Hypothetical:
        path = "~/foo-bar/quux.mp3"
        filename = path.split("/")[-1]
        dir = "/".join(path.split("/")[0:-1])

    h = Hypothetical()
    yield h


@pytest.fixture()
def ffs():
    ffs = FakeFileSystem()
    yield ffs


@pytest.fixture()
def podcastdir(ffs):
    podcastroot = os.path.expanduser("~/podcasts")
    if os.path.exists(podcastroot):
        files = os.listdir(podcastroot)
        dirs = [
            os.path.join(podcastroot, f)
            for f in files
            if os.path.isdir(os.path.join(podcastroot, f))
        ]
        rdir = random.choice(dirs)
        podcastdir = rdir
        files = os.listdir(podcastdir)
        for f in files:
            ffs.touch(podcastdir, f)

    else:
        podcastdir = None

    yield podcastdir


def test_exception_thrown_on_repeated_call_to_mkdir():
    with pytest.raises(FileExistsError):
        ffs = FakeFileSystem()
        ffs.mkdir("foo")
        ffs.mkdir("foo")


def test_unlink_raises_exception_with_nonexistant_file():
    with pytest.raises(FileNotFoundError):
        ffs = FakeFileSystem()
        ffs.unlink("foo")


def test_unlink_raises_exception_with_nonexistant_dir_file():
    with pytest.raises(FileNotFoundError):
        ffs = FakeFileSystem()
        ffs.mkdir("foo")
        ffs.unlink("foo/bar")


def test_unlink_raises_exception_with_nonexistant_dir_dir_file():
    with pytest.raises(FileNotFoundError):
        ffs = FakeFileSystem()
        ffs.mkdir("foo")
        ffs.mkdir("foo/bar")
        ffs.unlink("foo/bar/baz")


def test_fake_listdir(ffs, podcastdir):
    try:
        if len(ffs.listdir(podcastdir)) > 0:
            assert len(os.listdir(podcastdir)) == len(ffs.listdir(podcastdir))
    except FileNotFoundError as e:
        print("Invalid podcast directory: %s" % e)


def test_fake_file_system_tests(ffs, hypothetical):

    assert not ffs.path_exists(hypothetical.dir)
    assert not ffs.path_exists(hypothetical.path)

    ffs.touch(hypothetical.dir, hypothetical.filename)

    assert 1 == len(ffs.listdir(hypothetical.dir))
    assert ffs.path_exists(hypothetical.path)

    ffs.unlink(hypothetical.path)

    assert not (ffs.path_exists(hypothetical.path))
    assert 0 == len(ffs.listdir(hypothetical.dir))

    known_unknown = "~/foo-bar/known_unknown.mp3"
    assert not (ffs.path_exists(known_unknown))


def test_pathexists_for_nested_empty_directory(ffs):
    dir = "/foo/bar"
    ffs.mkdir(dir)
    assert ffs.path_exists(dir)
