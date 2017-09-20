#!/usr/bin/env python

__author__ = 'Gengwg'
__copyright__ = "Apache"
__version__ = '0.0.3'

"""
A Script to back up the Palo Alto Netowrk firewall configs.
Run as a cronjob to back up the configs weekly.
"""

import requests
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString
import sys
import threading
import os
import argparse
import json
import logging
from logging import log
from datetime import date


# helper function
def parse_config(conf):
    myconfig = {}
    execfile(conf, myconfig)
    return myconfig


def pan_backup(config={}):
    """Dowload PAN configs to local."""

    try:
        r = requests.get(config['myurl'], verify=config['ssl_certificate'])
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)

    with open(config['tmp_file'], 'w') as f:
        f.write(r.text)

    dom = parse(config['tmp_file'])
    result = dom.getElementsByTagName('result')[0]

    # print result.firstChild.toxml()
    with open(config['backup_file'], 'wb') as f:
        result.firstChild.writexml(f)


if __name__ == "__main__":
    pan_conf = './pan.conf'
    try:
        config = parse_config(pan_conf)
    except IOError as e:
        print e
        sys.exit(1)
    pan_backup(config)
    sys.exit(0)
