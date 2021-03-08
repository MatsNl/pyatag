"""Automatic discovery of ATAG Thermostat on LAN."""
import asyncio
import socket

from .const import _LOGGER
from .errors import RequestError

ATAG_UDP_PORT = 11000
LOCALHOST = "0.0.0.0"


class Discovery(asyncio.DatagramProtocol):
    """Discovery class."""

    def __init__(self):
        """Start listener."""
        self.data = asyncio.Future()

    def connection_made(self, transport):
        """Log connection made."""
        _LOGGER.debug("Listening on UDP %s", ATAG_UDP_PORT)

    def datagram_received(self, data, addr):
        """Record broadcasted data."""
        self.data.set_result([data, addr])


async def async_discover_atag():
    """Discover Atag on local network."""
    # return format: [b'ONE xxxx-xxxx-xxxx_xx-xx-xxx-xxx (ST)',
    # ('xxx.xxx.x.x', xxxx)]
    trans, proto = await asyncio.get_event_loop().create_datagram_endpoint(
        Discovery, local_addr=(LOCALHOST, ATAG_UDP_PORT)
    )
    try:
        result = await asyncio.wait_for(proto.data, timeout=30)
        host_ip = result[1][0]
        device_id = result[0].decode().split()[1]
        trans.close()
    except asyncio.TimeoutError:
        trans.close()
        raise RequestError("Host discovery failed")
    return host_ip, device_id


def discover_atag():
    """Discover Atag on local network."""
    # return format: [b'ONE xxxx-xxxx-xxxx_xx-xx-xxx-xxx (ST)',
    # ('xxx.xxx.x.x', xxxx)]
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.settimeout(30)
    sock.bind(("", 11000))
    try:
        while True:
            result = sock.recvfrom(37)
            host_ip = result[1][0]
            device_id = result[0].decode().split()[1]
            return host_ip, device_id
    except socket.timeout:
        return False
    except Exception as err:
        raise RequestError(err)
