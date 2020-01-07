"""Automatic discovery of ATAG Thermostat on LAN."""
import asyncio
from .helpers import RequestError

ATAG_UDP_PORT = 11000
LOCALHOST = "0.0.0.0"


class Discovery(asyncio.DatagramProtocol):
    """Discovery class."""

    def __init__(self):
        self.data = asyncio.Future()

    def connection_made(self, transport):
        print("Listening on UDP {}".format(ATAG_UDP_PORT))

    def datagram_received(self, data, addr):
        self.data.set_result([data, addr])


async def async_discover_atag():
    """Discover Atag on local network."""
    # return format: [b'ONE xxxx-xxxx-xxxx_xx-xx-xxx-xxx (ST)', ('xxx.xxx.x.x', xxxx)]
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
    # return format: [b'ONE xxxx-xxxx-xxxx_xx-xx-xxx-xxx (ST)', ('xxx.xxx.x.x', xxxx)]
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 11000))
    try:
        while True:
            result = sock.recvfrom(37)
            host_ip = result[1][0]
            device_id = result[0].decode().split()[1]
    except socket.timeout:
        pass
    except Exception as err:
        raise RequestError(err)
    return host_ip, device_id
