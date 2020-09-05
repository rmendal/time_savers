from fabric import task, Connection, Config
from subprocess import run, PIPE
from getpass import getpass
from tqdm import tqdm

@task
def virt_list(host_start, host_end, site):
    """
    First collect a sudo password. Next we dig with the +short flag and if we get an IP address back we continue with
    ping. If no IP back we skip to the next host. If we get an IP we ping the host to make sure it actually is alive.
    Not alive? Iterate to the next host. Alive? SSH to it and and print out the result of virsh list --all.
    Since this requires ping I've added a progress bar as it takes a bit to work through all of the hosts and otherwise
    looks stalled.
    :param host_start: server number to start at
    :param host_end: server number to end at
    :param site: physical site of servers, e.g. tym
    :return: None, print info to screen
    """
    sudo_pass = getpass("Env Password: ")
    config = Config(overrides={'sudo': {'password': sudo_pass}})
    for i in tqdm(range(int(host_start), (host_end + 1)), desc="Progress"):
        dig = str(run(f"dig +short vm{i}.product.{site}.domain.com", shell=True, stdout=PIPE))
        dig = ''.join(dig)
        if "stdout=b''" in dig:
            continue
        else:
            ping = str(run(f"ping -c 4 vm{i}.{site}.domain.com", shell=True, stdout=PIPE))
            ping = ''.join(ping)
            if "redirect.com" in ping or "100% packet loss" in ping:
                continue
            else:
                conn = Connection(f"vm{i}.{site}.domain.com", config=config)
                virsh_all = str(conn.sudo("virsh list --all", hide="stdout"))
                print(f"vm{i}.{site}.domain.com\n{virsh_all}")
    return None
