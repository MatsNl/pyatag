"""Helpers for the ATAG connection"""

from datetime import datetime, timezone, timedelta
from numbers import Number
import json

import asyncio
from aiohttp import client_exceptions
from .errors import RequestError, ResponseError
from .const import (REQUEST_INFO, SENSOR_VALUES, BOILER_STATUS,
                    DEFAULT_TIMEOUT, DETAILS, REPORT, CONTROLS,
                    HTTP_HEADER)

MAC = 'mac'
HOSTNAME = 'hostname'
MAIL = 'email'
URL = 'url'
HOST = 'host'
PORT = 'port'
INTERFACE = 'interface'
DEVICE = 'device'

MSG_TO_PATH = {
    'update_message': 'update',
    'retrieve_message': 'retrieve',
    'pair_message': 'pair'
}
RETRIEVE_REPLY = 'retrieve_reply'


def get_data_from_jsonreply(json_response):
    """Return relevant sensor data from json retrieve reply."""
    result = {}
    try:
        _reply = json_response[RETRIEVE_REPLY]
        _reply[DETAILS] = _reply[REPORT][DETAILS]
        for group in _reply.keys():
            if group in ['seqnr', 'acc_status']:
                continue
            for key in _reply[group]:
                if key == DETAILS:
                    break
                if key in SENSOR_VALUES:
                    worker = int(_reply[group][key])
                    result[key] = get_state_from_worker(key, worker)
                else:
                    res = _reply[group][key]
                    if isinstance(res, Number):
                        result[key] = float(res)
                    else:
                        result[key] = res
    except KeyError as err:
        raise ResponseError("Invalid value {} for {}".format(err, group))
    return result


def check_reply(json_reply):
    """reutrn the account status in an atag reply."""
    return json_reply[list(json_reply.keys())[0]]['acc_status']


def get_state_from_worker(key, worker):
    """
    Returns:\n
    Sensor values when decoded (int based).\n
    Binary representation when not decoded.\n
    Time based on seconds from 2000 (UTC).
    """
    if key == BOILER_STATUS:
        return SENSOR_VALUES[BOILER_STATUS][worker & 14]
    if SENSOR_VALUES[key] == 'time':
        return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=worker)
    if SENSOR_VALUES[key] == 'int':
        # not yet decoded integer values
        return [worker, int_to_binary(worker)]
    if worker in SENSOR_VALUES[key]:
        return SENSOR_VALUES[key][worker]
    return worker  # not yet figured out what it means


def int_to_binary(worker):
    """Returns binary representation of int (for certain status/config values)."""
    return '{0:b}'.format(worker)


class HttpConnector:
    """HTTP connector to ATAG thermostat."""

    def __init__(self, hostdata, websession):
        """Init of HTTP connector."""
        self.hostdata = hostdata
        self._websession = websession
        self._request_timeout = DEFAULT_TIMEOUT

    async def atag_put(self, data):
        """Make a put request to the API."""
        path = MSG_TO_PATH.get(list(data.keys())[0])
        posturl = '{}{}'.format(self.hostdata.baseurl, path)
        try:
            async with self._websession.put(
                    posturl,
                    json=data,
                    headers=HTTP_HEADER,
                    timeout=self._request_timeout) as req:
                data = await req.text()
                json_result = json.loads(data)
                return json_result
        except (client_exceptions.ClientError, ConnectionResetError,
                client_exceptions.ClientConnectorError, asyncio.TimeoutError) as err:
            raise ResponseError(err)
        except json.JSONDecodeError as err:
            raise ResponseError(
                "Unable to decode Json response: {}".format(err))

    def set_timeout(self, timeout=DEFAULT_TIMEOUT):
        """Set timeout for API calls."""
        self._request_timeout = timeout

    async def async_close(self):
        """Close the connection"""
        await self._websession.close()


class HostData:
    """Connection info store."""

    def __init__(self, host_config):
        host = host_config[HOST]
        port = host_config[PORT]
        interface = host_config[INTERFACE]
        mail = host_config[MAIL]
        if host is None:
            raise RequestError("Invalid/None host data provided")
        import netifaces
        import socket
        self.email = mail
        self.hostname = socket.gethostname()
        self.baseurl = "http://{}:{}/".format(host, port)
        if interface is None:
            interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        try:
            self.mac = netifaces.ifaddresses(interface)[
                netifaces.AF_LINK][0]['addr'].upper()
        except ValueError:
            raise RequestError("Incorrect interface selected")
        self.set_pair_msg()
        self.set_retrieve_msg()

    def set_retrieve_msg(self):
        """Get and store the constant retrieve payload."""

        json_payload = {
            "retrieve_message": {
                "seqnr": 1,
                "account_auth": {
                    'user_account': self.email,
                    'mac_address': self.mac
                },
                "info": REQUEST_INFO
            }
        }
        self.retrieve_msg = json_payload

    def set_pair_msg(self):
        """Get and store the constant pairing payload."""

        json_payload = {
            "pair_message": {
                "seqnr": 1,
                "account_auth": {
                    'user_account': self.email,
                    'mac_address': self.mac
                },
                "accounts": {
                    "entries": [
                        {
                            "user_account": self.email,
                            "mac_address": self.mac,
                            "device_name": self.hostname,
                            "account_type": 1
                        }
                    ]
                }
            }
        }
        self.pair_msg = json_payload

    def get_update_msg(self, **kwargs):
        """Return the update payload for control input."""
        for key, value in kwargs.items():
            if not key in CONTROLS or not isinstance(value, Number):
                raise RequestError(
                    "Invalid values received: {}: {}".format(key, value))

        json_payload = {
            'update_message': {
                'seqnr': 1,
                'account_auth': {
                    'user_account': self.email,
                    'mac_address': self.mac
                },
                'control': {
                }
            }
        }

        for key, value in kwargs.items():
            json_payload['update_message']['control'][CONTROLS.get(
                key)] = value

        return json_payload
