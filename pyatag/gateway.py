"""Gateway connecting to ATAG thermostat."""
import asyncio
import re
import socket  # together with your other imports
import uuid
from datetime import datetime, timedelta

import aiohttp

from . import __version__, errors
from .const import _LOGGER
from .entities import DHW, Climate, Report

USER_AGENT = "Mozilla/5.0 (compatible; AtagOneAPI/x; http://atag.one/)"
REQUEST_HEADER_USER_AGENT = "User-Agent"
REQUEST_HEADER_X_ONEAPP_VERSION = "X-OneApp-Version"
HEADERS = {
    REQUEST_HEADER_USER_AGENT: USER_AGENT,
    REQUEST_HEADER_X_ONEAPP_VERSION: f"{__package__}-{__version__}",
}


class AtagOne:
    """Central data store entity."""

    def __init__(self, host, session=None, device=None, email=None, port=10000):
        """Initialize main AtagOne object."""
        del email  # email is not needed for local connections
        self.host = host
        self.port = port
        self._device = device
        self._authorized = device is not None  # assume authorized if device id is known
        self._mac = "-".join(re.findall("..", "%012x" % uuid.getnode())).upper()
        self._last_call = datetime(1970, 1, 1)
        self._lock = asyncio.Lock()
        self._session = session or aiohttp.ClientSession()
        self.climate = None
        self.dhw = None
        self.report = None

    @property
    def id(self):
        """Return the ID of the bridge."""
        if self.report:
            self._device = self.report["device_id"].state
        return self._device

    @property
    def apiversion(self):
        """Return the ID of the bridge."""
        if self.report:
            return self.report["download_url"].state

    @property
    def authorized(self):
        """Return authorization status."""
        return self._authorized

    @authorized.setter
    def authorized(self, data):
        """Check response for error message."""
        self._authorized = data[list(data.keys())[0]]["acc_status"] == 2
        if not self._authorized:
            raise errors.Unauthorized("Received unauthorized message from device!")

    async def authorize(self):
        """Check auth status."""
        if not self.authorized:
            json = {
                "pair_message": {
                    "seqnr": 0,
                    "account_auth": {"user_account": "", "mac_address": self._mac},
                    "accounts": {
                        "entries": [
                            {
                                "user_account": "",  # self.email,
                                "mac_address": self._mac,
                                "device_name": socket.gethostname(),
                                "account_type": 0,
                            }
                        ]
                    },
                }
            }
            await self.request("pair", json)
            _LOGGER.debug("Authorized successfully.")
        return self.authorized

    async def request(self, path, json=None):
        """Make a request to the API."""
        url = f"http://{self.host}:{self.port}/{path}"
        async with self._lock:
            for tries in range(10):
                await asyncio.sleep(
                    1 - (datetime.utcnow() - self._last_call).total_seconds()
                )
                self._last_call = datetime.utcnow()
                _LOGGER.debug(f"Call {tries+1} to {self.host} for {path}")
                try:
                    async with self._session.post(
                        url, headers=HEADERS, json=json
                    ) as res:
                        self.authorized = data = await res.json()
                        return data
                except (
                    aiohttp.ServerDisconnectedError,
                    aiohttp.ClientError,
                    asyncio.CancelledError,
                ) as err:
                    if tries < 9 and isinstance(err, aiohttp.ServerDisconnectedError):
                        continue
                    raise errors.ConnectionError(
                        f"Giving up after {type(err).__name__} (attempts: {tries+1})"
                    ) from err

    async def update(self, info=71):
        """Get latest data from API."""
        if not self.authorized:
            await self.authorize()
        json = {
            "retrieve_message": {
                "seqnr": 0,
                "account_auth": {"user_account": "", "mac_address": self._mac},
                "info": info,
            }
        }
        res = await self.request("retrieve", json)
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
        if not self.authorized:
            await self.authorize()
        json = {
            "update_message": {
                "seqnr": 0,
                "account_auth": {"user_account": "", "mac_address": self._mac},
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
        res = await self.request("update", json)
        return res["update_reply"]
