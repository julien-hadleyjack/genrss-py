#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from lxml import html
from tinydb import TinyDB, Query
import requests
from . import get_logger, CONFIG


class TracklistManager(object):

    db = TinyDB(CONFIG["technical"]["tracklist-db"], indent=2, separators=(',', ': '))
    get_logger().info("Starting tracklist manager with database at %s", CONFIG["technical"]["tracklist-db"])

    @classmethod
    def get_tracklist(cls, pid):
        result = cls.db.get(Query().pid == pid)
        get_logger().info("Result for pid %s: %s", pid, result)
        if not result:
            get_logger().debug("Getting tracklist for: %s", pid)
            tracklist = Tracklist(pid).listing
            cls.db.insert({"pid": pid, "tracklist": tracklist})
        else:
            tracklist = result["tracklist"]

        return tracklist


class Tracklist(object):
    def __init__(self, pid):
        """
        See also https://github.com/StevenMaude/bbc_radio_tracklisting_downloader.

        :param pid: the unique pid of the episode
        """
        self.pid = pid

        self.listing = []

        url = "http://www.bbc.co.uk/programmes/{}/segments.inc".format(self.pid)

        page = requests.get(url)
        tree = html.fromstring(page.text)

        for track in tree.xpath('//div[@class="segment__track"]'):
            try:
                artist_names = track.xpath('.//span[@property="byArtist"]//span[@class="artist"]/text()')
            except ValueError:
                artist_names = []

            artist = ', '.join(artist_names)

            try:
                title, = track.xpath('.//p/span[@property="name"]/text()')
            except ValueError:
                title = ''

            self.listing.append([artist, title])

    def __repr__(self):
        return "Tracklist[pid={self.pid}, len={amount}]".format(amount=len(self.listing), **locals())
