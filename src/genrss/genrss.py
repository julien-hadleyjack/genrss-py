#!/usr/bin/env python
# -*- coding: utf-8 -*-

from episode import Episode
from history import History
from podcast import PodcastManager


def generate_podcasts():
    episodes = [Episode(**entry) for entry in History.get_lines()]
    manager = PodcastManager()

    for episode in episodes:
        manager.add_episode(episode)

    manager.generate_rss()
    manager.generate_html()

if __name__ == '__main__':
    generate_podcasts()
