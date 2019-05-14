"""Gateway connecting to ATAG thermostat."""
import json
import logging
#import asyncio
import aiohttp

from .const import (DEFAULT_SENSOR_SET, RETRIEVE_PATH, UPDATE_PATH, PAIR_PATH, PAIR_REPLY,
                    UPDATE_REPLY, RETRIEVE_REPLY, DETAILS, ACC_STATUS, REPORT, SENSOR_TYPES,
                    BOILER_STATUS, BOILER_STATES, CONTROL, INT_MODES, ATTR_OPERATION_MODE,
                    ATTR_OPERATION_MODE_INT, ATTR_REPORT_TIME)
from .helpers import HostData, HttpConnector, get_time_from_stamp
from .errors import ResponseError

_LOGGER = logging.getLogger(__name__)


class AtagDataStore:
    """Central data store entity."""

    def __init__(
            self, session=None, host=None, port=None,
            mail=None, interface=None, sensors=None):

        self.host_data = HostData(
            host=host, port=port, interface=interface, mail=mail)
        if session is None:
            session = aiohttp.ClientSession()
        if type(session).__name__ == 'ClientSession':
            self._connector = HttpConnector(self.host_data, session)
        else:
            _LOGGER.error("Not a valid session: %s", type(session).__name__)

        self.data = {}
        if sensors is None:
            self.sensors = DEFAULT_SENSOR_SET
        else:
            self.sensors = sensors
        self.sensordata = {}
        self.paired = False

    async def async_update(self):
        """Read data from thermostat."""
        try:
            self.data = await self._connector.atag_put(
                data=self.host_data.retrieve_msg, path=RETRIEVE_PATH)
            # _LOGGER.debug("Retrieve reply: %s", self.data)
            self.sensordata = self.store_sensor_data()
            _LOGGER.debug("Atag sensordata updated:\n %s", self.sensordata)
        except json.JSONDecodeError as err:
            raise ResponseError("Unable to decode Json response : {}".
                                format(err))

    async def async_set_atag(self, _target_mode=None, _target_temp=None):
        """initiative mode and temperature setting."""
        json_payload = self.host_data.get_update_msg(
            _target_mode, _target_temp)
        _LOGGER.debug(
            "Updating: Mode:[%s], Temp:[%s]", _target_mode, _target_temp)
        try:
            json_data = await self._connector.atag_put(data=json_payload, path=UPDATE_PATH)
            _LOGGER.debug("Update reply: %s", json_data)
            return json_data[UPDATE_REPLY][ACC_STATUS] == 2
        except json.JSONDecodeError as err:
            raise ResponseError("Unable to decode Json response : {}".
                                format(err))

    def store_sensor_data(self):
        """Store relevant sensor data directly from json."""
        result = {}
        try:
            status = self.data[RETRIEVE_REPLY][REPORT]
            _LOGGER.debug("status: %s", status)
            for sensor in self.sensors:
                datafield = SENSOR_TYPES[sensor][3]
                if sensor == BOILER_STATUS:
                    worker = int(status[sensor])
                    result[sensor] = BOILER_STATES[worker & 14]
                elif DETAILS in status and datafield in status[DETAILS]:
                    result[sensor] = float(status[DETAILS][datafield])
                elif datafield in status:
                    result[sensor] = float(status[datafield])
                else:
                    _LOGGER.error('Atag sensor %s type error: %s',
                                  sensor, datafield)
                    return False
        except ResponseError:
            _LOGGER.error('Atag sensor failed to update: %s', self.data)
            return False
        operation_mode_int = self.data[RETRIEVE_REPLY][CONTROL][ATTR_OPERATION_MODE_INT]
        result[ATTR_OPERATION_MODE] = INT_MODES[operation_mode_int]
        result[ATTR_REPORT_TIME] = get_time_from_stamp(
            status[ATTR_REPORT_TIME])
        return result

    async def async_check_pair_status(self):
        """COnfirm we can access the ATAG thermostat."""
        if self.paired:
            return True
        try:
            json_data = await self._connector.atag_put(data=self.host_data.pair_msg, path=PAIR_PATH)
            status = json_data[PAIR_REPLY][ACC_STATUS]
            _LOGGER.debug("AtagDataStore pairing\n%s\n%s",
                          self.host_data.pair_msg, json_data)
        except ResponseError:
            _LOGGER.error("Pairing failed\n%s\n%s",
                          self.host_data.pair_msg, self.host_data.baseurl)
            return False
        if status == 2:
            self.paired = True
            _LOGGER.debug("AtagDataStore paired")
            return self.paired
        if status == 1:
            print("Waiting for pairing confirmation")
        elif status == 3:
            print("Waiting for pairing confirmation")
        elif status == 0:
            print("No status returned from ATAG One")
        _LOGGER.warning("Atag not paired!\n%s", json_data)
        self.paired = False
        return self.paired

    async def async_close(self):
        """Close the connection"""
        await self._connector.async_close()
