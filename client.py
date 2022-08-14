import ipaddress
import logging
import shlex
import socket
import subprocess
import sys
import threading
import time
from ipaddress import IPv4Network
from typing import List, Dict

import requests
from requests import get, ConnectTimeout

IPv4_CIDR = 24  # should work on pretty much all nets
LOGGER = logging.getLogger('netAutoFS-Client')
logging.basicConfig(level=logging.INFO)
LOGGER.setLevel(logging.INFO)
DEFAULT_PROTOCOL_PORT = 7007  # ENSURE THIS MATCHES! (see server.py)


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
    NIX_COUNT = '-c {} -w 1'
    LOGGER.info('Generating list of IPs to ping...')

    hosts = [str(i) for i in net.hosts()]
    LOGGER.info(f'{len(hosts)} IPs. (sample: {hosts[:4]}...)')

    alive = []
    threads = []

    def ping(target: str):
        if 'linux' in sys.platform:
            cmd = f'ping {NIX_COUNT.format(1)} {target}'
        elif 'win' in sys.platform:
            cmd = f'ping {WIN_COUNT.format(1)} {target}'
        else:
            raise NotImplementedError(f'Platform {sys.platform} not supported. Sorry :(')
        LOGGER.debug(f'Pinging {target}...')
        try:
            out = subprocess.check_output(cmd, shell=True)
        except subprocess.CalledProcessError:
            return
        decoded = out.decode('utf-8')
        if 'Destination host unreachable' in decoded or 'Request timed out' in decoded or '100% packet loss' in decoded:
            return
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


# noinspection HttpUrlsUsage
def check_host_is_a_server(target: str) -> (bool, str):
    try:
        req = get(f'http://{target}:{DEFAULT_PROTOCOL_PORT}/exists', timeout=0.2)
        assert req.status_code == 200
        content = req.text
        assert content.startswith(f'netAutoFS-Server')
        return True, ' '.join(content.split(' ')[1:])
    except AssertionError:
        return False, ''
    except requests.ConnectionError:
        return False, ''


def check_for_servers(targets: List[str], thread_count: int = 32) -> Dict[str, str]:
    alive = {}
    threads = []

    def task(host: str):
        result, name = check_host_is_a_server(host)
        if result:
            LOGGER.info(f'{host} is a server ({name})')
            alive[host] = name

    def limit_threads(max_count: int, interval=0.1):
        while len(threads) > max_count:
            for thread in threads.copy():
                if not thread.is_alive():
                    threads.remove(thread)
            time.sleep(interval)

    for target in targets:
        limit_threads(thread_count)
        LOGGER.debug(f'Starting new thread for {target}...')
        t = threading.Thread(target=task, args=(target,))
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
    up_names_and_uas = check_for_servers(up_names)
    print(up_names_and_uas)


if __name__ == '__main__':
    main()
