#!/usr/bin/env python3

__author__ = 'Gengwg'
__copyright__ = "Apache"
__version__ = '0.1.0'

"""
A Script to back up the Palo Alto Network firewall configs.
Run as a cronjob to back up the configs weekly.
"""

import argparse
import os
import sys
from xml.dom.minidom import parse

import requests


def load_config(conf):
    config = {}
    with open(conf, encoding='utf-8') as f:
        exec(compile(f.read(), conf, 'exec'), config)
    return config


def pan_backup(config):
    """Download the firewall config to config['backup_file']."""
    try:
        r = requests.get(
            config['myurl'],
            verify=config.get('ssl_certificate', True),
            timeout=config.get('timeout', 30),
        )
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    with open(config['tmp_file'], 'w', encoding='utf-8') as f:
        f.write(r.text)

    dom = parse(config['tmp_file'])
    results = dom.getElementsByTagName('result')
    if not results or results[0].firstChild is None:
        print("error: PAN response did not contain a config result", file=sys.stderr)
        return 1

    backup_file = config['backup_file']
    os.makedirs(os.path.dirname(backup_file) or '.', exist_ok=True)
    with open(backup_file, 'w', encoding='utf-8') as f:
        results[0].firstChild.writexml(f)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '-c', '--config',
        default='./pan.conf',
        help='config file to use (default: %(default)s)',
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return pan_backup(config)


if __name__ == "__main__":
    sys.exit(main())
