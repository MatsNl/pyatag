"""Constants for ATAG API."""

import datetime

STATE_HEAT = 'heat'
STATE_ECO = 'eco'
STATE_AUTO = 'auto'
STATE_MANUAL = 'manual'
STATE_EXTEND = 'extend'
STATE_OFF = 'off'

DEFAULT_TIMEOUT = 15
DEFAULT_PORT = 10000
DEFAULT_SCAN_INTERVAL = 30
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
CH_OPERATION_CONTROL = 'ch_control_mode'  # TBD HA
CH_MODE_DURATION = 'ch_mode_duration'  # TBD HA
CH_HOLD_DURATION = 'extend_duration'  # TBD HA
VACATION = 'vacation_duration'  # TBD HA
FIREPLACE_DURATION = 'fireplace_duration'  # TBD HA
REPORT_TIME = 'report_time'
BOILER_STATUS = 'boiler_status'
BOILER_CONF = 'boiler_config'

# DHW constants
DHW_STATE = "dhw_status"
DHW_CURRENT_TEMPERATURE = 'dhw_water_temp'
DHW_TEMPERATURE = 'dhw_temp_setp'  # TBD HA
DHW_OPERATION_MODE = "dhw_mode"  # TBD HA
DHW_MODE_TEMPERATURE = 'dhw_mode_temp'  # TBD HA

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
    DHW_OPERATION_MODE: "dhw_mode",
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
    'device_id': {'type': 'One ID'	, 'unit': 	 ''	, 'icon': 	 'mdi:account-card-details-outline'	, 'datafield': 	 'device_id'},
    'device_status': {'type': 'One status'	, 'unit': 	 ''	, 'icon': 	 'mdi:account-card-details-outline'	, 'datafield': 	 'device_status'},
    'connection_status': {'type': 'Connection'	, 'unit': 	 ''	, 'icon': 	 'mdi:wifi'	, 'datafield': 	 'connection_status'},
    'date_time': {'type': 'Datetime'	, 'unit': 	 ''	, 'icon': 	 'mdi:calendar-clock'	, 'datafield': 	 'date_time'},
    CH_CURRENT_TEMPERATURE: {'type': 'Current Temperature'	, 'unit': 	 '°C'	,
                             'icon': 	 'mdi:thermometer'	, 'datafield': 	 'room_temp'},
    'outside_temp': {'type': 'Outside Temp'	, 'unit': 	 '°C'	, 'icon': 	 'mdi:thermometer'	, 'datafield': 	 'outside_temp'},
    'outside_temp_avg': {'type': 'Average Outside Temperature'	, 'unit': 	 '°C'	, 'icon': 	 'mdi:thermometer'	, 'datafield': 	 'tout_avg'},
    WEATHER_STATUS: {'type': 'Weather Status'	, 'unit': 	 ''	,
                     'icon': 	 'mdi:white-balance-sunny'	, 'datafield': 	 'weather_status'},
    'pcb_temp': {'type': 'PCB Temperature'	, 'unit': 	 '°C'	, 'icon': 	 'mdi:thermometer'	, 'datafield': 	 'pcb_temp'},
    CH_TEMPERATURE: {'type': 'Target Temperature'	, 'unit': 	 '°C',
                     'icon': 	 'mdi:thermometer'	, 'datafield': 	 'shown_set_temp'},
    CH_OPERATION_MODE: {'type': 'Operation Mode'	, 'unit': 	 ''	,
                        'icon': 	 'mdi:settings'	, 'datafield': 	 'ch_mode'},
    'ch_water_pressure': {'type': 'Central Heating Pressure'	, 'unit': 	 'Bar'	, 'icon': 	 'mdi:gauge'	, 'datafield': 	 'ch_water_pres'},
    'ch_water_temp': {'type': 'CH Water Temperature'	, 'unit': 	 '°C'	, 'icon': 	 'mdi:thermometer'	, 'datafield': 	 'ch_water_temp'},
    'ch_return_temp': {'type': 'CH Return Temperature'	, 'unit': 	 '°C'	, 'icon': 	 'mdi:thermometer'	, 'datafield': 	 'ch_return_temp'},
    DHW_CURRENT_TEMPERATURE: {'type': 'Hot Water Temp'	, 'unit': 	 '°C'	,
                              'icon': 	 'mdi:thermometer'	, 'datafield': 	 'dhw_water_temp'},
    'dhw_water_pres': {'type': 'Hot Water Pressure'	, 'unit': 	 'Bar'	, 'icon': 	 'mdi:gauge'	, 'datafield': 	 'dhw_water_pres'},
    'dhw_flow_rate': {'type': 'Hot Water Flow Rate'	, 'unit': 	 '?'	, 'icon': 	 'mdi:gauge'	, 'datafield': 	 'dhw_flow_rate'},
    BOILER_STATUS: {'type': 'Boiler Status'	, 'unit': 	 ''	,
                    'icon': 	 'mdi:flash'	, 'datafield': 	 'boiler_status'},
    BOILER_CONF: {'type': 'Boiler Config'	, 'unit': 	 ''	,
                  'icon': 	 'mdi:flash'	, 'datafield': 	 'boiler_config'},
    'burning_hours': {'type': 'Burning Hours'	, 'unit': 	 'h'	, 'icon': 	 'mdi:fire'	, 'datafield': 	 'burning_hours'},
    'voltage': {'type': 'Voltage'	, 'unit': 	 'V'	, 'icon': 	 'mdi:flash'	, 'datafield': 	 'voltage'},
    'current': {'type': 'Current'	, 'unit': 	 'mA'	, 'icon': 	 'mdi:flash-auto'	, 'datafield': 	 'current'},
    'flame_level': {'type': 'Flame'	, 'unit': 	 '%'	, 'icon': 	 'mdi:fire'	, 'datafield': 	 'rel_mod_level'},
    REPORT_TIME: {'type': 'Report Time'	, 'unit': 	 ''	,
                  'icon': 	 'mdi:clock'	, 'datafield': 	 'report_time'},
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
    23: {'state': "Connected to BCU"}
}

