"""Gateway connecting to ATAG thermostat."""
from .const import *
from .helpers import *
from .errors import RequestError, ResponseError

import json
import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class atagDataStore:

    def __init__(
            self, host, port, scan_interval, session, sensors):
        if type(session).__name__ == 'ClientSession':
            self._connector = HttpConnector(host, port, session)
        else:
            _LOGGER.error("Not a valid session: %s", type(session).__name__ )

        self.scan_interval = scan_interval
        self._host_data = get_host_data()
        self.retrieve_msg = set_retrieve_msg(self._host_data)
        self.data = {}
        self.sensors = sensors
        self.sensordata = {}
        self.report_time = None
        self._paired = False

    async def async_update(self):
        """Read data from thermostat."""
        try:
            self.data = await self._connector.atag_put(data=self.retrieve_msg, path=RETRIEVE_PATH)
            #_LOGGER.debug("Retrieve reply: %s", self.data)
            self.sensordata = self.get_storable_data()
            _LOGGER.debug("Atag sensordata updated:\n %s", self.sensordata)
        except json.JSONDecodeError as err:
            raise ResponseError("Unable to decode Json response : {}".
                                format(err))

    async def async_set_atag(self, _target_mode=None, _target_temp=None):
        jsonPayload = get_update_msg(self._host_data, _target_mode, _target_temp)
        _LOGGER.debug("Updating Mode: [%s], Temp:[%s]", _target_mode, _target_temp)
        try:
            json_data = await self._connector.atag_put(data=jsonPayload, path=UPDATE_PATH)
            _LOGGER.debug("Update reply: %s", json_data)
            return json_data[UPDATE_REPLY][ACC_STATUS] == 2
        except json.JSONDecodeError as err:
            raise ResponseError("Unable to decode Json response : {}".
                                format(err))

    def get_storable_data(self):
        result = {}
        try:
            status = self.data[RETRIEVE_REPLY][REPORT]
            for sensor in self.sensors:
                datafield = SENSOR_TYPES[sensor][3]
                if sensor == BOILER_STATUS:
                    s = int(status[sensor])
                    result[sensor] = BOILER_STATES[s & 14]
                elif DETAILS in status and datafield in status[DETAILS]:
                    result[sensor] = float(status[DETAILS][datafield])
                elif datafield in status:
                    result[sensor] = float(status[datafield])
                else:
                    _LOGGER.error('Atag sensor %s type error: %s', sensor, datafield)
                    return False
        except:
            _LOGGER.warn('Atag sensor failed to update: %s', self.data)
            return False
        operation_mode_int = self.data[RETRIEVE_REPLY][CONTROL][ATTR_OPERATION_MODE_INT]
        result[ATTR_OPERATION_MODE] = INT_MODES[operation_mode_int]
        result[ATTR_REPORT_TIME] = get_time_from_stamp(status[ATTR_REPORT_TIME])
        return result

    async def async_check_pair_status(self):
        if self._paired:
            return True

        jsonPayload = get_pair_msg(self._host_data)
        try:
            json_data = await self._connector.atag_put(data=jsonPayload, path=PAIR_PATH)
            status = json_data[PAIR_REPLY][ACC_STATUS]
        except:
            _LOGGER.error("Pairing failed")
            return False
        if status == 2:
            self._paired = True
            _LOGGER.debug("AtagDataStore paired")
            return self._paired
        elif status == 1:
            print("Waiting for pairing confirmation")
        elif status == 3:
            print("Waiting for pairing confirmation")
        elif status == 0:
            print("No status returned from ATAG One")
        _LOGGER.warning("Atag not paired!\n%s", json_data)
        self._paired = False
        return self._paired