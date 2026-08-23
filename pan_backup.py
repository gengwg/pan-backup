#!/usr/bin/env python

__author__ = 'Gengwg'
__copyright__ = "Apache"
__version__ = '0.0.3'

"""
A Script to back up the Palo Alto Network firewall configs.
Run as a cronjob to back up the configs weekly.
"""

import requests
from xml.dom.minidom import parse
import sys


# helper function
def parse_config(conf):
    myconfig = {}
    execfile(conf, myconfig)
    return myconfig


def pan_backup(config=None):
    """Download PAN configs to local."""
    if config is None:
        config = {}

    try:
        r = requests.get(config['myurl'], verify=config['ssl_certificate'])
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)

    with open(config['tmp_file'], 'w') as f:
        f.write(r.text)

    dom = parse(config['tmp_file'])
    results = dom.getElementsByTagName('result')
    if not results or results[0].firstChild is None:
        print "PAN response did not contain a config result"
        sys.exit(1)

    with open(config['backup_file'], 'wb') as f:
        results[0].firstChild.writexml(f)


if __name__ == "__main__":
    pan_conf = './pan.conf'
    try:
        config = parse_config(pan_conf)
    except IOError as e:
        print e
        sys.exit(1)
    pan_backup(config)
    sys.exit(0)
