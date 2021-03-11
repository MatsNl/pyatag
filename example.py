"""Example program to test pyatag."""
import asyncio
import logging

import aiohttp

from pyatag import AtagException, AtagOne
from pyatag.discovery import async_discover_atag

logging.basicConfig()
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def main():
    """Initialize session for main program."""
    async with aiohttp.ClientSession() as session:
        await run(session)


async def run(session):
    """Run example main program."""
    atag_ip, device_id = await async_discover_atag()
    _LOGGER.info(f"Found Atag device {device_id }at address {atag_ip}")
    atag = AtagOne(atag_ip, session)
    try:
        await atag.authorize()
        await atag.update()
    except AtagException as err:
        _LOGGER.error(err)
        return False

    for sensor in atag.report:
        _LOGGER.debug("%s = %s", sensor.name, sensor.state)

    for attribute in dir(atag.climate):
        _LOGGER.debug(
            "atag.climate.%s = %s", attribute, getattr(atag.climate, attribute)
        )

    await atag.climate.set_preset_mode("manual")
    await atag.climate.set_temp(21)

    _LOGGER.debug(atag.report.report_time)
    _LOGGER.debug(atag.dhw.temperature)


asyncio.run(main())
