#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Made to quickly and remotely check for failed drives after stress runs on new server builds. Uses Fabric to ssh into the
servers you specify via flags
"""

import fabric
import argparse
from invoke import Responder



def create_parser():
    """
    Create the parser and arguments.
    :return: parser
    """

    parser = argparse.ArgumentParser(description="Quickly make yaml multiple files with the ip and optional "
                                                 "mysql/moebius entries.")

    parser.add_argument("-s", "--host-start", dest='host_start', help="Starting host number (e.g. 100)", type=int,
                        required=True)
    parser.add_argument("-e", "--host-end", dest='host_end', help="Ending host number (e.g. 103)", type=int,
                        required=True)
    parser.add_argument("-i", "--ip", dest='ip', help="Starting ip (e.g. 10.0.0.1)", type=str, required=True)
    parser.add_argument("-o", "--moebius", dest='moebius', help="Include a moebius entry", type=str,
                        required=False)
    parser.add_argument("-m", "--mysql", dest='mysql', help="Include mysql", type=str, required=False)
    parser.add_argument("-M", "--master", dest='master', help="Add the mysql master line", type=str,
                        required=False)
    return parser


def handle_args(args=None):
    """
    If args are not provided or all required not present, call create_parser and print help info.
    """

    if args is None:
        parser = create_parser()
        args = parser.parse_args()

    if args.host_start and args.host_end and args.ip:
        make_files(args.host_start, args.host_end, args.ip, args.moebius, args.mysql, args.master)


if __name__ == '__main__':
    handle_args()

