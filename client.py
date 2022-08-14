import ipaddress
import logging
import shlex
import socket
import subprocess
import sys
import threading
import time
from ipaddress import IPv4Network
from typing import List

IPv4_CIDR = 24  # should work on pretty much all nets
LOGGER = logging.getLogger('netAutoFSClient')
logging.basicConfig(level=logging.INFO)
LOGGER.setLevel(logging.INFO)


def get_local_ip() -> (str, IPv4Network):
    """
    Gets the local IP address of the machine.
    :return: the local IP address of the machine.
    """
    # CREDIT https://stackoverflow.com/a/28950776/18817037

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)

    # noinspection PyBroadException
    try:
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP, ipaddress.ip_network(IP + '/' + str(IPv4_CIDR), False)


def ping_spam(net: IPv4Network, thread_count: int = 32) -> List[str]:
    """
    Pings the network and prints the results.
    :param net: the network to ping.
    :param thread_count: the number of threads.
    :return: None.
    """
    WIN_COUNT = '-n {}'
    NIX_COUNT = '-c {}'
    LOGGER.info('Generating list of IPs to ping...')

    hosts = [str(i) for i in net.hosts()]
    LOGGER.info(f'{len(hosts)} IPs. (sample: {hosts[:4]}...)')

    alive = []
    threads = []

    def ping(target: str):
        if 'nix' in sys.platform:
            cmd = f'ping {NIX_COUNT.format(1)} {target}'
        elif 'win' in sys.platform:
            cmd = f'ping {WIN_COUNT.format(1)} {target}'
        else:
            raise NotImplementedError(f'Platform {sys.platform} not supported. Sorry :(')
        LOGGER.debug(f'Pinging {target}...')
        try:
            subprocess.check_output(shlex.split(cmd), shell=True)
        except subprocess.CalledProcessError:
            LOGGER.info(f'{target} is down.')
        else:
            LOGGER.info(f'{target} is up.')
            alive.append(target)

    def limit_threads(max_count: int, interval=0.1):
        while len(threads) > max_count:
            for thread in threads.copy():
                if not thread.is_alive():
                    threads.remove(thread)
            time.sleep(interval)

    for host in hosts:
        limit_threads(thread_count)
        LOGGER.debug(f'Starting new thread for {host}...')
        t = threading.Thread(target=ping, args=(host,))
        t.start()
        threads.append(t)
        LOGGER.debug(f'Thread started')
    LOGGER.info('Finishing up')
    limit_threads(0)
    LOGGER.info(f'Done, alive: {len(alive)}')
    return alive


def main():
    local, net = get_local_ip()
    print(f'i am {local}')
    up_names = ping_spam(net)

if __name__ == '__main__':
    main()
