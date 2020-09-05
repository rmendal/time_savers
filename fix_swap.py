#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Use fabric to fix swap on 107x boxes until Platform sorts it out.
"""


from fabric import Connection, Config
from tqdm import tqdm
from getpass import getpass
import argparse


def fix_swap(host_type, host_start, host_end, site):
    """
    Description

    """
    sudo_pass = getpass("Env Password: ")
    config = Config(overrides={'sudo': {'password': sudo_pass}})
    for i in tqdm(range(int(host_start), (host_end + 1)), desc="Progress"):
        conn = Connection(f"{host_type}{i}.product.{site}.domain.com", config=config)
        mk_swp = str(conn.sudo("mkswap /dev/sda3", hide="stdout"))
        swp_on = str(conn.sudo("swapon /dev/sda3", hide="stdout"))
        print(mk_swp, "\n", swp_on)

    return None


def create_parser():
    """
    Create the parser and arguments.
    :return: parser
    Add action="store_true" to parser arguments to allow empty flags.
    The below are examples and should be modified as necessary.
    """

    parser = argparse.ArgumentParser(description="Enter host type, starting host, ending host, and site. Tool will log "
                                                 "into the servers and fix the swap issue.")

    parser.add_argument("-t", "--type", dest='host_type', help="Host type (e.g. vm, db, fs, etc...)", type=str,
                        required=True)
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

    if args.host_type and args.host_start and args.host_end and args.site:
        fix_swap(args.host_type, args.host_start, args.host_end, args.site)


if __name__ == '__main__':
    handle_args()
