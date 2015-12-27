import os
from tinydb import TinyDB, Query
import unittest

import anyconfig

from tests import TEST_PATH


def initialize():
    import genrss
    import logging
    PATH = TEST_PATH
    genrss.CONFIG.update(
        anyconfig.load(os.path.join(TEST_PATH, "data/custom.yml"), ac_template=True, ac_context=locals()))

    tmp_dir = os.path.dirname(genrss.CONFIG["technical"]["tracklist-db"])
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir, exist_ok=True)

    logging.basicConfig(**genrss.CONFIG["logging"])

initialize()

from genrss import CONFIG, get_logger
from genrss.episode import Episode
from genrss.history import History
from genrss.podcast import PodcastManager
from genrss.tracklist import Tracklist, TracklistManager


class TestGeneral(unittest.TestCase):
    def test_config(self):
        assert "url-base" in CONFIG
        assert isinstance(CONFIG["shows"], list)


class TestEpisode(unittest.TestCase):
    def setUp(self):
        self.lines = History.get_lines()
        self.test_episodes = [Episode(**entry) for entry in History.get_lines()]

    def test_tracklist_exists(self):
        episodes = [Episode(**entry) for entry in self.lines]
        for episode in episodes:
            self.assertGreater(len(episode.tracklist), 0)

    def test_with_tracklist(self):
        episodes = [Episode(**entry) for entry in self.lines]
        self.assertEqual(len(episodes), 30)

    def test_without_tracklist(self):
        tracklist_setting = CONFIG["technical"]["tracklist"]
        CONFIG["technical"]["tracklist"] = False

        episodes = [Episode(**entry) for entry in self.lines]

        self.assertEqual(len(episodes), 30)
        CONFIG["technical"]["tracklist"] = tracklist_setting

    def test_subdir_name(self):
        directory_names = [
            '6_Mix',
            'Annie_Mac',
            'BBC_Radio_1s_Essential_Mix',
            'Composer_of_the_Week',
            'DJ_Edu_-_Destination_Africa',
            'David_Rodigan',
            'Don_Letts',
            'Essential_Classics',
            'Gilles_Peterson',
            'Hip_Hop_with_Semtex',
            'Jamie_Cullum',
            'My_Playlister',
            'Pete_Tong',
            'RnB_with_CJ_Beatz',
            'The_Craig_Charles_Funk_and_Soul_Show',
            'Through_the_Night',
            'Trevor_Nelsons_Soul_Show',
            'UKG_with_Cameo',
            'World_on_3'
        ]

        for episode in self.test_episodes:
            self.assertIn(episode.sub_directory, directory_names)

    def test_media_type(self):
        for episode in self.test_episodes:
            self.assertEqual("audio/mp4", episode.media_type)

    def test_date(self):
        expected = [
            "Sat, 10 May 2014 06:00:44 +0100",
            "Sun, 08 Jun 2014 19:06:11 +0100",
            "Sat, 21 Jun 2014 04:02:21 +0100",
            "Thu, 26 Jun 2014 19:17:49 +0100",
            "Thu, 26 Jun 2014 19:21:36 +0100",
            "Thu, 26 Jun 2014 19:24:23 +0100"
        ]
        for episode, expected_date in zip(self.test_episodes[::5], expected):
            self.assertEqual(expected_date, episode.format_date())


