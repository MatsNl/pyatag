"""First test for gateway functioning"""
import asyncio
import aiohttp
from pyatag.gateway import AtagDataStore
from pyatag.input import TESTDATA


async def test():
    """Test connection with imported TESTDATA dict"""
    async with aiohttp.ClientSession() as session:
        atag = AtagDataStore(host=TESTDATA["_host"],
                             port=TESTDATA["_port"],
                             mail=TESTDATA["_mail"],
                             interface=TESTDATA["_interface"],
                             session=session,
                             sensors=TESTDATA["_sensors"])
        await atag.async_check_pair_status()
        # await atag.async_update()
        print(await atag.async_set_atag(_target_mode="manual", _target_temp=13))
        return atag

asyncio.get_event_loop().run_until_complete(test())
