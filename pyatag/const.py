"""Constants for ATAG API."""

import datetime

CONF_INTERFACE = 'interface'

STATE_HEAT = 'heat'
STATE_ECO = 'eco'
STATE_AUTO = 'auto'
STATE_MANUAL = 'manual'
STATE_EXTEND = 'extend'
STATE_OFF = 'off'

DEFAULT_TIMEOUT = 15
DEFAULT_PORT = 10000
DEFAULT_SCAN_INTERVAL = 120
DEFAULT_MIN_TEMP = 12
DEFAULT_MAX_TEMP = 21
REQUEST_INFO = 71

HTTP_HEADER = {
    'Content-type': 'applicaton/json;charset=UTF-8',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (compatible; AtagOneAPI/x; http://atag.one/)'
}

# CH constants
CH_STATE = "ch_status"
CH_CURRENT_TEMPERATURE = 'current_temperature'
CH_MAX_TEMP = 'max_temp'
CH_MIN_TEMP = 'min_temp'
CH_OPERATION_LIST = 'operation_list'
CH_OPERATION_MODE = 'operation_mode'
CH_TEMPERATURE = 'temperature'
CH_OPERATION_CONTROL = 'ch_control_mode' # TBD HA
CH_MODE_DURATION = 'ch_mode_duration' # TBD HA
CH_HOLD_DURATION = 'extend_duration' # TBD HA
VACATION = 'vacation_duration' # TBD HA
FIREPLACE_DURATION = 'fireplace_duration' # TBD HA
REPORT_TIME = 'report_time'
BOILER_STATUS = 'boiler_status'
BOILER_CONF = 'boiler_config'

# DHW constants
DHW_STATE = "dhw_status"
DHW_CURRENT_TEMPERATURE = 'dhw_water_temp'
DHW_TEMPERATURE = 'dhw_temp_setp' # TBD HA
DHW_OPERATION_MODE = "dhw_mode" # TBD HA
DHW_MODE_TEMPERATURE = 'dhw_mode_temp' # TBD HA

STATUS = 'status'
REPORT = 'report'
CONTROL = 'control'
DETAILS = 'details'
ACC_STATUS = 'acc_status'
WEATHER_STATUS = 'weather_status'
WEATHER_CURRENT_TEMPERATURE = 'weather_current_temperature'

CONTROLS = {
    CH_STATE: "ch_status",
    CH_OPERATION_CONTROL: "ch_control_mode",
    CH_OPERATION_MODE: "ch_mode",
    CH_MODE_DURATION: "ch_mode_duration",
    CH_TEMPERATURE: "ch_mode_temp",
    CH_HOLD_DURATION: "extend_duration",
    FIREPLACE_DURATION: "fireplace_duration",
    VACATION: "vacation_duration",
    DHW_TEMPERATURE: "dhw_temp_setp",
    DHW_STATE: "dhw_status",
    DHW_OPERATION_MODE:"dhw_mode",
    DHW_MODE_TEMPERATURE: "dhw_mode_temp",
    WEATHER_STATUS: 'weather_status',
    WEATHER_CURRENT_TEMPERATURE: 'weather_temp'
}

REPORT_STRUCTURE = {
    STATUS: ["device_id", "device_status", "connection_status", "date_time"],
    REPORT: ["report_time", "burning_hours", "device_errors", "boiler_errors", "room_temp",
             "outside_temp", "dbg_outside_temp", "pcb_temp", "ch_setpoint", "dhw_water_temp",
             "ch_water_temp", "dhw_water_pres", "ch_water_pres", "ch_return_temp",
             "boiler_status", "boiler_config", "ch_time_to_temp", "shown_set_temp",
             "power_cons", "tout_avg", "rssi", "current", "voltage", "charge_status",
             "lmuc_burner_starts", "dhw_flow_rate", "resets", "memory_allocation"],
    DETAILS: ["boiler_temp", "boiler_return_temp", "min_mod_level", "rel_mod_level",
              "boiler_capacity", "target_temp", "overshoot", "max_boiler_temp", "alpha_used",
              "regulation_state", "ch_m_dot_c", "c_house", "r_rad", "r_env", "alpha", "alpha_max",
              "delay", "mu", "threshold_offs", "wd_k_factor ", "wd_exponent",
              "lmuc_burner_hours", "lmuc_dhw_hours", "KP", "KI"],
    CONTROL: ["ch_status", "ch_control_mode", "ch_mode", "ch_mode_duration", "ch_mode_temp",
              "dhw_temp_setp", "dhw_status", "dhw_mode", "dhw_mode_temp", "weather_temp",
              "weather_status", "vacation_duration", "extend_duration", "fireplace_duration"]
}
SENSOR_TYPES = {
    'device_id': ['One ID', '', 'mdi:account-card-details-outline', 'device_id'],
    'device_status': ['One status', '', 'mdi:account-card-details-outline', 'device_status'],
    'connection_status': ['Connection', '', 'mdi:wifi', 'connection_status'],
    'date_time': ['Datetime', '', 'mdi:calendar-clock', 'date_time'],
    CH_CURRENT_TEMPERATURE: ['Current Temperature', '°C', 'mdi:thermometer', 'room_temp'],
    'outside_temp': ['Outside Temp', '°C', 'mdi:thermometer', 'outside_temp'],
    'outside_temp_avg': ['Average Outside Temperature', '°C', 'mdi:thermometer', 'tout_avg'],
    WEATHER_STATUS: ['Weather Status', '', 'mdi:white-balance-sunny', 'weather_status'],
    'pcb_temp': ['PCB Temperature', '°C', 'mdi:thermometer', 'pcb_temp'],
    CH_TEMPERATURE: ['Target Temperature', '°C', 'mdi:thermometer', 'shown_set_temp'],
    CH_OPERATION_MODE: ['Operation Mode', '', 'mdi:settings', 'ch_mode'],
    'ch_water_pressure': ['Central Heating Pressure', 'Bar', 'mdi:gauge', 'ch_water_pres'],
    'ch_water_temp': ['CH Water Temperature', '°C', 'mdi:thermometer', 'ch_water_temp'],
    'ch_return_temp': ['CH Return Temperature', '°C', 'mdi:thermometer', 'ch_return_temp'],
    DHW_CURRENT_TEMPERATURE: ['Hot Water Temp', '°C', 'mdi:thermometer', 'dhw_water_temp'],
    'dhw_water_pres': ['Hot Water Pressure', 'Bar', 'mdi:gauge', 'dhw_water_pres'],
    'dhw_flow_rate': ['Hot Water Flow Rate', '?', 'mdi:gauge', 'dhw_flow_rate'],
    BOILER_STATUS: ['Boiler Status', '', 'mdi:flash', 'boiler_status'],
    BOILER_CONF: ['Boiler Config', '', 'mdi:flash', 'boiler_config'],
    'burning_hours': ['Burning Hours', 'h', 'mdi:fire', 'burning_hours'],
    'voltage': ['Voltage', 'V', 'mdi:flash', 'voltage'],
    'current': ['Current', 'mA', 'mdi:flash-auto', 'current'],
    'flame_level': ['Flame', '%', 'mdi:fire', 'rel_mod_level'],
    REPORT_TIME: ['Report Time', '', 'mdi:clock', 'report_time'],
}

for i in CONTROLS:
    if i not in SENSOR_TYPES:
        SENSOR_TYPES[i] = [i, '', 'mdi:flash', CONTROLS[i]]

REPORT_STRUCTURE_INV = {
    v: i for i in REPORT_STRUCTURE for v in REPORT_STRUCTURE[i]}

BOILER_STATES = {
    14: 'Heating CV & Water',
    12: 'Heating Water',
    10: 'Heating CV',
    8: 'Heating Boiler',
    4: 'Pumping Water',
    2: 'Pumping CV',
    0: 'Idle'
}

CONNECTION_STATES = {
    23: "Connected to BCU"
}

WEATHER_STATES = {
    0: ['Sunny', 'mdi:weather-sunny'],
    1: ['Clear', 'mdi:weather-night'],
    2: ['Rainy', 'mdi:weather-rainy'],
    3: ['Snowy', 'mdi:weather-snowy'],  # Not sure, Atag icons unclear
    4: ['Haily', 'mdi:weather-hail'],  # Not sure, Atag icons unclear
    5: ['Windy', 'mdi:weather-windy'],
    6: ['Misty', 'mdi:weather-fog'],
    7: ['Cloudy', 'mdi:weather-cloudy'],
    8: ['Partly Sunny', 'mdi:weather-partlycloudy'],
    9: ['Partly Cloudy', 'mdi:cloud'],  # Night with clouds..
    10: ['Shower', 'mdi:weather-pouring'],  # Not sure, Atag icons unclear
    11: ['Lightning', 'mdi:weather-lightning'],
    12: ['Hurricane', 'mdi:weather-hurricane'],
    13: ['Unknown', 'mdi:cloud-question']
}

MODES = {STATE_MANUAL: 1, STATE_AUTO: 2, STATE_EXTEND: 4}
INT_MODES = {v: k for k, v in MODES.items()}

CH_CONTROLS = {'heat': 0, 'auto': 1} # Non weather based and weather based respectively
INT_CH_CONTROLS = {v: k for k, v in CH_CONTROLS.items()}

SENSOR_VALUES = {
    "report_time": 'time',
    "date_time": 'time',
    "weather_status": WEATHER_STATES,
    "connection_status": CONNECTION_STATES,
    "boiler_status": BOILER_STATES,
    "ch_control_mode": INT_CH_CONTROLS,
    'ch_mode': INT_MODES,
    'boiler_config': 'int',
    "ch_status": 'int',
    "dhw_status": 'int',
    "device_status": 'int'
}

SQLTYPES = {
    float: 'FLOAT',
    int: 'INT',
    datetime.datetime: 'DATETIME',
    str: 'TEXT',
    list: 'TEXT',
    dict: 'TEXT',
    type(None): 'TEXT'
}
