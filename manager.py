#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Made to quickly restart mysql_manager on multiple machines."
"""

from fabric import Connection, Config
from getpass import getpass


def manager_fix():
    """
    Uses fabric to securely use a sudo password, ssh to each server and restart mysql_manager.
    :return: None, print info to screen
    """
    sudo_pass = getpass("Env Password: ")
    config = Config(overrides={'sudo': {'password': sudo_pass}})
    with open("/home/rob/Desktop/list.txt", "r") as f:
        servers = f.readlines()
        servers = [i.strip("\n") for i in servers]

    for i in servers:
        conn = Connection(i, config=config)
        conn.sudo("service mysql_manager restart")
    return None


if __name__ == '__main__':
    manager_fix()
