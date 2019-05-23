#-*- coding:utf-8 -*-
'''
Provides connection to ATAG One Thermostat REST API

#__version__ = '0.1.5'
__all__ = ["pyatag"]

from pytag.gateway import AtagDataStore
'''
import asyncio

async def test():
    """Test connection with imported TESTDATA dict"""
    from pyatag.gateway import AtagDataStore
    import aiohttp
    from .input import TESTDATA
    async with aiohttp.ClientSession() as session:
        atag = AtagDataStore(host=TESTDATA["_host"],
                             port=TESTDATA["_port"],
                             #mail=None, # test with mail == None
                             mail=TESTDATA["_mail"],
                             interface=TESTDATA["_interface"],
                             session=session,
                             sensors=TESTDATA["_sensors"])

        await atag.async_update()
        assert atag.paired
        print(atag.sensordata)
        #print(await atag.async_set_atag(_target_mode="manual", _target_temp=13))

        return atag.sensordata

asyncio.get_event_loop().run_until_complete(test())
