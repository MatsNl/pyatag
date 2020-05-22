"""Gateway connecting to ATAG thermostat."""
import aiohttp
import logging
from datetime import datetime, timedelta
import re
import uuid
import asyncio
from .errors import raise_error, AtagException
from .entities import Report, Climate, DHW

_LOGGER = logging.getLogger(__name__)


class AtagOne:
    """Central data store entity."""

    def __init__(self, host, session, device=None, email=None, port=10000):
        """Initialize main AtagOne object."""
        self.host = host
        self.email = email or ""
        self.port = port
        if email is None:
            _LOGGER.debug("No email address provided.")
        self.session = session
        self._device = device
        self._authorized = device is not None
        self._mac = ":".join(re.findall("..", "%012x" % uuid.getnode()))
        self._last_call = datetime(1970, 1, 1)
        self._lock = asyncio.Lock()

        self.climate = None
        self.dhw = None
        self.report = None

    @property
    def id(self):
        """Return the ID of the bridge."""
        if self.report:
            return self.report["device_id"].state
        return self._device

    @property
    def apiversion(self):
        """Return the ID of the bridge."""
        if self.report:
            return self.report["download_url"].state

    async def authorize(self):
        """Check auth status."""
        json = {
            "pair_message": {
                "seqnr": 1,
                "account_auth": {"user_account": self.email, "mac_address": self._mac},
                "accounts": {
                    "entries": [
                        {
                            "user_account": self.email,
                            "mac_address": self._mac,
                            "device_name": "HomeAssistant",
                            "account_type": 1,
                        }
                    ]
                },
            }
        }
        try:
            await self.request("post", "pair", json)
        except AtagException as err:
            _LOGGER.error("Authorization failed: %s", err)
            return self._authorized
        self._authorized = True
        _LOGGER.debug("Authorized successfully")
        return self._authorized

    async def request(self, meth, path, json=None, force=False):
        """Make a request to the API."""
        url = f"http://{self.host}:{self.port}/{path}"
        async with self._lock:
            slept = (datetime.utcnow() - self._last_call).total_seconds()
            if slept < 3 and not force:
                _LOGGER.debug("Sleeping for %ss", 3 - slept)
                await asyncio.sleep(3 - slept)
            self._last_call = datetime.utcnow()
            try:
                _LOGGER.debug("Calling %s for %s", self.host, path)
                async with self.session.request(meth, url, json=json) as res:
                    data = await res.json()
                    _raise_on_error(data)
                    return data
            except aiohttp.ClientConnectorError as err:
                raise_error(err, 2)
            except Exception as err:
                _LOGGER.debug("Caught unexpected exception %s", err)
                raise_error(err, 5)

    async def update(self, info=71, force=False):
        """Get latest data from API."""
        json = {
            "retrieve_message": {
                "seqnr": 1,
                "account_auth": {"user_account": self.email, "mac_address": self._mac},
                "info": info,
            }
        }
        try:
            _LOGGER.debug("Queueing data update")
            res = await self.request("get", "retrieve", json, force)
        except AtagException as err:
            _LOGGER.warning("Update failed: %s", err)
            return False
        res = res["retrieve_reply"]
        res["report"].update(res["report"].pop("details"))
        if self.report is None:
            self.report = Report(res, self.update, self.setter)
            self.climate = Climate(self.report)
            self.dhw = DHW(self.report)
        else:
            self.report.update(res)
        return True

    async def setter(self, **kwargs):
        """Set control items."""
        json = {
            "update_message": {
                "seqnr": 1,
                "account_auth": {"user_account": self.email, "mac_address": self._mac},
                "control": {},
                "configuration": {},
            }
        }

        for key, val in kwargs.items():
            json["update_message"]["control"][key] = val
            if key == "ch_mode" and val == 3:
                json["update_message"]["control"]["vacation_duration"] = int(
                    timedelta(days=1).total_seconds()
                )
                json["update_message"]["configuration"]["start_vacation"] = int(
                    (datetime.utcnow() - datetime(2000, 1, 1)).total_seconds()
                )
        try:
            res = await self.request("post", "update", json)
        except AtagException as err:
            _LOGGER.warning("Failed to set Atag: %s", err)
            return False
        return res["update_reply"]


def _raise_on_error(data):
    """Check response for error message."""
    if data[list(data.keys())[0]]["acc_status"] != 2:
        raise_error(data, 1)

    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data)