class TestHistory(unittest.TestCase):
    def test_lines(self):
        lines = History.get_lines()
        self.assertEqual(len(lines), 30)

        for entry in lines:
            self.assertEqual(len(entry), 17)
            self.assertIn("pid", entry)

    def test_line(self):
        expected = {
            "pid": "b042cv1h",
            "show": "BBC Radio 1's Essential Mix",
            "title": "Jimmy Edgar",
            "type": "radio",
            "time_added": "1399694444",
            "mode": "flashaaclow1",
            "file_path": "/podcast/BBC_Radio_1s_Essential_Mix/BBC_Radio_1s_Essential_Mix_-_Jimmy_Edgar_b042cv1h_default.m4a",
            "version": "default",
            "duration": "7200",
            "description": "\"This Essential Mix is Ultramajic doing Detroit radio circa 1993. It's all of my inspirations put into one mix, modernised melodically and meticulously blended\". Jimmy Edgar, May 2014.",
            "channel": "BBC Radio 1",
            "categories": "Music,Dance & Electronica",
            "thumbnail": "http://ichef.bbci.co.uk/programmeimages/p01ysm3l/b042cv1h_150_84.jpg",
            "guidance": "",
            "url": "http://www.bbc.co.uk/programmes/b042cv1h.html",
            "episode_num": "",
            "series_num": ""
        }

        self.assertDictEqual(History.get_lines()[0], expected)


class TestPodcastManager(unittest.TestCase):
    def setUp(self):
        self.manager = PodcastManager()

        episodes = [Episode(**entry) for entry in History.get_lines()]
        for episode in episodes:
            self.manager.add_episode(episode)

    def test_add(self):
        self.manager = PodcastManager()

        episodes = [Episode(**entry) for entry in History.get_lines() if entry["show"] == "BBC Radio 1's Essential Mix"]
        for episode in episodes:
            self.manager.add_episode(episode)

        self.assertEqual(len(self.manager.podcasts), 1)
        self.assertEqual(len(self.manager.podcasts["BBC Radio 1's Essential Mix"].episodes), 4)

        self.assertEqual(len(self.manager.fallback.episodes), 0)

    def test_get_all(self):
        self.assertEqual(len(self.manager.podcasts), len(CONFIG["shows"]))
        self.assertEqual(len(self.manager.get_all_podcasts()), len(CONFIG["shows"]) + 1)
        self.assertIsInstance(self.manager.get_all_podcasts(), list)

    def test_rss(self):
        self.manager.generate_rss()

    def test_html(self):
        episodes = [Episode(**entry) for entry in History.get_lines()]
        manager = PodcastManager()

        for episode in episodes:
            manager.add_episode(episode)

        self.manager.generate_html()


class TestPodcast(unittest.TestCase):

    pass


class TestTracklist(unittest.TestCase):
    def setUp(self):
        self.lines = History.get_lines()

    def test_tracklist_all(self):
        for line in self.lines:
            tracklist = TracklistManager.get_tracklist(line["pid"])
            self.assertIsInstance(tracklist, list)
            self.assertGreater(len(tracklist), 0)

    def test_tracklist_all_db(self):
        get_logger().info("Tracklist database at %s", CONFIG["technical"]["tracklist-db"])
        with TinyDB(CONFIG["technical"]["tracklist-db"], indent=2) as db:
            for line in self.lines:
                result = db.get(Query().pid == line["pid"])
                self.assertIsInstance(result["tracklist"], list)

    def test_tracklist_compare(self):
        get_logger().info("Tracklist database at %s", CONFIG["technical"]["tracklist-db"])
        with TinyDB(CONFIG["technical"]["tracklist-db"], indent=2) as db:
            self.assertListEqual(Tracklist("b042bqrs").listing, db.get(Query().pid == "b042bqrs")["tracklist"])

    def test_in_db(self):
        get_logger().info("Tracklist database at %s", CONFIG["technical"]["tracklist-db"])
        with TinyDB(CONFIG["technical"]["tracklist-db"], indent=2) as db:
            self.assertTrue(db.get(Query().pid == "b045xwkl"))

    def test_tracklist_db(self):
        get_logger().info("Tracklist database at %s", CONFIG["technical"]["tracklist-db"])
        with TinyDB(CONFIG["technical"]["tracklist-db"], indent=2) as db:
            self.assertEqual(len(db.get(Query().pid == "b045xwkl")["tracklist"]), 22)

    def test_tracklist_new(self):
        self.assertEqual(len(Tracklist("b046cs3d").listing), 21)
