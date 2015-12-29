#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytz as pytz

from . import CONFIG, get_logger
import os
import re
import datetime
from .tracklist import TracklistManager


class Episode(object):

    def __init__(self, pid, show, title, time_added, file_path, duration, description, categories, thumbnail, url,
                 **kargs):
        self.pid = pid
        self.show = show
        self.title = title
        # self.type = _type
        self.time_added = time_added
        # self.mode = mode
        self.file_path = file_path
        self.duration = duration
        self.description = description
        # self.channel = channel
        self.categories = categories
        self.thumbnail = thumbnail.replace("150_84", CONFIG["technical"]["thumbnail-size"])
        self.url = url

        self.directory_path, self.file_name = os.path.split(self.file_path)
        self.sub_directory = self.get_subdir_name()
        self.file_extension = os.path.splitext(self.file_name)[1]
        self.media_type = self.get_media_type(self.file_extension)
        self.exists = os.path.exists(self.file_path)
        self.file_size = os.path.getsize(self.file_path) if self.exists else "0"

        self.feed_url = self.generate_feed_url()

        self.tracklist = TracklistManager.get_tracklist(self.pid) if CONFIG["technical"]["tracklist"] else []

        get_logger().debug("Creating Episode:\n\t%s", repr(self))

    def url_base(self):
        base = CONFIG["url-base"]
        folder = self.sub_directory + "/" if self.sub_directory else ""
        return base + folder

    def generate_feed_url(self):
        return self.url_base() + self.file_name

    def get_subdir_name(self):
        subdir_name = re.sub("[']+", "", self.show)
        subdir_name = re.sub("[^a-zA-Z0-9_\-\./]+", "_", subdir_name)
        directory_name = os.path.split(self.directory_path)[1]
        return directory_name if directory_name == subdir_name else ""

    @staticmethod
    def get_media_type(file_extension):
        extension = {
            ".aac": "audio/mp4",
            ".m4a": "audio/mp4",
            ".mp4": "video/mp4"
        }

        return extension.get(file_extension, "audio/mpeg")

    def format_date(self):
        dt = datetime.datetime.fromtimestamp(int(self.time_added), tz=pytz.utc)
        return dt.strftime("%a, %d %b %Y %H:%M:%S %z")

    def __bool__(self):
        return self.exists

    def __repr__(self):
        template = "Episode[show={self.show}, title={self.title}, pid={self.pid}, " \
                   "timeadded={self.time_added}, exists={self.exists}]"
        return template.format(**locals())
