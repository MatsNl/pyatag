"""Helpers for the ATAG connection"""

from datetime import datetime, timezone, timedelta
from numbers import Number
import logging
import json
import re
import uuid

import asyncio
from aiohttp import client_exceptions
from .errors import RequestError, ResponseError
from .const import (
    REQUEST_INFO,
    SENSOR_VALUES,
    BOILER_STATUS,
    DEFAULT_TIMEOUT,
    DETAILS,
    REPORT,
    CONTROLS,
    HTTP_HEADER,
)

MAC = "mac"
HOSTNAME = "hostname"
MAIL = "mail"
URL = "url"
HOST = "host"
PORT = "port"
DEVICE = "device"

RETRIEVE_REPLY = "retrieve_reply"

LOCALTZ = datetime.now().astimezone().tzinfo
_LOGGER = logging.getLogger(__name__)


def get_data_from_jsonreply(json_response):
    """Return relevant sensor data from json retrieve reply."""
    result = {}
    try:
        _reply = json_response[RETRIEVE_REPLY]
        _reply[DETAILS] = _reply[REPORT].pop(DETAILS)
        for group in _reply.keys():
            if group in ["seqnr", "acc_status"]:
                continue
            for key in _reply[group]:
                if key in SENSOR_VALUES:
                    worker = int(_reply[group][key])
                    result[key] = get_state_from_worker(key, worker)
                else:
                    res = _reply[group][key]
                    if isinstance(res, Number):
                        result[key] = {'state': float(res)}
                    else:
                        result[key] = {'state': res}
    except KeyError as err:
        raise ResponseError("Invalid value {} for {}".format(err, group))
    return result


def check_reply(json_reply):
    """reutrn the account status in an atag reply."""
    return json_reply[list(json_reply.keys())[0]]["acc_status"]


def get_state_from_worker(key, worker):
    """
    Returns:\n
    Sensor values when decoded (int based).\n
    Binary representation when not decoded.\n
    Time based on seconds from 2000 (UTC).
    """
    if key == BOILER_STATUS:
        return {'state': list(map(int, list("{0:04b}".format(worker & 14))))[0:3]}  
    if SENSOR_VALUES[key] == "time":
        return {'state': (
            datetime(2000, 1, 1, tzinfo=timezone.utc) +
            timedelta(seconds=worker)
        ).astimezone(tz=LOCALTZ)}
    if SENSOR_VALUES[key] == "int":
        # TODO not yet decoded integer values
        return {'state_orig': worker, 'state': int_to_binary(worker)}
    if worker in SENSOR_VALUES[key]:
        return SENSOR_VALUES[key][worker]
    return {'state': worker}  # not yet figured out what it means


def int_to_binary(worker):
    """Returns binary representation of int (for certain status/config values)."""
    return "{0:b}".format(worker)


class HttpConnector:
    """HTTP connector to ATAG thermostat."""

    def __init__(self, hostconfig, session=None):
        """Init of HTTP connector."""
        self.hostconfig = hostconfig
        self._websession = session
        self._request_timeout = DEFAULT_TIMEOUT

    async def atag_put(self, data):
        """Make a put request to the API."""
        path = list(data)[0].split("_")[0]
        posturl = "{}{}".format(self.hostconfig.baseurl, path)
        _LOGGER.debug("Posting to %s", posturl)
        try:
            async with self._websession.put(
                posturl,
                json=data,
                headers=self.hostconfig.http_header,
                proxy=self.hostconfig.proxy,
                # ssl=self.hostconfig.ssl,
                timeout=self._request_timeout,
            ) as req:
                data = await req.text()
                _LOGGER.debug("Received: %s", data)
                json_result = json.loads(data)
                return json_result
        except (
            client_exceptions.ClientError,
            ConnectionResetError,
            json.JSONDecodeError,
            client_exceptions.ClientConnectorError,
            asyncio.TimeoutError,
        ) as err:
            raise ResponseError(err)

    def set_timeout(self, timeout=DEFAULT_TIMEOUT):
        """Set timeout for API calls."""
        self._request_timeout = timeout

    async def async_close(self):
        """Close the connection"""
        await self._websession.close()


class HostConfig:
    """Connection info store."""

    def __init__(
        self,
        host=None,
        port=10000,
        mail=None,
        hostname="HomeAssistant",
        ssl=None,
        proxy=None,
    ):

        self.host = host
        self.port = port or 10000
        self.mail = mail or ""
        self.proxy = proxy
        self._mac = ":".join(re.findall("..", "%012x" % uuid.getnode()))
        self._ssl = ssl
        self.http_header = HTTP_HEADER
        self.hostname = hostname
        self.set_pair_msg()
        self.retrieve_msg = self.get_retrieve_msg()
        if self.host:
            self.update_params()
        # self.http_header['Authorization'] = host_config.get('auth')

    def update_params(self, host=None):
        """Set or update the values that depend on host address"""
        if host:
            self.host = host
        self.baseurl = "{}:{}/".format(self.host, self.port)
        if not re.match(r"^https?:\/\/", self.baseurl):
            prefix = "https://" if self._ssl else "http://"
            self.baseurl = prefix + self.baseurl

    def get_retrieve_msg(self, info=REQUEST_INFO):
        """Get and store the constant retrieve payload."""

        json_payload = {
            "retrieve_message": {
                "seqnr": 1,
                "account_auth": {"user_account": self.mail, "mac_address": self._mac},
                "info": info,
            }
        }
        return json_payload

    def set_pair_msg(self, hass=True):
        """Get and store the constant pairing payload."""

        msg = {
            "pair_message": {
                "seqnr": 1,
                "account_auth": {"user_account": self.mail, "mac_address": self._mac},
                "accounts": {
                    "entries": [
                        {
                            "user_account": self.mail,
                            "mac_address": self._mac,
                            "device_name": self.hostname,
                            "account_type": 1,
                        }
                    ]
                },
            }
        }
        self.pair_msg = msg

    def get_update_msg(self, **kwargs):
        """Return the update payload for control input."""
        for key, val in kwargs.items():
            if not key in CONTROLS or not isinstance(val, Number):
                raise RequestError("Invalid value for {}: {}".format(key, val))

        json_payload = {
            "update_message": {
                "seqnr": 1,
                "account_auth": {"user_account": self.mail, "mac_address": self._mac},
                "control": {},
            }
        }

        for key, val in kwargs.items():
            json_payload["update_message"]["control"][CONTROLS[key]] = val

        return json_payload
