"""Helpers for the ATAG connection"""

from datetime import datetime, timezone, timedelta
from numbers import Number
import json

import asyncio
from aiohttp import client_exceptions
from .errors import RequestError, ResponseError
from .const import (REQUEST_INFO, MODES, INT_MODES, BOILER_STATES, BOILER_STATUS, BOILER_CONF,
                    DEFAULT_TIMEOUT, DEFAULT_INTERFACE, ATTR_OPERATION_MODE,
                    ATTR_REPORT_TIME, RETRIEVE_REPLY, DETAILS, REPORT, SENSOR_TYPES,
                    REPORT_STRUCTURE_INV, HTTP_HEADER, WEATHER_STATUS, WEATHER_STATES)

MAC = 'mac'
HOSTNAME = 'hostname'
MAIL = 'email'
URL = 'url'


def get_data_from_jsonreply(json_response):
    """Return relevant sensor data from json retrieve reply."""
    result = {}
    try:
        _reply = json_response[RETRIEVE_REPLY]
        _reply[DETAILS] = _reply[REPORT][DETAILS]
        for sensor in SENSOR_TYPES:
            datafield = SENSOR_TYPES[sensor][3]
            location = REPORT_STRUCTURE_INV[datafield]
            if sensor in [BOILER_STATUS, BOILER_CONF, ATTR_OPERATION_MODE,
                          ATTR_REPORT_TIME, WEATHER_STATUS]:
                worker = int(_reply[location][datafield])
                result[sensor] = get_state_from_worker(sensor, worker)
            else:
                result[sensor] = float(_reply[location][datafield])
    except KeyError as err:
        raise ResponseError(err)
    return result


def get_state_from_worker(sensor, worker):
    """
    Returns:\n
    Boiler status based on binary indicator.\n
    Operation mode and Weather status from Atag int.\n
    Report time based on seconds from 2000 (UTC).
    """
    if sensor == BOILER_STATUS:
        return BOILER_STATES[worker & 14]
    if sensor == ATTR_OPERATION_MODE:
        return INT_MODES[worker]
    if sensor == WEATHER_STATUS:
        return WEATHER_STATES[worker] # list incl status string and icon
    if sensor == BOILER_CONF:
        return [worker, int_to_binary(worker)]
    if sensor == ATTR_REPORT_TIME:
        return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=worker)
    return False


def int_to_binary(worker):
    """Returns binary representation of int (for certain status/config values)."""
    return '{0:b}'.format(worker)


class HttpConnector:
    """HTTP connector to Bosch thermostat."""

    def __init__(self, hostdata, websession):
        """Init of HTTP connector."""
        self.hostdata = hostdata
        self._websession = websession
        self._request_timeout = DEFAULT_TIMEOUT

    async def atag_put(self, data, path):
        """Make a put request to the API."""

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
        except (client_exceptions.ClientError,
                client_exceptions.ClientConnectorError, asyncio.TimeoutError) as err:
            raise ResponseError("Error putting data Atag: {}".format(err))
        except json.JSONDecodeError as err:
            raise ResponseError("Unable to decode Json response: {}".format(err))

    def set_timeout(self, timeout=DEFAULT_TIMEOUT):
        """Set timeout for API calls."""
        self._request_timeout = timeout

    async def async_close(self):
        """Close the connection"""
        await self._websession.close()


HOST = 'host'
PORT = 'port'
MAIL = 'mail'
INTERFACE = 'interface'
DEVICE = 'device'


class HostData:
    """Connection info store."""

    def __init__(self, host_config):
        host = host_config[HOST]
        port = host_config[PORT]
        interface = host_config[INTERFACE]
        mail = host_config[MAIL]
        if host is None:
            raise RequestError("Invalid/None host data provided")
        if interface is None:
            interface = DEFAULT_INTERFACE
        import netifaces
        import socket
        self.email = mail
        self.hostname = socket.gethostname()
        self.baseurl = "http://{}:{}/".format(host, port)
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

    def get_update_msg(self, _target_mode=None, _target_temp=None):
        """Get and return the update payload (mode and temp)."""

        _target_mode_int = None
        if _target_mode is None and _target_temp is None:
            raise RequestError("No update data received")
        if _target_mode is not None:
            if _target_mode in MODES:
                _target_mode_int = MODES[_target_mode]
            else:
                raise RequestError(
                    "Invalid update mode: {}".format(_target_mode))
        elif _target_temp is not None and not isinstance(_target_temp, Number):
            raise RequestError(
                "Not a valid temperature: {}".format(_target_temp))

        json_payload = {
            'update_message': {
                'seqnr': 1,
                'account_auth': {
                    'user_account': self.email,
                    'mac_address': self.mac
                },
                'control': {
                    'ch_mode': _target_mode_int,
                    'ch_mode_temp': _target_temp
                }
            }
        }
        return json_payload
