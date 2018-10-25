#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Description: This cli tool will print out memory/cpu/disk stats then prompt the user to continue creating the vm or not
based on available resources. Variables required for virsh-install are gathered via flags passed when called.

This version supports python 2.7
"""

import argparse
import subprocess
import re
from sys import exit


def create_vm(name, ram, vcpus, brint, lv_boot, lv_data, lv_log):
    """Check for the existence of a volume group, network bridge, existing guest name and existing lv storage.
    Then create those disks, the guest, set the max cpus and ram and set the guest to autostart. The function returns
    some information on starting the guest, default password and connecting to it."""

    max_vcpus = (vcpus * 2)
    max_ram = (ram * 2)

    # vgdisplay then regex the volume group out and store in variable
    print("\nFinding existing volume group(s)...")
    vgd = subprocess.Popen("vgdisplay -s", stdout=subprocess.PIPE)
    vgd_out = vgd.stdout.read().decode("utf-8")
    pattern = r'"([A-Za-z0-9_\./\\-]*)"'
    get_vg = re.findall(pattern, vgd_out)
    vg = None

    if len(get_vg) > 1:
        print("Looks like we found more than one volume group...")
        print(', '.join(get_vg))
        n = 0
        while n < 1:
            vg = raw_input("Please enter the volume group you want to use: ")
            if vg in get_vg:
                n += 1
                continue
            else:
                print("\nSorry, I didn\'t get that...\n")
    else:
        vg = ''.join(get_vg)
        print("\nContinuing with {} volume group".format(''.join(vg)))

    # checks to make sure chosen bridge exists
    print("\nChecking if the bridge interface exists...")
    br_show = subprocess.Popen(["brctl", "show"], stdout=subprocess.PIPE)
    br_out = br_show.stdout.read().decode("utf-8")

    if brint in br_out:
        print("\n{} exists continuing...".format(brint))
    else:
        exit("\nSorry, that bridge interface doesn't exist and needs to be created before continuing.\n\nGoodbye...")

    # check vm name isn't already on the box
    print("\nChecking if the guest already exists...")
    name_show = subprocess.Popen(["virsh", "list", "--all"], stdout=subprocess.PIPE)
    name_out = name_show.stdout.read().decode("utf-8")

    if name not in name_out:
        print("\n{} not found in existing vms, continuing...".format(name))
    else:
        exit("\nThat guest already exists.\n\nGoodbye...")

    # Make sure the lv disks don't already exist
    print("\nChecking if storage already exists...")
    lvs_show = subprocess.Popen(["lvs"], stdout=subprocess.PIPE)
    lvs_out = lvs_show.stdout.read().decode("utf-8")

    if name in lvs_out or name+"-data" in lvs_out or name+"-log" in lvs_out:
        exit("\nExisting lv storage found.\n\nGoodbye...")
    else:
        print("\nNo storage found, continuing...")

    # create storage
    print("\nCreating storage for / ...")
    subprocess.call(["lvcreate", "-n", name, "-L", lv_boot, vg])

    print("Creating storage for /var/data... ")
    subprocess.call(["lvcreate", "-n", name+"-data", "-L", lv_data, vg])

    print("Creating storage for /var/log... ")
    subprocess.call(["lvcreate", "-n", name+"-log", "-L", lv_log, vg])

    print("\nStorage created...")

    # Create the guest
    print("\nCreating the guest...")
    subprocess.call("virt-install --autostart --connect qemu:///system --network bridge={} --graphics none "
                    "--name={} --ram={} --vcpus={},maxvcpus={} --os-type=linux --os-variant=rhel7 --cpu host "
                    "--location http://portage-dist.bitleap.net/centos/ "
                    "--extra-args 'ks=http://portage-dist.bitleap.net/kickstart/el7/virtual/cuda_kickstart.cfg "
                    "ip=dhcp console=tty0 console=ttyS0,115200n8' --noautoconsole "
                    "--disk /dev/{}/{},bus=virtio,sparse=false,cache=none,io=native "
                    "--disk /dev/{}/{}-data,bus=virtio,sparse=false,cache=none,io=native "
                    "--disk /dev/{}/{}-log,bus=virtio,sparse=false,cache=none,io=native".format(brint, name,
                                                                                                str(ram),
                                                                                                str(vcpus),
                                                                                                str(max_vcpus), vg,
                                                                                                name, vg, name, vg,
                                                                                                name), shell=True)
    print("\nGuest is being created. This can take a few minutes...")

    # set max memory to 2x asked for ram
    print("\nSetting max memory to {}MB".format(max_ram))

    subprocess.call("virsh setmaxmem {} {}M --config".format(name, str(max_ram)), shell=True)
    print("Max memory set...")

    # set vm to auto start
    print("\nSetting guest to autostart...")

    subprocess.call("virsh autostart {}".format(name), shell=True)

    print("""\nCreation of {} completed. Guest will finish installation and shut down. Once it's shut down you can
          start it up (virsh start {}) and connect to it (virsh console {}). Log in with root. The default root password
          is in Device42 under 'Kickstart Default Password': https://device42.cudaops.com/admin/rowmgmt/password/5419/
          """).format(name, name, name)

    return None


def get_stats():
    """This function gets the cpu/ram/disk stats of the vm host and prints them to the screen then the user decides to
    continue vm creation or exit based on the results, i.e. vm creation would over provision the host"""

    # Get memory stats, convert to GB and print them to the screen. kb to gb is (total kb / 1048576)
    mem = subprocess.Popen(["virsh", "nodememstats"], stdout=subprocess.PIPE)  # Gets mem stats and pipes it out
    mem_out = mem.stdout.read().decode("utf-8")  # reads the popen output and decodes it from binary to a regular string
    nums = [int(i) for i in mem_out.split() if i.isdigit()]  # Because screw regex but re.findall(r"\d+", output)
    total_gb = round((nums[0] / 1048576), 2)
    free_gb = round((nums[1] / 1048576), 2)
    print("Memory Usage\n------------\nTotal: {} GiB\nFree:  {} GiB".format(total_gb, free_gb))

    # Pulls CPU stats as percentages and prints it to the screen
    cpu = subprocess.Popen(["virsh", "nodecpustats", "--percent"], stdout=subprocess.PIPE)
    cpu_out = cpu.stdout.read().decode("utf-8")
    print("\nCPU Stats\n---------\n{}".format(cpu_out))

    # lsblk commands to show name, size, type and mountpoints. Mountpoints may be unnecessary
    print("Listing Block Devices\n---------------------")
    print(subprocess.call(["lsblk", "-o", "NAME,SIZE,TYPE,MOUNTPOINT"]))

    # Print disk usage with total. Ignoring this for now as I don't think it's necessary
    '''print("\nSystem Disk Space Usage\n-----------------------")
    dsk = subprocess.Popen(["df", "--total", "-h"], stdout=subprocess.PIPE)
    dsk_out = dsk.stdout.read().decode("utf-8")
    get_heading = re.findall(r"File.*", dsk_out)
    get_total = re.findall(r"total.*", dsk_out)
    print(''.join(get_heading))
    print(''.join(get_total),"\n")'''

    #  Have the user choose to continue or exit based on ram, cpu, disk use
    n = 0
    while n < 1:
        go_on = raw_input("Continue with VM creation? [y/n]: ").lower()

        if go_on == "y" or go_on == "yes":
            n += 1
            print("Good to go...")
            continue
        elif go_on == "n" or go_on == "no":
            exit("User exited...")
        else:
            print("\nSorry, I didn\'t get that...\n")


def create_parser():
    """Self explanatory no?"""

    parser = argparse.ArgumentParser(description='Create a CIV2 VM on a CIV2 VM Server. The "--lvboot" and "--lvlog" '
                                                 'flags are defaulted to 20GB and 50GB respectively. Change as needed. '
                                                 'All other flags are REQUIRED.')

    parser.add_argument("-n", "--name", dest='name', help="VM Name e.g. test123.bco.tym", type=str, required=True)
    parser.add_argument("-b", "--brint", dest='brint', help="Bridge int e.g. br404", type=str, required=True)
    parser.add_argument("-c", "--cpus", dest='vcpus', help="How many vcpus to assign", type=int, required=True)
    parser.add_argument("-r", "--ram", dest='ram', help="Ram amount in MB. Need 1GB per core for CentOS",
                        type=int, required=True)
    parser.add_argument("-B", "--lvboot", dest='lv_boot', help="LV_Boot Size e.g. 20G", type=str, default="20G",
                        required=False)
    parser.add_argument("-d", "--lvdata", dest='lv_data', help="LV_Data Size e.g. 50G", type=str, required=True)
    parser.add_argument("-l", "--lvlog", dest='lv_log', help="LV_Log Size e.g. 50G", type=str, default="50G",
                        required=False)
    return parser


def handle_args(args=None):
    """Get host stats first then call the create_vm function and pass in the necessary args
       If args are not provided or all required not present, call create_parser and print help info."""
    if args is None:
        parser = create_parser()
        args = parser.parse_args()

    if args is not None:
        get_stats()

    if args.name and args.brint and args.vcpus and args.ram and args.lv_boot and args.lv_data and args.lv_log:
        create_vm(args.name, args.ram, args.vcpus, args.brint, args.lv_boot, args.lv_data, args.lv_log)


if __name__ == '__main__':
    handle_args()
