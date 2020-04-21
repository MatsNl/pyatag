# -*- coding:utf-8 -*-
'''
Provides connection to ATAG One Thermostat REST API

#__version__ = '0.1.5'
__all__ = ["pyatag"]

from pytag.gateway import AtagDataStore
from pyatag.helpers import insert_in_db
'''
import asyncio
import json
# import pprint
import datetime

async def test():
    """Test connection with imported TESTDATA dict"""
    from pyatag.gateway import AtagDataStore
    import aiohttp
    from .input import TESTDATA #, SQLSERVER
    # pretty = pprint.PrettyPrinter(indent=2)
    async with aiohttp.ClientSession() as session:
        atag = AtagDataStore(host= TESTDATA["host"],
                             port=TESTDATA["port"],
                             # mail=None, # test with mail == None
                             mail=TESTDATA["mail"],
                             interface=None,  # TESTDATA["_interface"],
                             session=session)
        await atag.async_update()
        assert atag.paired
        print(json.dumps(atag.sensordata, default=str))
        # print(await atag.async_set_atag(dhw_mode_temp=44))
        # print("INSERT INTO atag VALUES({})".format(list(atag.sensordata.values())))
        # print(await atag.async_set_atag(_target_mode="manual", _target_temp=13))
        #await insert_in_db(atag.sensordata, SQLSERVER)
        print(f"hold mode: {atag.hold_mode}")
        await atag.set_hold_mode('auto')
        print(f"hold mode: {atag.hold_mode}")
        print(atag.hold_mode_duration)
        return atag

asyncio.get_event_loop().run_until_complete(test())
