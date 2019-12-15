import asyncio
from pprint import pprint
import async_timeout
from pyatag.gateway import AtagDataStore
from pyatag import discovery
import logging
import aiohttp

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


async def main(target):
    async with aiohttp.ClientSession() as session:
        await target(session)

async def run_search_explicit(websession):

    with async_timeout.timeout(10):
        host, device = await discovery.discover_atag()
    if not host:
        return False
    atag = AtagDataStore(host=host, device=device)
    _LOGGER.info('Found device {} at {}'.format(device, host))

    await atag.async_update()

    for k, v in atag.sensordata.items():
        print('{}: {}'.format(k, v))

    await atag.async_close()


async def run_search_integrated(websession):

    atag = AtagDataStore()
    await atag.async_host_search()
    await atag.async_update()

    for k, v in atag.sensordata.items():
        print('{}: {}'.format(k, v))

    await atag.async_close()


async def run_search_integrated_paired(websession):

    atag = AtagDataStore(paired=True)
    await atag.async_host_search()
    await atag.async_update()

    for k, v in atag.sensordata.items():
        print('{}: {}'.format(k, v))

    await atag.async_close()

asyncio.get_event_loop().run_until_complete(main(run_search_integrated_paired))
