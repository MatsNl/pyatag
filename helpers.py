from datetime import datetime, timezone, timedelta
from aiohttp import client_exceptions
from asyncio import TimeoutError
from numbers import Number
import json

from .const import REQUEST_INFO, MODES, INT_MODES, HTTP_HEADER, DEFAULT_TIMEOUT
from .errors import RequestError, ResponseError, Response404Error

MAC = 'mac'
HOSTNAME = 'hostname'
HOST = ""
STATE_UNKNOWN = 'unknown'

def get_host_data(interface='eth0'):
    import netifaces, socket
    data = {
        MAC: netifaces.ifaddresses(interface)[
                netifaces.AF_LINK][0]['addr'].upper(),
        HOSTNAME: HOST,#socket.gethostname()
    }
    return data

def get_int_from_mode(mode):
    return MODES[mode]

def get_mode_from_int(int_mode):
    if int_mode in INT_MODES:
        return INT_MODES[int_mode]
    else:
        return STATE_UNKNOWN

def get_hostname():
    import socket
    return socket.gethostname()

def get_update_msg(_host_data={}, _target_mode=None, _target_temp=None):
    if _target_mode is None and _target_temp is None:
        raise RequestError("No update data received")
    elif _target_mode is not None and _target_temp is not None:
        raise RequestError("Cannot update mode and temperature simultaneously")
    elif _target_mode is not None:
        if _target_mode in MODES:
            _target_mode = get_int_from_mode(_target_mode)
        else:
            raise RequestError("Invalid update mode: %s", _target_mode)
    elif _target_temp is not None and not isinstance(_target_temp, Number):
        raise RequestError("Not a valid temperature: %s", _target_temp)
    
    jsonPayload = {
        'update_message': {
            'seqnr': 1,
            'account_auth': {
                'user_account': '',
                'mac_address': MAC #_host_data[MAC]
            },
            'device_id': HOST, #_host_data[HOSTNAME],
            'control': {
                'ch_mode': _target_mode,
                'ch_mode_temp': _target_temp
            }
        }
    }
    return(jsonPayload)

def set_retrieve_msg(_host_data={}):
    jsonPayload = {
        "retrieve_message": {
            "seqnr": 1,
            "account_auth": {
                "user_account": '',
                'mac_address': MAC#_host_data[MAC]
            },
            "device_id": HOST, #_host_data[HOSTNAME],
            "info": REQUEST_INFO
        }
    }
    #_LOGGER.debug(jsonPayload)
    return(jsonPayload)

def get_pair_msg(_host_data={}):
    jsonPayload = {
        "pair_message": {
            "seqnr": 1,
            "account_auth": {
                "user_account": '',
                'mac_address': MAC#_host_data[MAC]_host_data[MAC]
            },
            "accounts": {
                "entries": [
                    {
                        "user_account": '',
                        "mac_address": MAC, #_host_data[MAC],
                        "device_name": HOST,#_host_data[HOSTNAME],
                        "account_type": 1
                    }
                ]
            }
        }
    }
    return(jsonPayload)
    
def get_time_from_stamp(secs_after_2k):
    return datetime(2000, 1, 1, tzinfo=timezone.utc) + timedelta(seconds = secs_after_2k)

class HttpConnector:
    """HTTP connector to Bosch thermostat."""

    def __init__(self, host, port, websession):
        """Init of HTTP connector."""
        self._host = host
        self._port = port
        self._websession = websession
        self._request_timeout = DEFAULT_TIMEOUT

    async def atag_put(self, data, path):
        """Make a put request to the API."""
        try:
            async with self._websession.put(
                    self._format_url(path),
                    json=data,
                    headers=HTTP_HEADER,
                    timeout=self._request_timeout) as req:
                data = await req.text()
                json_result = json.loads(data)
                return json_result
        except (client_exceptions.ClientError, TimeoutError) as err:
            #_LOGGER.debug(err)
            raise RequestError(
                'Error putting data to {}{}, message: {}'.
                format(self._host, path, data) )
        except json.JSONDecodeError as jsonerr:
            raise ResponseError("Unable to decode Json response : {}".
                                format(jsonerr))

    def _format_url(self, path):
        """Format URL to make requests to gateway."""
        url = ''.join(['http://', str(self._host), ':', str(self._port), str(path)])

        return url

    def set_timeout(self, timeout=DEFAULT_TIMEOUT):
        """Set timeout for API calls."""
        self._request_timeout = timeout
