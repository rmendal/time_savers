#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Base framework for a task using fabric
"""


from fabric import Connection, Config
from subprocess import run, PIPE
from getpass import getpass
import argparse


def func():
    """
    Description

    """
    sudo_pass = getpass("Env Password: ")
    config = Config(overrides={'sudo': {'password': sudo_pass}})
    conn = Connection(f"vm{i}.{site}.domain.com", config=config)
    virsh_all = str(conn.sudo("virsh list --all", hide="stdout"))
    return None


def create_parser():
    """
    Create the parser and arguments.
    :return: parser
    Add action="store_true" to parser arguments to allow empty flags.
    The below are examples and should be modified as necessary.
    """

    parser = argparse.ArgumentParser(description="")

    parser.add_argument("-s", "--host-start", dest='host_start', help="Starting host number (e.g. 100)", type=str,
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
        your_func(args_to_pass)


if __name__ == '__main__':
    handle_args()
