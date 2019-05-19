"""Helpers for the ATAG connection"""

from datetime import datetime, timezone, timedelta
from numbers import Number
import json

from aiohttp import client_exceptions
from .errors import AtagException, RequestError, ResponseError  # , Response404Error
from .const import (REQUEST_INFO, MODES, INT_MODES, HTTP_HEADER,
                          DEFAULT_TIMEOUT, DEFAULT_INTERFACE, DEFAULT_PORT)

MAC = 'mac'
HOSTNAME = 'hostname'
MAIL = 'email'
STATE_UNKNOWN = 'unknown'
URL = 'url'

def get_host_data(host=None, port=DEFAULT_PORT, interface=DEFAULT_INTERFACE, mail=None):
    """Store connection information in dict."""
    if host is None:
        raise AtagException("Invalid/None host data provided")
    import netifaces
    from socket import gethostname
    data = {
        URL: "http://{}:{}/".format(host, port),
        MAC: netifaces.ifaddresses(interface)[
            netifaces.AF_LINK][0]['addr'].upper(),
        HOSTNAME: gethostname(),
        MAIL: mail
    }
    return data


def get_int_from_mode(mode):
    """Convert the mode string to corresponding int."""
    return MODES[mode]


def get_mode_from_int(int_mode):
    """Convert the mode integer to corresponding string."""
    if int_mode in INT_MODES:
        return INT_MODES[int_mode]
    return STATE_UNKNOWN

def get_time_from_stamp(secs_after_2k):
    """Convert ATAG report time to datetime seconds after 2000 UTC."""
    return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=secs_after_2k)


class HttpConnector:
    """HTTP connector to Bosch thermostat."""

    def __init__(self, hostdata, websession):
        """Init of HTTP connector."""
        self.hostdata = hostdata
        self._websession = websession
        self._request_timeout = DEFAULT_TIMEOUT

    async def atag_put(self, data, path):
        """Make a put request to the API."""

        posturl = ''.join([str(self.hostdata.baseurl), str(path)])
        try:
            async with self._websession.put(
                    posturl,
                    json=data,
                    headers=HTTP_HEADER,
                    timeout=self._request_timeout) as req:
                data = await req.text()
                json_result = json.loads(data)
                return json_result
        except (client_exceptions.ClientError, client_exceptions.ClientConnectorError, TimeoutError) as err:
            raise ResponseError("Error putting data Atag: {}".format(err))
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

    def __init__(self, host=None, port=DEFAULT_PORT,
                 interface=DEFAULT_INTERFACE, mail=None):

        if host is None:
            raise RequestError("Invalid/None host data provided")
        print(interface)
        if interface is None:
            interface = DEFAULT_INTERFACE
        import netifaces
        import socket
        self.ataghost = host
        self.hostname = socket.gethostname()
        self.port = port
        self.baseurl = ''.join(['http://', str(host), ':', str(port), '/'])
        self.interface = interface
        self.email = mail
        self.mac = netifaces.ifaddresses(interface)[
            netifaces.AF_LINK][0]['addr'].upper()
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
        elif _target_mode is not None:
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
