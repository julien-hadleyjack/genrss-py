#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from . import CONFIG, get_logger
from io import open


class History(object):
    @staticmethod
    def get_lines():
        download_history = CONFIG["technical"]["download-history"]
        get_logger().debug("Opening download history at %s", download_history)
        with open(download_history, encoding="utf8", mode="r") as history:
            return [History.get_line(line) for line in history]

    @staticmethod
    def get_line(line):
        keys = ["pid", "show", "title", "type", "time_added", "mode", "file_path", "version", "duration",
                "description", "channel", "categories", "thumbnail", "guidance", "url", "episode_num", "series_num"]

        return {key: value for key, value in zip(keys, line.split("|"))}
