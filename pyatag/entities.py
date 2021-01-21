"""Classes within AtagOne object."""
from datetime import datetime, timedelta

from .const import CLASSES, SENSORS, STATES


def convert_time(seconds, sensorclass="time"):
    """Convert reported time to real time."""
    if sensorclass == "duration":
        return str(timedelta(seconds=seconds))
    return str(datetime(2000, 1, 1) + timedelta(seconds=seconds))


class Report:
    """Main object to hold report and control data."""

    def __init__(self, data, update, setter):
        """Initiate object for Sensor and Control data."""
        self._update = update
        self._setter = setter
        self._items = {}
        self._data = data
        self._classes = CLASSES
        self._classes["temp"][1] = STATES["temp_unit"][
            self._data["configuration"]["temp_unit"]
        ]
        self._process_raw(self._data)

    def update(self, data):
        """Process latest data."""
        self._data = data
        self._process_raw(self._data)

    def _process_raw(self, raw):
        """Push data to the sensor and control objects."""
        for grp in ["configuration", "status", "report", "control"]:
            for _id, raw_i in raw[grp].items():
                name = SENSORS.get(_id)
                obj = self._items.get(name) or self._items.get(_id)

                if obj is not None:
                    obj.raw = raw_i
                elif grp == "control":
                    self._items[name or _id] = Control(
                        _id, raw_i, self._classes, self._setter
                    )
                else:
                    self._items[name or _id] = Sensor(_id, raw_i, self._classes)

    def items(self):
        """Return the report objects."""
        return self._items.values()

    @property
    def report_time(self):
        """Return latest report time."""
        return self._items["report_time"].state

    def __getitem__(self, obj_id):
        """Return selected sensor object by name or ID."""
        if obj_id in SENSORS:
            return self._items[SENSORS[obj_id]]
        return self._items[obj_id]

    def __iter__(self):
        """Iterate over sensor and control objects."""
        return iter(self._items.values())


class Sensor:
    """Represents an Atag sensor."""

    def __init__(self, _id, raw, classes):
        """Initiate sensor object."""
        self.id = _id
        self.raw = raw
        self._info = classes.get(self.id.split("_")[-1])
        if _id == "tout_avg":
            self._info = classes["temp"]
        if _id == "rel_mod_level":
            self._info = classes["rate"]
        self._states = STATES.get(self.id)

    @property
    def name(self):
        """Return the readable name of the Sensor."""
        return SENSORS.get(self.id) or self.id

    @property
    def sensorclass(self):
        """Return the sensorclass if known."""
        if self._info:
            return self._info[0]

    @property
    def state(self):
        """Return state, if known in readable format."""
        if self.sensorclass in ["time", "duration"]:
            return convert_time(self.raw, self.sensorclass)
        if self.id == "boiler_status":
            return {
                "burner": self.raw & 8 == 8,
                "dhw": self.raw & 4 == 4,
                "ch": self.raw & 2 == 2,
            }
        if self.id == "download_url":
            return self.raw.split("/")[-1]
        if self._states is not None:
            if isinstance(self._states[self.raw], dict):
                return self._states[self.raw]["state"]
            return self._states[self.raw]
        return self.raw

    @property
    def icon(self):
        """Return the icon corresponding to the state."""
        if self._info:
            return self._info[2]
        if self._states is not None:
            if isinstance(self._states[self.raw], dict):
                return self._states[self.raw]["icon"]
        return None

    @property
    def measure(self):
        """Return the unit of measurement if known."""
        if self._info:
            return self._info[1]
        return None

    def __repr__(self):
        """Return the name of the Sensor."""
        return str(self.state)


class Control(Sensor):
    """Represents an Atag control."""

    def __init__(self, _id, raw, classes, setter):
        """Initiate Control object."""
        super().__init__(_id, raw, classes)
        self._setter = setter
        self._target = None
        self._last_call = None

    @property
    def state(self):
        """Return reported state, or target state if recently set."""
        if self._target:
            if (datetime.utcnow() - self._last_call).total_seconds() < 15:
                return self._target
            self._target = None
        if self.sensorclass in ["time", "duration"]:
            return convert_time(self.raw, self.sensorclass)
        if self._states:
            if isinstance(self._states[self.raw], dict):
                return self._states[self.raw]["state"]
            return self._states[self.raw]
        if self.id == "dhw_mode_temp":
            return self.raw % 150
        return self.raw

    async def set_state(self, target):
        """Set the Control to a new target state."""
        target_int = None
        if self._states is not None:
            target = {v.lower(): v for v in self._states.values()}.get(target.lower())
            target_int = {v: k for k, v in self._states.items()}.get(target)
        if target == self.state:
            return True
        self._target = target
        self._last_call = datetime.utcnow()
        return await self._setter(**{self.id: target_int or target})


