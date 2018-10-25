#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Collects user info and outputs info you can copypasta into a colo ticket.
"""

host_name = input("Hostname: ")
drive_enclosure = input("Enclosure: ")
drive_slot = input("Slot: ")
drive_size = input("Size: ")
rack = input("Rack: ")
rack_unit = input("RU:")
which_side = input("Front or Back (f/b): ").lower()
my_name = input("Name: ")

while i == True:
    if which_side == "front" or which_side == "f":
        print(f"\nHDD replacement on {host_name} [{drive_enclosure}:{drive_slot}]")
        print("\n\nHello,")
        print(f"\nPlease replace drive {drive_slot} on the {which_side} with an {drive_size}TB HDD from our stock. Label "
              f"the failed drive as bad and placed in our decom pile. There should be an LED indicator isolating the "
            f"failed drive.")
        print(f"\nHost: {host_name}")
        print(f"Rack: {rack}")
        print(f"RU: {rack_unit}")

        print("\nDrive Layout:")
        print("05  11  17  23")
        print("04  10  16  22")
        print("03  09  15  21")
        print("02  08  14  20")
        print("01  07  13  19")
        print("00  06  12  18")

        print("\nThanks,")
        print(f"{my_name}")
        i = False

    elif which_side == "back" or which_side == "b":
        print(f"\nHDD replacement on {host_name} [{drive_enclosure}:{drive_slot}]")
        print("\n\nHello,")
        print(f"\nPlease replace drive {drive_slot} on the {which_side} with an {drive_size}TB HDD from our stock. Label "
            f"the failed drive as bad and placed in our decom pile. There should be an LED indicator isolating the "
            f"failed drive.")
        print(f"\nHost: {host_name}")
        print(f"Rack: {rack}")
        print(f"RU: {rack_unit}")

        print("\nDrive Layout:")
        print("02  05  08  11")
        print("01  04  07  10")
        print("00  03  06  09")

        print("\nThanks,")
        print(f"{my_name}")
        i = False

    else:
        print("sorry I didn't get that...")