WEATHER_STATES = {
    0: {'state': 'Sunny', 'icon': 'mdi:weather-sunny'},
    1: {'state': 'Clear', 'icon': 'mdi:weather-night'},
    2: {'state': 'Rainy', 'icon': 'mdi:weather-rainy'},
    # Not sure, Atag icons unclear
    3: {'state': 'Snowy', 'icon': 'mdi:weather-snowy'},
    # Not sure, Atag icons unclear
    4: {'state': 'Haily', 'icon': 'mdi:weather-hail'},
    5: {'state': 'Windy', 'icon': 'mdi:weather-windy'},
    6: {'state': 'Misty', 'icon': 'mdi:weather-fog'},
    7: {'state': 'Cloudy', 'icon':  'mdi:weather-cloudy'},
    8: {'state': 'Partly Sunny', 'icon':  'mdi:weather-partlycloudy'},
    9: {'state': 'Partly Cloudy', 'icon': 'mdi:cloud'},  # Night with clouds..
    # Not sure, Atag icons unclear
    10: {'state': 'Shower', 'icon': 'mdi:weather-pouring'},
    11: {'state': 'Lightning', 'icon':  'mdi:weather-lightning'},
    12: {'state': 'Hurricane', 'icon': 'mdi:weather-hurricane'},
    13: {'state': 'Unknown', 'icon': 'mdi:cloud-question'}
}

MODES = {STATE_MANUAL: 1, STATE_AUTO: 2, STATE_EXTEND: 4}
INT_MODES = {v: {'state': k} for k, v in MODES.items()}

# Non weather based and weather based respectively
CH_CONTROLS = {'heat': 0, 'auto': 1}
INT_CH_CONTROLS = {v: {'state': k} for k, v in CH_CONTROLS.items()}

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
