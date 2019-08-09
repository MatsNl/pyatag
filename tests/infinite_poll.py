# -*- coding:utf-8 -*-
'''
Provides connection to ATAG One Thermostat REST API

#__version__ = '0.1.5'
__all__ = ["pyatag"]

from pytag.gateway import AtagDataStore
'''
import asyncio
from contextlib import suppress
# import pprint


async def test():
    """Test connection with imported TESTDATA dict"""
    from pyatag.gateway import AtagDataStore
    import aiohttp
    from .input import TESTDATA
    # pretty = pprint.PrettyPrinter(indent=2)
    async with aiohttp.ClientSession() as session:
        atag = AtagDataStore(host='192.168.1.3',  # TESTDATA["_host"],
                             port=TESTDATA["_port"],
                             # mail=None, # test with mail == None
                             mail=TESTDATA["_mail"],
                             interface=None,  # TESTDATA["_interface"],
                             session=session)

        while True:
            print("starting loop")
            await atag.async_update()
            print('updated')
            assert atag.paired
            print(atag.sensordata.get('date_time'))
            print(atag.session.closed)
            await asyncio.sleep(3)


async def main():
    """Start infinite polling loop"""
    task = asyncio.Task(test())
    await asyncio.sleep(300)
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task

try:
    LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(LOOP)
    LOOP.run_until_complete(main())
finally:
    LOOP.run_until_complete(LOOP.shutdown_asyncgens())
    LOOP.close()
