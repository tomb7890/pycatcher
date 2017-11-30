# Pycatcher
### Simple podcast subscription and downloading

Pycatcher is a Python command-line podcast client designed to be used with a preferred media player application. Pycatcher processes a configuration file for subscription information, and downloads media content as ordinary files. Individual media items (episodes) are written to disk with filenames derived from the text of the RSS TITLE elements.

### Requirements
Pycatcher requires Python 2.7 and the `wget` utility.

### Configuration
A `pycatcher.conf` configuration file is used to specify the selection and configuration of the downloading of media content.
The main section, `[general]`, is used to specify the file system location of media content, using `podcasts-directory`.  An optional `data-directory` can be used to override the location of primary data storage.

Additional sections are used to describe each feed, or subscription of interest.  An `url` option within a feed's section indicates the internet address of a the feed.  An `rssfile` option is used to specify a name for the local copy of the RSS file.  A `maxeps` option for a feed will specify the total number of items, or episodes, that will be downloaded.   As new items appear in a feed, the oldest episodes that exceed `maxeps` will be removed from the disk.


### Installation
Rename the provided `pycatcher.conf.example` to `pycatcher.conf` and modify accordingly.



### Execution
`$ python application.py`
