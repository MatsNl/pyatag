"""Gateway connecting to ATAG thermostat."""
import logging
import datetime
import re, uuid
import asyncio
import logging
from errors import raise_error
from entities import Report, Climate, DHW

MINTIMEBETWEENCALLS = 5 

HANDLE = 'atag'
_LOGGER = logging.getLogger(HANDLE)
_LOGGER.setLevel(logging.DEBUG)

class AtagOne:
    """Central data store entity."""
    def __init__(self, host, session=None, *, atag_id=None,mail=None):
    
        self.host = host
        self.mail = mail
        if mail is None:
            _LOGGER.info('Running without Mail may lead to authorization issues.')
        self.session = session or ClientSession()
        self._atag_id = atag_id
        self._authorized = atag_id is not None
        self._mac = ":".join(re.findall("..", "%012x" % uuid.getnode()))
        self._last_call = datetime.datetime(1970,1,1)
        self._lock = asyncio.Lock()
        
        self.climate = None
        self.dhw = None
        self.report = None

    @property
    def id(self):
        """Return the ID of the bridge."""
        if self.report:
            return self.report['device_id'].state
        return self._atag_id

    async def authorize(self):
        """Check auth status."""
        json = {
            "pair_message": {
                "seqnr": 1,
                "account_auth": {"user_account": self.mail, "mac_address": self._mac},
                "accounts": {
                    "entries": [
                        {
                            "user_account": self.mail,
                            "mac_address": self._mac,
                            "device_name": "HomeAssistant",
                            "account_type": 1,
                        }
                    ]
                },
            }
        }
        await self.request("post", "pair", json)
        self.authorized = True
        _LOGGER.debug(f'Authorized: {self.authorized}')
        return self.authorized

    async def initialize(self):
        """Initialize the Atag object"""
        data = await self.update(force=True)
        self.report = Report(data, self.update, self.setter)
        self.climate = Climate(self.report)
        self.dhw = DHW(self.report)
        return True

    async def request(self, method, path, json=None):
        """Make a request to the API."""
        url = f"http://{self.host}:10000/{path}"
        async with self._lock:
            slept = (datetime.datetime.utcnow() - self._last_call).total_seconds()
            if slept < 5:
                await asyncio.sleep(5-slept)
            self._last_call = datetime.datetime.utcnow()
            async with self.session.request(method, url, json=json) as res:
                res.raise_for_status()
                data = await res.json()
                _raise_on_error(data)
                return data

    async def update(self, info=71, force=False):
        """Get latest data from API"""
        if (datetime.datetime.utcnow() - self._last_call ).total_seconds() > 15 or force:
            json = {
                "retrieve_message": {
                    "seqnr": 1,
                    "account_auth": {"user_account": self.mail, "mac_address": self._mac},
                    "info": info,
                }
            }
            res = await self.request('get','retrieve', json)
            res= res['retrieve_reply']
            res['report'].update(res['report'].pop('details') )
            return res
        return None

    async def setter(self, **kwargs):
        """Set control items."""
        json = {
            "update_message": {
                "seqnr": 1,
                "account_auth": {"user_account": self.mail, "mac_address": self._mac},
                "control": {},
                "configuration": {},
            }
        }

        for key, val in kwargs.items():
            json["update_message"]["control"][key] = val
            if key == "ch_mode" and val == 3:
                json["update_message"]["control"]["vacation_duration"] = int(
                    datetime.timedelta(days=1).total_seconds())
                json["update_message"]["configuration"]["start_vacation"] = int(
                    (datetime.datetime.utcnow() - datetime.datetime(2000, 1, 1)).total_seconds())
        res = await self.request('post','update', json)
        return res['update_reply']


def _raise_on_error(data):
    """Check response for error message."""
    if data[list(data.keys())[0]]["acc_status"] != 2:
        raise_error(data,1)

    if isinstance(data, list):
        data = data[0]

    if isinstance(data, dict) and "error" in data:
        raise_error(data)
