#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Made to quickly resize the /var/data
"""

from fabric import Connection, Config
from invoke import Responder
from subprocess import run
from getpass import getpass
import argparse


def resize(host_start, host_end, site):
    """
    Gathers sudo password, connects to host(s) and resizes the completely used 3TB of /dev/vg0/var_data. It then prints
    the final disk sizes and physical volume sizes to confirm the newly freed space.

    """
    # TODO: This kills the partitions, fix it
    sudo_pass = getpass("Env Password: ")
    config = Config(overrides={'sudo': {'password': sudo_pass}})
    confirm = Responder(pattern=r"Do you really want to reduce vg0/var_data? \[y\/n\]:", response="y\n")
    for i in range(int(host_start), (host_end + 1)):
        conn = Connection(f"vm{i}.bco.{site}.cudaops.com", config=config)
        conn.sudo("systemctl stop node_exporter.service")
        conn.sudo("mv /var/data/node_exporter /var/tmp/")
        conn.sudo("umount /var/data")
        conn.sudo("e2fsck -f /dev/vg0/var_data")
        conn.sudo("resize2fs /dev/vg0/var_data 100G")
        conn.sudo("lvreduce -L 100G /dev/vg0/var_data", pty=True, watchers=[confirm])
        conn.sudo("mount /var/data")
        conn.sudo("mv /var/tmp/node_exporter /var/data")
        conn.sudo("systemctl start node_exporter.service")
        print(run("df -h", shell=True), "\n", run("pvs", shell=True))

    return None


def create_parser():
    """
    Create the parser and arguments.
    :return: parser
    Add action="store_true" to parser arguments to allow empty flags.
    The below are examples and should be modified as necessary.
    """

    parser = argparse.ArgumentParser(description="This tool will resize the /var/data partition on a newly imaged civ2 "
                                                 "vm host.\n\n**WARNING!**\n\nIf this is not a newly imaged vm host you "
                                                 "risk data loss by running this script. You should move any data off "
                                                 "this partition and manually resize it.\n\nYOU'VE BEEN WARNED!")

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
        resize(args.host_start, args.host_end, args.site)


if __name__ == '__main__':
    handle_args()
