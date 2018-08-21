#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Designed to create multiple base yaml files for server builds including ip addresses. Options include adding lines
for moebius and mysql
"""

from ipaddress import ip_address
import argparse
import subprocess


def make_files(host_start, host_end, ip, moebius, mysql, master):
    """
    Creates and writes to the yaml files
    :param host_start: Starting host number
    :param host_end: Ending host number
    :param ip: IP Address to begin with
    :param moebius: Include moebius line?
    :param mysql: Include mysql line?
    :param master: Include mysql master line?
    :return: Nothing, just make the files as necessary
    """
    file_list = []
    for i in range(host_start, (host_end + 1)):
        with open("fs{}.yaml".format(i), 'a') as f:
            f.write("---\n"
                    "profiles::network::interfaces:\n"
                    "  lan:\n"
                    "    ipaddress: {}\n".format(ip_address(ip)))
            if moebius is not None:
                f.write("\nprofiles::storage::moebius::moebius_version: 6.6.6-108")
            if mysql is not None:
                f.write("\nbbs::fileserver::enabledb_metadata_cluster: true")
            if master is not None:
                f.write("\nprofiles::mysql::master: true")
        ip = ip_address(ip) + 1
        file_list.append("fs{}.yaml".format(i))
    git(file_list)
    return None


def git(file_list):
    """
    Function receives the file list from above, adds them to git, commits them and pushes the commit.
    :param file_list: list of yaml files created in the above function.
    :return: None
    """
    message = input("Enter commit message: ")
    for i in file_list:
        subprocess.call(f"git add {i}", shell=True)

    subprocess.call(f"git commit -a -m '{message}'", shell=True)
    subprocess.call("git push", shell=True)
    subprocess.call("git request-pull -p", shell=True)
    return None


def create_parser():
    """Self explanatory no?"""

    parser = argparse.ArgumentParser(description="Quickly make yaml files with the ip and optional mysql/moebius"
                                                 " entries.")

    parser.add_argument("-s", "--host-start", dest='host_start', help="Starting host number (e.g. 100)", type=int,
                        required=True)
    parser.add_argument("-e", "--host-end", dest='host_end', help="Ending host number (e.g. 103)", type=int,
                        required=True)
    parser.add_argument("-i", "--ip", dest='ip', help="Starting ip", type=str, required=True)
    parser.add_argument("-m", "--moebius", dest='moebius', help="Include a moebius entry", type=str,
                        required=False)
    parser.add_argument("-q", "--mysql", dest='mysql', help="Include mysql.", type=str, required=False)
    parser.add_argument("-M", "--master", dest='master', help="Add the master line", type=str,
                        required=False)
    return parser


def handle_args(args=None):
    """Get host stats first then call the create_vm function and pass in the necessary args
       If args are not provided or all required not present, call create_parser and print help info."""
    if args is None:
        parser = create_parser()
        args = parser.parse_args()

    if args.host_start and args.host_end and args.ip:
        make_files(args.host_start, args.host_end, args.ip, args.moebius, args.mysql, args.master)


if __name__ == '__main__':
    handle_args()
