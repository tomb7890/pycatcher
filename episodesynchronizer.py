import logging

from index import episode_is_registered

from episodequeue import EpisodeQueue

logging.basicConfig(level=logging.INFO)


class EpisodeSynchronizer:
    def __init__(self, filesystem, subscription, downloader, args=None):
        self.filesystem = filesystem
        self.subscription = subscription
        self.args = args
        self.downloader = downloader
        self.episodequeue = EpisodeQueue(subscription, filesystem)

    def dodownload(self, db):
        self._make_directories_if_necessary()
        self._initialize_database(db)
        self._organize_episodes_to_fetch_and_destroy(db)
        self._fetch_the_new_episodes(db)
        self._destroy_the_old_episodes(db)
        self._write_updates_to_database(db)

    def _make_directories_if_necessary(self):
        dirs = [
            self.subscription.base_podcasts_dir(),
            self.subscription.podcasts_subdir(),
        ]
        for d in dirs:
            if not self.filesystem.path_exists(d):
                self.filesystem.mkdir(d)

    def _initialize_database(self, db):
        if db.exists():
            db.load()

    def _organize_episodes_to_fetch_and_destroy(self, db):
        n = self.subscription.maxeps
        self.episodes = self.subscription.episodes()
        self.new_episodes_to_download = self.episodes[0:n]
        self.old_episodes_to_remove = self.episodes[n:]

    def _fetch_the_new_episodes(self, db):
        for e in self.new_episodes_to_download:
            self.episodequeue.enqueue(e, db)
        self._download_episode_queue(db)

    def _destroy_the_old_episodes(self, db):
        self._remove_old_episodes(db)
        self.episodequeue.clear()

    def _write_updates_to_database(self, db):
        db.save()

    def _download_episode_queue(self, db):
        for tuple in self.episodequeue.queue._queue:
            episode, destination_filename = tuple
            fullpath = self.filesystem._full_path(
                self.subscription.podcasts_subdir(), destination_filename
            )
            if self.filesystem.path_exists(fullpath):
                logging.warning("Target file already exists: %s", fullpath)
            else:
                try:
                    self.downloader.download_impl(episode, destination_filename)
                except Exception as e:
                    logging.exception(
                        "Error downloading %s: %s", destination_filename, e
                    )
            if self.filesystem.path_exists(fullpath):
                db.set(episode, fullpath)

    def _remove_old_episodes(self, db):
        for e in self.old_episodes_to_remove:
            if episode_is_registered(db, e):
                self._delete_file(e, db)
                self._delete_registry_entry(e, db)

    def _delete_file(self, e, db):
        self.filesystem.unlink(db.get(e))

    def _delete_registry_entry(self, e, db):
        db.delete(e.guid)


if __name__ == "__main__":
    pass
