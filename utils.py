#!/usr/bin/env python

import sys
import os
import json
import socket
from config import Config


def get_config():
    """
    Instantiate config from disk
    :return:
    """
    config_name = socket.getfqdn()

    try:
        plat_config = Config(config_name).get_config()
        return plat_config
    except NameError:
        print("Error in instantiating config for " + config_name)
