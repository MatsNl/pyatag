"""Example program to test pyatag."""
import asyncio
import logging

import aiohttp
from pyatag import AtagOne

handle = "atag"
logging.basicConfig()
_LOGGER = logging.getLogger(handle)
_LOGGER.setLevel(logging.DEBUG)


async def main():
    """Initialize session for main program."""
    async with aiohttp.ClientSession() as session:
        await run(session)


async def run(session):
    """Run example main program."""
    atag = AtagOne("atag.local", session, email=None)
    await atag.authorize()
    await atag.update(force=True)

    for s in atag.report:
        _LOGGER.debug(f"{s.name} = {s.state}")

    for a in dir(atag.climate):
        _LOGGER.debug("atag.climate.{} = {!r}".format(a, getattr(atag.climate, a)))

    await atag.climate.set_preset_mode("manual")
    await atag.climate.set_temp(11)

    _LOGGER.debug(atag.report.report_time)
    _LOGGER.debug(atag.dhw.temperature)


asyncio.run(main())
