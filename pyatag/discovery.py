"""Automatic discovery of ATAG Thermostat on LAN."""
import asyncio
ATAG_UDP_PORT = 11000
LOCALHOST = '0.0.0.0'

class Discovery(asyncio.DatagramProtocol):
    """Discovery class."""
    def __init__(self):
        self.data = asyncio.Future()
    def connection_made(self, transport):
        print("connected")
    def datagram_received(self, data, addr):
        self.data.set_result([data, addr])


async def discover_atag():
    """Discover Atag on local network."""
    # return format: [b'ONE xxxx-xxxx-xxxx_xx-xx-xxx-xxx (ST)', ('xxx.xxx.x.x', xxxx)]
    trans, proto = await asyncio.get_event_loop().create_datagram_endpoint(
        Discovery,
        local_addr=(LOCALHOST, ATAG_UDP_PORT))
    result = await proto.data
    trans.close()
    host_ip = result[1][0]
    device_id = result[0].decode().split()[1]
    return host_ip, device_id

# To dry run / test
#asyncio.get_event_loop().run_until_complete(discover_atag())
