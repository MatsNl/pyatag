"""Gateway connecting to ATAG thermostat."""
import asyncio
import logging
import re
import uuid
from datetime import datetime, timedelta

import aiohttp
from pyatag import errors

from .entities import DHW, Climate, Report

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
        if self._authorized:
            _LOGGER.debug("Not checking auth status as ID was provided")
            return True
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

        except errors.Unauthorized as err:
            _LOGGER.debug("Received unauthorized message, try with email address")
            raise err
        except errors.AtagException as err:
            _LOGGER.debug("Authorization failed: %s", type(err))
            raise err
        self._authorized = True
        _LOGGER.debug("Authorized successfully")
        return True

    async def request(self, meth, path, json=None, force=False):
        """Make a request to the API."""
        url = f"http://{self.host}:{self.port}/{path}"
        async with self._lock:
            slept = (datetime.utcnow() - self._last_call).total_seconds()
            if slept < 3 and not force:
                _LOGGER.debug("Sleeping for %ss", 3 - slept)
                await asyncio.sleep(3 - slept)
            self._last_call = datetime.utcnow()
            for tries in range(4):
                try:
                    _LOGGER.debug("Calling %s for %s", self.host, path)
                    async with self.session.post(url, json=json) as res:
                        data = await res.json()
                        _raise_on_error(data)
                        return data
                except aiohttp.ServerDisconnectedError as err:
                    if tries == 3:
                        _LOGGER.debug(
                            "Server disconnected unexpectedly 3 times, giving up"
                        )
                        errors.raise_error(err, 2)
                    _LOGGER.debug("Server disconnected unexpectedl: %s", tries)
                except aiohttp.ClientConnectionError as err:
                    _LOGGER.debug("Failed to connect to %s", self.host)
                    errors.raise_error(err, 2)
                except aiohttp.ClientResponseError as err:
                    _LOGGER.debug("Caught response error: %s", err)
                    errors.raise_error(err, 3)
                except aiohttp.InvalidURL as err:
                    _LOGGER.debug("Could not connect, url %s is incorrect", url)
                    errors.raise_error(err, 2)
                except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                    _LOGGER.debug("Unknown error occurred")
                    errors.raise_error(err, 5)

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
            res = await self.request("post", "retrieve", json, force)
        except errors.AtagException as err:
            _LOGGER.debug("Update failed: %s", err)
            raise err
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
        except errors.Unauthorized:
            raise errors.Unauthorized(
                "Failed to set Atag, received unauthorized message"
            )
        except errors.RequestError:
            raise errors.RequestError("Failed to set Atag, could not complete request")
        except errors.AtagException:
            raise errors.UnknownAtagError("Failed to set Atag, unknown error occurred")
        return res["update_reply"]


def _raise_on_error(data):
    """Check response for error message."""
    if data[list(data.keys())[0]]["acc_status"] != 2:
        errors.raise_error(data, 1)

    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        errors.raise_error(data)
