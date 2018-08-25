#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Designed to add sumo logic lines to multiple csv files at once because anything else is too hard. Pass it the ip and
site. It does the rest.

Just 'ls >> /path/to/file/filename.txt' at the cli to make a list.
"""

import argparse


def add_sumo(ip, site):
    """
    Writes to existing csv files
    :param ip: IP Address of sumo box
    :param site: Physical site identifier
    :return: Nothing, just make the files as necessary
    """
    with open("/home/rob/Desktop/tym_file.txt", "r") as f:
        servers = f.readlines()
        servers = [i.strip("\n") for i in servers]

    for i in servers:
        with open(f"bbs_staging/extdata/fqdn/bbs.{site}.cudaops.com/{i}", "a") as f:
            f.write(f"\n# Sumo Logic config\n"
                    f"syslog_sumo_proto,tcp\n"
                    f"syslog_sumo_ip_address,{ip}\n"
                    f"syslog_sumo_ip_port,5140\n")
    return None


def create_parser():
    """
    Create the parser and arguments.
    :return: parser
    """

    parser = argparse.ArgumentParser(description="Quickly make yaml multiple files with the ip and optional "
                                                 "mysql/moebius entries.")

    parser.add_argument("-i", "--ip", dest='ip', help="SUMO IP", type=str, required=True)
    parser.add_argument("-s", "--site", dest="site", help="Site", type=str, required=True)

    return parser


def handle_args(args=None):
    """
    If args are not provided or all required not present, call create_parser and print help info.
    """

    if args is None:
        parser = create_parser()
        args = parser.parse_args()

    if args.ip and args.site:
        add_sumo(args.ip, args.site)


if __name__ == '__main__':
    handle_args()
