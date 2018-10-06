#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Designed to create multiple base yaml files for server builds including ip addresses. Options include adding lines
for moebius and mysql
"""

from ipaddress import ip_address
import argparse
import subprocess


def make_files(host_start, host_end, ip, moebius, mysql, master, svr):
    """
    Creates and writes to the yaml files
    :param host_start: Starting host number
    :param host_end: Ending host number
    :param ip: IP Address to begin with
    :param moebius: Include moebius line?
    :param mysql: Include mysql line?
    :param master: Include mysql master line?
    :param svr: Server type (db, fs, etc)
    :return: Nothing, just make the files as necessary
    """
    file_list = []
    for i in range(int(host_start), (host_end + 1)):
        with open(f"{svr}{i}.yaml", 'a') as f:
            f.write("---\n"
                    "profiles::network::interfaces:\n"
                    "  lan:\n"
                    f"    ipaddress: {ip_address(ip)}\n")
            if moebius is True:
                f.write("\nprofiles::storage::moebius::moebius_version: 6.6.6-108")
            if mysql is True:
                f.write("\nbbs::fileserver::enabledb_metadata_cluster: true")
            if master is True:
                f.write("\nprofiles::mysql::master: true")
        ip = ip_address(ip) + 1
        file_list.append(f"fs{i}.yaml")
    git(file_list)
    return None


def git(file_list):
    """
    Function receives the file list from above, adds them to git and outputs a git status. Then asks user if all looks
     right.. If yes, it commits them and pushes. Else it quits.
    :param file_list: list of yaml files created in the above function.
    :return: None
    """
    n = 0
    message = input("Enter commit message: ")
    for i in file_list:
        subprocess.call(f"git add {i}", shell=True)
    subprocess.call("git status", shell=True)

    while n < 1:
        stat = input("Does the status look right? (y/n) ").lower()
        if stat == "y" or stat == "yes":
            subprocess.call(f"git commit -a -m '{message}'", shell=True)
            subprocess.call("git push", shell=True)
            n += 1
        elif stat == "n" or stat == "no":
            print("Exiting...")
            n += 1
        else:
            print("Sorry I didn't get that...")
    return None


def create_parser():
    """
    Create the parser and arguments.
    :return: parser
    """

    parser = argparse.ArgumentParser(description="Quickly make multiple yaml files with an ip and optional "
                                                 "mysql/mysql master/moebius entries.\nOnce created the app will then "
                                                 "perform a git add, commit, status and if ok'd by you, will push your "
                                                 "changes to the repo.")

    parser.add_argument("-s", "--start", dest="host_start", help="starting host number (e.g. 100)", type=str,
                        required=True)
    parser.add_argument("-e", "--end", dest="host_end", help="ending host number (e.g. 103)", type=int,
                        required=True)
    parser.add_argument("-t", "--svr", dest="svr", help="server type (i.e. fs, db, etc). Default is 'fs'", type=str,
                        required=False, default="fs")
    parser.add_argument("-i", "--ip", dest="ip", help="starting ip (e.g. 10.0.0.1)", type=str, required=True)
    parser.add_argument("-o", "--moebius", dest='moebius', help="include a moebius entry", action="store_true",
                        required=False)
    parser.add_argument("-m", "--mysql", dest="mysql", help="include mysql", action="store_true", required=False)
    parser.add_argument("-M", "--master", dest="master", help="add the mysql master line", action="store_true",
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
        make_files(args.host_start, args.host_end, args.ip, args.moebius, args.mysql, args.master, args.svr)


if __name__ == '__main__':
    handle_args()
