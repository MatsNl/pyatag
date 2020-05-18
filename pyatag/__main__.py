"""Example program to test pyatag."""
import asyncio

from pyatag import AtagOne
import aiohttp
import logging

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
    atag = AtagOne("localhost", session, email=None)
    await atag.authorize()
    await atag.update(force=True)

    for s in atag.report:
        _LOGGER.debug(f"{s.name} = {s.state}")

    for a in dir(atag.climate):
        _LOGGER.debug("atag.climate.%s = %r" % (a, getattr(atag.climate, a)))

    await atag.climate.set_preset_mode("manual")
    await atag.climate.set_temp(11)

    _LOGGER.debug(atag.report.report_time)
    _LOGGER.debug(atag.dhw.temperature)


asyncio.run(main())
