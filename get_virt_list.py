#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
I need the guests on these kvm hosts. Print them to screen."
"""

from fabric import Connection, Config
from subprocess import check_output
from getpass import getpass
import argparse


def virt_list(host_start, host_end, site):
    """
    First we collect a sudo password. Next we ping the host to make sure it actually is alive. Not alive? Iterate to the
    next host. Alive? SSH to it and and print out the result of virsh list --all.
    :param host_start: server number to start at
    :param host_end: server number to end at
    :param site: physical site of servers, e.g. tym
    :return: None, print info to screen
    """
    sudo_pass = getpass("Env Password: ")
    config = Config(overrides={'sudo': {'password': sudo_pass}})
    for i in range(host_start, (host_end + 1)):
        ping = check_output(["ping", "-c 4", f"vm{i}.{site}.cudaops.com"])
        ping = ping.decode("utf-8")
        if "bn-scl-redirect.cuda-inc.com" in ping:
            continue
        else:
            conn = Connection(f"vm{i}.{site}.cudaops.com", config=config)
            virsh_all = str(conn.sudo("virsh list --all", hide="stdout"))
            print(f"vm{i}.{site}.cudaops.com\n{virsh_all}")
    return None


def create_parser():
    """
    Create the parser and arguments.
    :return: parser
    """

    parser = argparse.ArgumentParser(description="Log into specified kvm hosts and print the vm list.")

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
        virt_list(args.host_start, args.host_end, args.site)


if __name__ == '__main__':
    handle_args()
