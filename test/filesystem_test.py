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
    ffs =  FakeFileSystem()
    yield ffs


@pytest.fixture()
def podcastdir(ffs):
    podcastroot = os.path.expanduser("~/podcasts")
    if os.path.exists(podcastroot):
        files = os.listdir(podcastroot)
        dirs = [os.path.join(podcastroot, f)   for f in files if           os.path.isdir(os.path.join(podcastroot, f))]
        rdir = random.choice(dirs)
        podcastdir = rdir
        files = os.listdir(podcastdir)
        for f in files:
            ffs.touch(podcastdir, f)

    yield podcastdir



def test_exception_thrown_on_repeated_call_to_mkdir():
    pass


def test_fake_listdir(ffs, podcastdir):
    if len(ffs.listdir(podcastdir)) > 0:
        assert len(os.listdir(podcastdir)) == len(ffs.listdir(podcastdir))
        

def test_exception_from_making_redundant_link(ffs, hypothetical):
    with pytest.raises(ValueError):
        ffs.mkdir(hypothetical.dir)
        ffs.touch(hypothetical.dir, hypothetical.path)

        dest = "~/foo-bar/dest.mp3"
        ffs.link(hypothetical.path,
                      dest)

        ffs.link(hypothetical.path,
                      dest)


def test_fake_file_system_tests(ffs, hypothetical):

    assert not ffs.path_exists(hypothetical.dir)
    assert not ffs.path_exists(hypothetical.path)

    ffs.touch(hypothetical.dir, hypothetical.filename)

    assert(1 == len(ffs.listdir(hypothetical.dir)))
    assert (ffs.path_exists(hypothetical.path))

    ffs.prune_file(hypothetical.path)

    assert not (ffs.path_exists(hypothetical.path))
    assert (0 == len(ffs.listdir(hypothetical.dir)))

    known_unknown = "~/foo-bar/known_unknown.mp3"
    assert not (ffs.path_exists(known_unknown))


def test_link_creation_test(ffs):
    src = '~/.podcasts-data/freakonomics/freakonomics_podcast112917.mp3'
    dst = '~/podcasts/freakonomics/Are We Running Out of Ideas.mp3 '
    ffs.touch(ffs._directory_portion_of_full_path(src),
                   ffs._filename_portion_of_full_path(src))
    assert (ffs.path_exists(src))
    assert not (ffs.path_exists(dst))
    assert (ffs.link_creation_test(src, dst))
    ffs.mkdir(ffs._directory_portion_of_full_path(dst))
    ffs.link(src,dst)

    assert (ffs.path_exists(dst))
    assert not (ffs.link_creation_test(src, dst)) 


def test_pathexists_for_nested_empty_directory(ffs):
    dir = '/foo/bar'
    ffs.mkdir(dir)
    assert (ffs.path_exists(dir))

@pytest.mark.skip(reason="")
def test_file_rename(ffs, hypothetical):
    ffs.rename(hypothetical.path,
                    ffs.rename(hypothetical.path) )
