import requests
from tqdm import tqdm
import os
import logging

from downloadqueue import DownloadQueue
logging.basicConfig(level=logging.INFO)


class Downloader:
    def __init__(self, filesystem, subscription, args=None):
        self.fs = filesystem
        self.sub = subscription
        self.args = args
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
        self._organize_episodes_to_fetch_and_destroy(db)
        self._fetch_the_new_episodes(db)
        self._destroy_the_old_episodes(db)
        self._write_updates_to_database(db)

    def _initialize_database(self, db):
        if db.exists():
            db.load()

    def _organize_episodes_to_fetch_and_destroy(self, db):
        n = self.sub.maxeps
        self.episodes = self.sub.episodes()
        self.new_episodes_to_download = self.episodes[0:n]
        self.old_episodes_to_remove = self.episodes[n:]

    def _fetch_the_new_episodes(self, db):
        for e in self.new_episodes_to_download:
            self._queue_episode(e, db)
        self._download_episode_queue(db)

    def _destroy_the_old_episodes(self, db):
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
        registered_filename = db.get(episode)
        if self._file_of_registered_episode_is_missing(episode, registered_filename):
            self.queue.queue(episode, os.path.basename(registered_filename))

    def _download_episode_queue(self, db):
        for tuple in self.queue._queue:

            episode, destination_filename = tuple

            fullpath = self._full_path(destination_filename)

            if self.fs.path_exists(fullpath):
                logging.info("Target file already exists: %s", fullpath)
            else:
                try:
                    self.download_impl(episode, destination_filename)
                except Exception as e:
                    logging.exception("Error downloading %s: %s", destination_filename, e)
            if self.fs.path_exists(fullpath):
                db.set(episode, fullpath)

    def _episode_is_registered(self, episode, db):
        return db.find(episode.guid)

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
            self._full_path(destination_filename),
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
            proposal = episode.numerify_filename(count)
        return proposal

    def _in_use(self, db, filename):
        if db.has(filename):
            return True
        if self.queue.in_use(filename):
            return True
        return False

    def _full_path(self, b):
        return self.fs.path_join(self.sub.podcasts_subdir(), b)

    def _delete_file(self, e, db):
        self.fs.unlink(db.get(e))

    def _delete_registry_entry(self, e, db):
        db.delete(e.guid)


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

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))
    if response.status_code == 200:
        with open(output_path, "wb") as file, tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc=program + " " + url.split("/")[-1],
            ncols=80,
            disable=args.quiet,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))


if __name__ == "__main__":
    pass
