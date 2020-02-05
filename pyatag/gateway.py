"""Gateway connecting to ATAG thermostat."""
import logging
import datetime
import asyncio
from aiohttp import ClientSession
from .helpers import HostConfig, HttpConnector, get_data_from_jsonreply, check_reply
from .errors import ResponseError, RequestError
from .const import BOILER_STATUS

_LOGGER = logging.getLogger(__name__)
MINTIMEBETWEENCALLS = 5  # Time in seconds


class AtagDataStore:
    """Central data store entity."""

    def __init__(
        self,
        session=None,
        host=None,
        port=10000,
        device=None,
        hostname="HomeAssistant",
        mail=None,
        auth=None,
        ssl=None,
        proxy=None,
        paired=False,
        **kwargs
    ):

        self._initialized = False
        self._device = device
        self._paired = paired
        self.connection = None
        self.sensordata = {}
        self._session = session
        mail = mail or kwargs.get("email")
        self.config = HostConfig(host, port, mail, hostname, ssl, proxy)
        self._last_api_call = (
            datetime.datetime(1970, 1, 1, 0, 0, 0).astimezone(),
            None,
        )
        self._target_temperature = None
        self._dhw_target_temperature = None
        self._hvac_mode = None
        if self.config.host:
            self.initialized = True

    @property
    def device(self):
        """Device identifier"""
        return self._device

    @property
    def apiversion(self):
        """Return api version reported by device"""
        return self.sensordata.get("download_url").get('state').split("/")[-1]

    @property
    def paired(self):
        """Pairing status"""
        return self._paired

    @property
    def initialized(self):
        """Initialization completed"""
        return self._initialized

    @initialized.setter
    def initialized(self, arg=None):
        if not self.config.host:
            raise RequestError("Attempted initialization without hostaddress")
        if self._session is None:
            self._session = ClientSession()
        self.connection = HttpConnector(self.config, self._session)
        self._initialized = True

    @property
    def burner_status(self):
        """Returns a tuple: boolean for burning and percentage for modulation"""
        if isinstance(self.sensordata.get(BOILER_STATUS).get('state'), list):
           if self.sensordata[BOILER_STATUS]['state'][0]==1:
                return (True, self.sensordata.get("rel_mod_level"))
        return (False, 0)

    @property
    def cv_status(self):
        """Return boolean indicator for heating for CV"""
        if self.burner_status:
            return self.sensordata[BOILER_STATUS]['state'][2] == 1

    @property
    def dhw_status(self):
        """Return boolean indicator for heating for DHW"""
        if self.burner_status:
            return self.sensordata[BOILER_STATUS]['state'][1] == 1

    @property
    def hvac_mode(self):
        """Return the mode ATAG is operating in:
        :param auto: Returned when ATAG is set to weather based.
        :param heat: Returned when set to regular mode.
        """
        if (
            self._last_api_call[1] == "ch_control_mode"
            and self.sensordata.get("report_time").get('state') < self._last_api_call[0]
        ):
            return self._hvac_mode
        return self.sensordata.get("ch_control_mode").get('state')

    async def set_hvac_mode(self, mode: str) -> bool:
        """Set the mode ATAG operates in:
        :param auto: Returned when ATAG is set to weather based.
        :param heat: Returned when set to regular mode.
        """
        if mode == self.hvac_mode:
            return True
        int_mode = 1 if mode == "auto" else 0
        try:
            if await self.async_set_atag(ch_control_mode=int_mode):
                self._hvac_mode = mode
                return True
        except ResponseError as err:
            _LOGGER.error("Failed to update mode: %s", err)
            return False

    @property
    def temperature(self):
        """Return current CV temperature"""
        return self.sensordata.get("room_temp").get('state')

    @property
    def target_temperature(self):
        """Return target CV temperature"""
        if (
            self._last_api_call[1] == "temperature"
            and self.sensordata.get("report_time").get('state') < self._last_api_call[0]
        ):
            return self._target_temperature
        return self.sensordata.get("ch_mode_temp").get('state')

    async def set_temp(self, target: float):
        """Set target CV temperature"""
        if target == self.target_temperature:
            return True
        try:
            if await self.async_set_atag(temperature=target):
                self._target_temperature = target
                return True
        except ResponseError as err:
            _LOGGER.error("Failed to set atag: %s", err)
            return False

    @property
    def dhw_temperature(self):
        """Return current dhw temperature"""
        return self.sensordata.get("dhw_water_temp").get('state')

    @property
    def dhw_min_temp(self):
        """Return dhw min temperature"""
        return self.sensordata.get("dhw_min_set").get('state')

    @property
    def dhw_max_temp(self):
        """Return dhw max temperature"""
        return self.sensordata.get("dhw_max_set").get('state')


    @property
    def dhw_target_temperature(self):
        """Return dhw target temperature"""

        if self.dhw_status:
            return self.sensordata.get("dhw_temp_setp").get('state')

        if (
            self._last_api_call[1] == "dhw_mode_temp"
            and self.sensordata.get("report_time").get('state') < self._last_api_call[0]
        ):
            return self._dhw_target_temperature
        return self.sensordata.get("dhw_mode_temp").get('state') % 150

    async def dhw_set_temp(self, target: float):
        """Set dhw target temperature"""
        if target == self.dhw_target_temperature:
            return True
        try:
            if await self.async_set_atag(dhw_target_temp=target):
                self._dhw_target_temperature = target
                return True
        except ResponseError as err:
            _LOGGER.error("Failed to set atag: %s", err)
            return False

    async def async_host_search(self):
        """Atag Discovery in case no host provided."""
        from .discovery import discover_atag

        _LOGGER.debug("No host provided, attempting discovery...")
        host, device = await discover_atag()
        if host and device:
            self.config.host = host
            self._device = device
            self.config.update_params()

    async def async_update(self):
        """Read data from thermostat."""
        if not self.initialized:
            self.initialized = True

        if not self.paired:
            await self.async_check_pair_status()
        await self.can_call()
        try:
            json_data = await self.connection.atag_put(data=self.config.retrieve_msg)
            sensordata = get_data_from_jsonreply(json_data)
            if sensordata:
                self.sensordata = sensordata
        except ResponseError as err:
            _LOGGER.warning("Failed to update Atag Data: %s", err)

    async def async_set_atag(self, **kwargs):
        """set mode and/or temperature."""

        payload = self.config.get_update_msg(**kwargs)
        await self.can_call()
        try:
            self._last_api_call = (
                datetime.datetime.now().astimezone(),
                list(kwargs)[0],
            )
            json_data = await self.connection.atag_put(payload)
            _LOGGER.debug("Update reply: %s", json_data)
            return check_reply(json_data) == 2
        except (ResponseError, KeyError) as err:
            raise RequestError("Failed to set Atag: {}".format(err))

    async def async_check_pair_status(self):
        """Confirm we are authorized."""

        if self.paired:
            return True
        if not self.initialized:
            self.initialized = True
        await self.can_call()
        try:
            self._last_api_call = (datetime.datetime.now().astimezone(), None)
            json_data = await self.connection.atag_put(self.config.pair_msg)
            status = check_reply(json_data)
            if status == 2 and self.device is not None:
                self._paired = True
            elif status == 2:
                json_data = await self.connection.atag_put(
                    self.config.get_retrieve_msg(info=0)
                )
                self._device = json_data["retrieve_reply"]["status"]["device_id"]
                self._paired = True
            else:
                self._paired = False
                raise ResponseError("Pairing failed")
        except ResponseError as err:
            self._paired = False
            raise RequestError("Pairing failed: {}".format(err))

    async def async_close(self):
        """Close the connection"""
        await self.connection.async_close()

    async def can_call(self):
        """Sleep until next API call can be made, to avoid device overload"""
        slept = min(
            datetime.datetime.now().astimezone() - self._last_api_call[0],
            datetime.timedelta(seconds=MINTIMEBETWEENCALLS),
        ).seconds
        await asyncio.sleep(MINTIMEBETWEENCALLS - slept)

        return True
