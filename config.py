#!/usr/bin/env python
import sys
import os
import json


class Config(object):

    def __init__(self, name):
        self.name = name
        if os.path.isfile(self.name + ".json"):
            with open(self.name + ".json", 'r') as config_file:
                self.cfg = json.load(config_file)
        else:
            print("Error in config!")
            self.cfg = none

    def get_config(self):
        return self.cfg

    def get_name(self):
        return self.name
