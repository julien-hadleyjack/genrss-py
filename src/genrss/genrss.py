#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import get_logger
from .tracklist import TracklistManager
from .episode import Episode
from .history import History
from .podcast import PodcastManager


def generate_podcasts():
    try:
        get_logger().info("Getting episode information from get_iplayer history.")
        episodes = [Episode(**entry) for entry in History.get_lines()]
    except KeyboardInterrupt:
        get_logger().warn("Aborting. Closing tracklist manager.")
        TracklistManager.db.close()
        return
    except BaseException as e:
        get_logger().warn("Closing tracklist manager.")
        TracklistManager.db.close()
        raise e

    manager = PodcastManager()

    get_logger().info("Adding episodes to the corresponding podcasts")
    for episode in episodes:
        manager.add_episode(episode)

    manager.generate_rss()
    manager.generate_html()

    get_logger().info("Finished.")

if __name__ == '__main__':
    generate_podcasts()
