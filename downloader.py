from urllib.request import ProxyHandler, build_opener, install_opener, urlretrieve
from tqdm import tqdm
import lib

from downloadqueue import DownloadQueue


class Downloader:
    def __init__(self, f, s, a=None):
        self.fs = f
        self.sub = s
        self.args = a
        self.queue = DownloadQueue()

    def dodownload(self, db):
        self._make_directories_if_necessary()
        self._parse_download_and_purge_episodes(db)

    def _make_directories_if_necessary(self):
        dirs = [self.sub.base_podcasts_dir(), self.sub.podcasts_subdir()]
        for d in dirs:
            if not self.fs.path_exists(d):
                self.fs.mkdir(d)

    def _parse_download_and_purge_episodes(self, db):

        self._initialize_database(db)
        self._parse_and_inventory_episode_lists(db)
        self._download_the_new_episodes(db)
        self._purge_the_old_episodes(db)
        self._write_updates_to_database(db)

    def _initialize_database(self, db):
        db.load()

    def _parse_and_inventory_episode_lists(self, db):
        n = self.sub.maxeps
        self.episodes = self.sub.parse_rss_file()
        self.new_episodes_to_download = self.episodes[0:n]
        self.old_episodes_to_remove = self.episodes[n:]

    def _download_the_new_episodes(self, db):
        for e in self.new_episodes_to_download:
            self._queue_episode(e, db)
        self._download_episode_queue(db)

    def _purge_the_old_episodes(self, db):
        self._remove_old_episodes(db)
        self.queue.clear()

    def _write_updates_to_database(self, db):
        db.save()

    def _queue_episode(self, e, db):
        if not self._episode_is_registered(e, db):
            self._generate_filename_and_queue_episode(e, db)
        else:
            self._queue_anyway_if_file_is_missing(db, e)

    def _generate_filename_and_queue_episode(self, episode, db):
        filename = self._generate_file_name(episode, db, len(self.episodes))
        self.queue.queue(episode, filename)

    def _queue_anyway_if_file_is_missing(self, db, episode):
        registered_filename = db.filename_of(episode)
        if self._file_of_registered_episode_is_missing(episode, registered_filename):
            self.queue.queue(episode, lib.basename(registered_filename))

    def _download_episode_queue(self, db):
        for tuple in self.queue._queue:
            episode, destination_filename = tuple
            fullpath = self.fs.path_join(
                self.sub.podcasts_subdir(), destination_filename
            )
            if self.fs.path_exists(fullpath):
                print("target file exists! " + fullpath)
            else:
                try:
                    self.download_impl(episode, destination_filename)
                except Exception as e:
                    print(e)
            if self.fs.path_exists(fullpath):
                db.set_path(episode, fullpath)

    def _episode_is_registered(self, episode, db):
        return db.find_by_id(episode.guid)

    def _file_of_registered_episode_is_missing(self, episode, registered_filename):
        return not self.fs.path_exists(registered_filename)

    def _remove_old_episodes(self, db):
        for e in self.old_episodes_to_remove:
            if self._episode_is_registered(e, db):
                self._delete_file(e, db)
                self._delete_registry_entry(e, db)

    def download_impl(self, episode, destination_filename):
        fetch(
            episode.url,
            self.fs.path_join(self.sub.podcasts_subdir(), destination_filename),
            self.sub.title,
            self.args,
        )

    def _generate_file_name(self, episode, db, max):

        """

        Generate a new file name that is not yet in use

        A file name is typically the text of an episode's TITLE
        element.  However sometimes there are duplicate (repeating)
        TITLEs, e.g. "Week in Review". In this case a modified version
        must be generated to avoid the exception by the filesystem
        when a second file with the same name is created.  A numerical
        suffix is appended to the filename to avoid duplication.


        """

        count = 1

        proposal = episode.basename()
        while True:
            if count > max:
                raise RuntimeError
            count = count + 1
            if not self._in_use(db, proposal):
                break
            proposal = (
                episode.filename_base() + "-%d" % count + episode.filename_extension()
            )
        return proposal

    def _in_use(self, db, filename):
        if db.has_filename(filename):
            return True
        if self.queue.in_use(filename):
            return True
        return False

    def _delete_file(self, e, db):

        self.fs.prune_file(db.filename_of(e))

    def _delete_registry_entry(self, e, db):
        db.remove_entry(e.guid)


class FakeDownloader(Downloader):
    def __init__(self, fs, subscription):
        Downloader.__init__(self, fs, subscription)

    def download_impl(self, episode, destination):
        self.fs.touch(self.sub.podcasts_subdir(), destination)


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def fetch(url, output_path, program, args):
    # Some very popular podcasts reject the Python user agent.
    proxy = ProxyHandler({})
    opener = build_opener(proxy)
    opener.addheaders = [
        (
            "User-Agent",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30",
        )
    ]
    install_opener(opener)

    if not args.quiet:
        with DownloadProgressBar(
            unit="B",
            unit_scale=True,
            miniters=1,
            desc=program + " " + url.split("/")[-1],
        ) as t:

            urlretrieve(url, output_path, t.update_to)
    else:
        urlretrieve(url, output_path)


if __name__ == "__main__":
    pass
