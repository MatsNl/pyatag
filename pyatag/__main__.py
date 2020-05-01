import asyncio
from pprint import pprint

from gateway import AtagOne
import aiohttp
import logging

handle = 'atag'
logging.basicConfig()
_LOGGER = logging.getLogger(handle)
_LOGGER.setLevel(logging.DEBUG)

async def main():
    async with aiohttp.ClientSession() as session:
        await run(session)


async def run(session):
    
    atag = AtagOne('192.168.1.104', session,'mats.nelissen@gmail.com')
    # atag = AtagOne('atag.local', aiohttp.ClientSession(),mail='mats.nelissen@gmail.com')
    await atag.authorize()
    await atag.initialize()
    for s in atag.report:
        _LOGGER.debug(f"{s.name} = {s.state}" )

    for attr in dir(atag.climate):
        _LOGGER.debug("atag.climate.%s = %r" % (attr, getattr(atag.climate, attr)))
        
    await atag.climate.set_preset_mode('away')
    _LOGGER.debug(atag.report.report_time)
    _LOGGER.debug(atag.dhw.temperature)

    #await atag.climate.set_hvac_mode('heat')



    #     print('{}: {}'.format(light.name, 'on' if light.state['on'] else 'off'))

    # # Change state of a light.
    # await light.set_state(on=not light.state['on'])

    # print()
    # print('Groups:')
    # for id in bridge.groups:
    #     group = bridge.groups[id]
    #     print('{}: {}'.format(group.name, 'on' if group.action['on'] else 'off'))

    # # Change state of a group.
    # await group.set_action(on=not group.state['on'])


asyncio.run(main())
