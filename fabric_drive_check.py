#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Made to quickly and remotely check for failed drives after stress runs on new server builds. Uses Fabric to ssh into the
servers you specify via flags
"""

import fabric
import getpass
import argparse


def drv_chk(host_start, host_end, site):
    sudo_pass = getpass.getpass("Env password: ")
    config = fabric.Config(overrides={'sudo': {'password': sudo_pass}})

    for i in range (host_start, (host_end + 1)):
        conn = fabric.Connection(f"fs{i}.bbs.{site}.cudaops.com", config=config)
        print(f"fs{i}.bbs.{site}.cudaops.com")
        print(conn.sudo("raiddisplay.py", pty=True))

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

