#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
from pathlib import Path

import anyconfig

__version__ = "0.2.0"

ROOT_DIR = Path(__file__).parent.absolute()

config_path = [
    ROOT_DIR / "config" / "default.yml",
    Path.home() / "genrss.yml",
]
CONFIG = anyconfig.load(config_path, ac_ignore_missing=True)


def fix_config():
    if not CONFIG["url-base"].endswith("/"):
        CONFIG["url-base"] += "/"
    CONFIG["technical"]["thumbnail_size"] = CONFIG["technical"]["thumbnail-size"].replace("x", "_")

    CONFIG["file-base"] = os.path.expanduser(CONFIG["file-base"])
    CONFIG["technical"]["tracklist-db"] = os.path.expanduser(CONFIG["technical"]["tracklist-db"])
    CONFIG["technical"]["download-history"] = os.path.expanduser(CONFIG["technical"]["download-history"])

    if not os.path.exists(CONFIG["file-base"]):
        os.makedirs(CONFIG["file-base"])


fix_config()

logger_instance = None


def get_logger():
    global logger_instance
    if logger_instance is None:
        logging.basicConfig(**CONFIG["logging"])
        logging.getLogger("requests").setLevel(logging.WARNING)
        logger_instance = logging.getLogger(__name__)
        logger_instance.debug("Loading logger: %s", CONFIG["logging"])
    return logger_instance
