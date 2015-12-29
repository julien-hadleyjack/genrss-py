#!/usr/bin/env python
# -*- coding: utf-8 -*-

import anyconfig
import os
import logging


__version__ = "0.1.0"

PATH = os.path.dirname(os.path.abspath(__file__))

config_path = [os.path.join(PATH, "config/default.yml"), "~/genrss.yml"]
CONFIG = anyconfig.load(config_path, ignore_missing=True)


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
