DOMAIN = 'atag'
ATAG_HANDLE = 'atag_handle'
DATA_LISTENER = 'listener'
REQUEST_INFO = 64 + 8 + 1
SIGNAL_UPDATE_ATAG = 'atag_update'

STATE_HEAT = 'heat'
STATE_ECO = 'eco'
STATE_AUTO = 'auto'
STATE_MANUAL = 'manual'
ATTR_OPERATION_MODE = 'operation_mode'

DEFAULT_TIMEOUT = 15
DEFAULT_PORT = 10000
DEFAULT_SCAN_INTERVAL = 120
HTTP_HEADER = {
    'Content-type': 'applicaton/x-www-form-urlencoded;charset=UTF-8',
    'Connection': 'Close',
    'User-Agent': 'Mozilla/5.0 (compatible; AtagOneAPI/x; http://atag.one/)'
}
SENSOR_TYPES = {
    'current_temp': ['Room Temp', '°C', 'mdi:thermometer','room_temp'],
    'outside_temp': ['Outside Temp', '°C', 'mdi:thermometer','outside_temp'],
    'outside_temp_avg': ['Average Outside Temp', '°C', 'mdi:thermometer','tout_avg'],
    'pcb_temp': ['PCB Temp', '°C', 'mdi:thermometer','pcb_temp'],
    'temperature': ['Target Temp', '°C', 'mdi:thermometer','shown_set_temp'],
    'ch_water_pressure': ['Central Heating Pressure', 'Bar', 'mdi:gauge','ch_water_pres'],
    'ch_water_temp': ['Central Heating Water Temp', '°C', 'mdi:thermometer','ch_water_temp'],
    'ch_return_temp': ['Central Heating Return Temp', '°C', 'mdi:thermometer','ch_return_temp'],
    'dhw_water_temp': ['Hot Water Temp', '°C', 'mdi:thermometer','dhw_water_temp'],
    'dhw_water_pres': ['Hot Water Pressure', 'Bar', 'mdi:gauge','dhw_water_pres'],
    'boiler_status': ['Boiler Status', '', 'mdi:flash','boiler_status'],
    'boiler_config': ['Boiler Config', '', 'mdi:flash','boiler_config'],
    'water_pressure': ['Boiler Pressure', 'Bar', 'mdi:gauge','water_pressure'],
    'burning_hours': ['Burning Hours', 'h', 'mdi:fire','burning_hours'],
    'voltage': ['Voltage', 'V', 'mdi:flash','voltage'],
    'current': ['Current', 'mA', 'mdi:flash-auto','current'],
    'flame_level': ['Flame', '%', 'mdi:fire','rel_mod_level'],
}

BOILER_STATUS = 'boiler_status'
BOILER_STATES = {
    14: 'Heating CV & Water',
    12: 'Heating Water',
    10: 'Heating CV',
    8: 'Heating Boiler',
    4: 'Water active',
    2: 'CV active',
    0: 'Idle'
}

MODES = {STATE_MANUAL: 1, STATE_AUTO: 2}
INT_MODES = {v: k for k, v in MODES.items()}

UPDATE_MODE = 'update_mode'
UPDATE_TEMP = 'update_temp'
PAIR_PATH = 'pair'
UPDATE_PATH = 'update'
RETRIEVE_PATH = 'retrieve'
UPDATE_REPLY = 'update_reply'
RETRIEVE_REPLY = 'retrieve_reply'
PAIR_REPLY = 'pair_reply'
REPORT = 'report'
CONTROL = 'control'
DETAILS = 'details'
ACC_STATUS = 'acc_status'

DEFAULT_NAME = 'Atag One Thermostat'
DEFAULT_MIN_TEMP = 12
DEFAULT_MAX_TEMP = 21

SENSOR_PREFIX = 'Atag '
ATTR_REPORT_TIME = 'report_time'
ATTR_OPERATION_MODE_INT = 'ch_mode'

#ATTR_CURRENT_HUMIDITY = 'current_humidity'
#ATTR_CURRENT_TEMPERATURE = 'current_temp'

#ATTR_HUMIDITY = 'humidity'
#ATTR_MAX_HUMIDITY = 'max_humidity'
ATTR_MAX_TEMP = 'max_temp'
#ATTR_MIN_HUMIDITY = 'min_humidity'
ATTR_MIN_TEMP = 'min_temp'
ATTR_OPERATION_LIST = 'operation_list'
ATTR_OPERATION_MODE = 'operation_mode'
ATTR_OPERATION_MODE_INT = 'ch_mode'
ATTR_TEMPERATURE_SET = 'shown_set_temp'
ATTR_TEMPERATURE = 'temperature'
#ATTR_TARGET_TEMP_HIGH = 'target_temp_high'
#ATTR_TARGET_TEMP_LOW = 'target_temp_low'
#ATTR_TARGET_TEMP_STEP = 'target_temp_step'