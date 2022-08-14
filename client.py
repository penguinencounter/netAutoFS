import ipaddress
import logging
import socket
from ipaddress import IPv6Network, IPv4Network
from typing import Union


IPv4_CIDR = 24  # should work on pretty much all nets
LOGGER = logging.getLogger('netAutoFSClient')
logging.basicConfig(level=logging.INFO)
LOGGER.setLevel(logging.DEBUG)


def get_local_ip() -> IPv4Network:
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
    return ipaddress.ip_network(IP + '/' + str(IPv4_CIDR), False)


def ping_spam(net: IPv4Network, count: int = 1) -> None:
    """
    Pings the network and prints the results.
    :param net: the network to ping.
    :param count: the number of pings to send.
    :return: None.
    """
    NT_COUNT = '-n {}'
    NIX_COUNT = '-c {}'
    LOGGER.info('Generating list of IPs to ping...')

    hosts = [str(i) for i in net.hosts()]
    LOGGER.info(f'{len(hosts)} IPs.')


if __name__ == '__main__':
    local = get_local_ip()
    ping_spam(local)
