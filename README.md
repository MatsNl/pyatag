# PyAtag

## Asynchronous library to control Atag One

Requires Python 3.x and uses asyncio and aiohttp.

```python
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
    atag_ip, atag_id = await async_discover_atag() # for auto discovery, requires access to UDP broadcast (hostnet)
    # atag_ip = "atag.local"
    atag = AtagOne(atag_ip, session, email=None)
    try:
        await atag.authorize()
        await atag.update(force=True)
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
    await atag.climate.set_temp(11)

    _LOGGER.debug(atag.report.report_time)
    _LOGGER.debug(atag.dhw.temperature)


asyncio.run(main())
```
