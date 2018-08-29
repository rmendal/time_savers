#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Made to quickly and remotely check for failed drives after stress runs on new server builds. Uses Fabric to ssh into the
servers you specify via flags and output any failed drives to the screen and associated hostname."
"""

from fabric import Connection, Config
from getpass import getpass
import argparse
from re import findall


def drv_chk(host_start, host_end, site):
    """
    Uses fabric to securely use a sudo password, ssh to each server specified with flags, run raiddisplay.py, use regex
    to find any failed drives and print out the hostname along with any failed drives.
    :param host_start: server number to start at
    :param host_end: server number to end at
    :param site: physical site of servers, e.g. tym
    :return: None, print info to screen
    """
    sudo_pass = getpass("Env Password: ")
    config = Config(overrides={'sudo': {'password': sudo_pass}})
    pattern = r"(\D\d+:\d+\D\s+\D\bFAIL\b\D)"
    for i in range(host_start, (host_end + 1)):
        conn = Connection(f"fs{i}.bbs.{site}.cudaops.com", config=config)
        rd = str(conn.sudo("raiddisplay.py", hide="stdout"))
        drv_list = findall(pattern, rd)
        drv_list = "\n".join(drv_list)
        print(f"fs{i}.bbs.{site}.cudaops.com\n{drv_list}")
    return None


def create_parser():
    """
    Create the parser and arguments.
    :return: parser
    """

    parser = argparse.ArgumentParser(description="Log into specified hosts, find any bad drives and return the host and"
                                                 " bad drive number.")

    parser.add_argument("-s", "--host-start", dest='host_start', help="Starting host number (e.g. 100)", type=int,
                        required=True)
    parser.add_argument("-e", "--host-end", dest='host_end', help="Ending host number (e.g. 103)", type=int,
                        required=True)
    parser.add_argument("-S", "--site", dest='site', help="Site Abbreviation (e.g. tym)", type=str, required=True)

    return parser


def handle_args(args=None):
    """
    If args are not provided or all required not present, call create_parser and print help info.
    """

    if args is None:
        parser = create_parser()
        args = parser.parse_args()

    if args.host_start and args.host_end and args.site:
        drv_chk(args.host_start, args.host_end, args.site)


if __name__ == '__main__':
    handle_args()
