#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from operator import attrgetter
from urllib.request import urlretrieve
from io import open

from PIL import Image
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from . import CONFIG, get_logger, ROOT_DIR


class PodcastManager(object):
    def __init__(self):

        self.podcasts = {}
        self.fallback = Podcast(CONFIG["fallback"]["title"], is_collection=True)

    def get_all_podcasts(self):
        return list(self.podcasts.values()) + [self.fallback]

    def add_episode(self, episode):
        """

        :param episode:
        :type episode: episode.Episode
        """

        if episode.show not in CONFIG["shows"]:
            podcast = self.fallback
        elif episode.show not in self.podcasts:
            podcast = Podcast(episode.show)
            self.podcasts[episode.show] = podcast
        else:
            podcast = self.podcasts[episode.show]

        if not CONFIG["technical"]["check-episode"] or episode:
            podcast.episodes.append(episode)

    def generate_html(self):
        env = Environment(loader=FileSystemLoader(ROOT_DIR / 'template'),
                          autoescape=True, trim_blocks=True, lstrip_blocks=True,
                          undefined=StrictUndefined)
        template = env.get_template("index.html")
        output = template.render(config=CONFIG, manager=self)

        file_path = os.path.join(CONFIG["file-base"], CONFIG["technical"]["overview-path"])
        with open(file_path, "w", encoding="utf8") as file:
            get_logger().info("Writing HTML overview at %s", file_path)
            file.write(output)

    def generate_rss(self):
        for podcast in self.get_all_podcasts():
            podcast.save()


class Podcast():
    def __init__(self, title, short_description=None, html_description=None, is_collection=False):

        self.title = title
        self.episodes = []

        self.is_collection = is_collection
        self.short_description = short_description or CONFIG["fallback"]["short-description"]
        self.html_description = html_description or CONFIG["fallback"]["html-description"]

        get_logger().debug("Creating podcast:\n\t%s", repr(self))

    @staticmethod
    def format_date(dt):
        return dt.strftime("%a, %d %b %Y %H:%M:%S +0100")

    def image_url(self):
        image_url = CONFIG["fallback"]["image-url"]

        if not self.is_collection and len(self.episodes) > 0:
            image_location = None
            image_name = CONFIG["technical"]["image-name"]

            for episode in self.episodes:
                location = os.path.join(episode.directory_path, image_name)
                if os.path.exists(location):
                    image_location = location
                    image_url = episode.sub_directory + image_name
                    break
            if not image_location:
                for episode in self.episodes:
                    if os.path.exists(episode.directory_path):
                        image_location = os.path.join(episode.directory_path, image_name)
                        urlretrieve(episode.thumbnail, image_location)
                        image_url = episode.sub_directory + image_name
                        break

            if image_location:
                self.crop_image(image_location)

        return CONFIG["url-base"] + image_url

    @staticmethod
    def crop_image(image_location):
        # http://www.carlbednorz.de/python-create-square-thumbnails-from-images-with-pil/
        img = Image.open(image_location)
        width, height = img.size
        if width != height:
            upper_x = int((width / 2) - (height / 2))
            upper_y = 0
            lower_x = int((width / 2) + (height / 2))
            lower_y = height
            img = img.crop((upper_x, upper_y, lower_x, lower_y))
            assert img.size[0] == img.size[1]
            get_logger().debug("Saving a new thumbnail at %s", image_location)
            img.save(image_location, "JPEG")

    def get_rss_filename(self):
        if not self.episodes:
            get_logger().info("No episodes found for %s. No rss file name.", self.title)
        elif self.is_collection:
            return CONFIG["fallback"]["rss-file"]
        else:
            return re.sub("[^a-zA-Z0-9_\-\./]+", "_", self.title) + ".rss"

    def save(self):
        if not self.episodes:
            get_logger().info("No episodes found for %s. Can't save rss feed", self.title)
            return

        sorted_episodes = sorted(self.episodes, key=attrgetter('time_added'), reverse=True)

        env = Environment(loader=FileSystemLoader(ROOT_DIR / 'template'),
                          autoescape=True, trim_blocks=True, lstrip_blocks=True,
                          undefined=StrictUndefined)
        template = env.get_template("feed.rss")
        output = template.render(config=CONFIG, sorted_episodes=sorted_episodes, podcast=self)

        file_path = os.path.join(CONFIG["file-base"], self.get_rss_filename())
        with open(file_path, "w", encoding="utf8") as file:
            get_logger().info("Saving %d episodes at %s.", len(self.episodes), file_path)
            file.write(output)

    def __repr__(self):
        return "Podcast[title={self.title}, episodes={amount}]".format(amount=len(self.episodes), **locals())