class Climate:
    """Main climate entity."""

    def __init__(self, report):
        """Initiate the main climate object."""
        self._report = report

    def __repr__(self):
        """Return Climate properties."""
        return ", ".join(
            [
                f"temperature: {self.temperature} {self.temp_unit}",
                f"target: {self.target_temperature} {self.temp_unit}",
                f"status: {self.status}",
                f"burner status: {self.burnerstatus}",
                f"hvac mode: {self.hvac_mode}",
                f"preset mode: {self.preset_mode}",
                f"flame: {self.flame}",
            ]
        )

    @property
    def temp_unit(self):
        """Return temperature unit."""
        return self._report["temp_unit"].state

    @property
    def burnerstatus(self):
        """Return boolean for burner active."""
        return self._report["boiler_status"].state["burner"]

    @property
    def status(self):
        """Return HVAC action."""
        return self._report["boiler_status"].state["ch"]

    @property
    def flame(self):
        """Return flame level."""
        if self.status:
            return self._report["rel_mod_level"].state
        return 0

    @property
    def hvac_mode(self):
        """Return the operating mode (Weather or Regular/Heat)."""
        return self._report["ch_control_mode"].state

    async def set_hvac_mode(self, target: str) -> bool:
        """Set the operating mode (Weather or Regular/Heat)."""
        await self._report["ch_control_mode"].set_state(target)

    @property
    def preset_mode(self):
        """Return the preset mode (Manual/Auto/Extend/Vacation/Fireplace)."""
        return self._report["ch_mode"].state

    @property
    def preset_mode_duration(self):
        """Return remaining time on preset mode."""
        return self._report["ch_mode_duration"].state

    async def set_preset_mode(self, target: str, **kwargs) -> bool:
        """Set the hold mode (Manual/Auto/Extend/Vacation/Fireplace)."""
        await self._report["ch_mode"].set_state(target)

    @property
    def temperature(self):
        """Return current indoor temperature."""
        return self._report["room_temp"].state

    @property
    def target_temperature(self):
        """Return target temperature."""
        return self._report["ch_mode_temp"].state

    async def set_temp(self, target: float):
        """Set target temperature."""
        await self._report["ch_mode_temp"].set_state(target)


class DHW:
    """Main Domestic Hot Water object."""

    def __init__(self, report):
        """Initiate main DHW object."""
        self._report = report

    @property
    def temp_unit(self):
        """Return temperature unit."""
        return self._report["temp_unit"].state

    @property
    def burnerstatus(self):
        """Return boolean for burner status."""
        return self._report["boiler_status"].state["burner"]

    @property
    def status(self):
        """Return boolean indicator for heating for DHW."""
        return self._report["boiler_status"].state["dhw"]

    @property
    def flame(self):
        """Return flame level if active for DHW."""
        if self.status:
            return self._report["rel_mod_level"].state
        return 0

    @property
    def temperature(self):
        """Return water temperature."""
        return self._report["dhw_water_temp"].state

    @property
    def min_temp(self):
        """Return dhw min temperature."""
        return self._report["dhw_min_set"].state

    @property
    def max_temp(self):
        """Return dhw max temperature."""
        return self._report["dhw_max_set"].state

    @property
    def target_temperature(self):
        """Return dhw target temperature."""
        if self.status:
            return self._report["dhw_temp_setp"].state
        return self._report["dhw_mode_temp"].state
    
    @property
    def current_operation(self):
        """Return the current operating mode (Eco or Performance (Comfort)."""
        return self._report["dhw_mode"].state if self.status else "off"

    async def set_temp(self, target: float):
        """Set dhw target temperature."""
        await self._report["dhw_temp_setp"].set_state(target)
