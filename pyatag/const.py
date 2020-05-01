"""Constants for ATAG API."""
CLASSES = {
    'temp': ('temperature', '°', "mdi:thermometer"),
    'pres': ('pressure', 'bar', "mdi:gauge"),
    'time': ('time',None, 'mdi:clock'),
    'duration': ('duration', None,'mdi:timer')
}

SENSORS = {
    "ch_water_pres": "CH Water Pressure",
    "outside_temp": "Outside Temperature",
    "tout_avg": "Average Outside Temperature",
    "ch_water_temp": "CH Water Temperature",
    "ch_return_temp":"CH Return Temperature",
    "burning_hours": "Burning Hours",
    "rel_mod_level": "Flame",
    "weather_status": "Weather Status",
    'download_url': "API Version",
    'ch_mode': "CH Preset Mode",
    'ch_mode_duration': "CH Preset Duration",
    'ch_control_mode': 'CH HVAC Mode',
    'ch_mode_temp': 'CH Target Temperature'
}

STATES = {
    'weather_status': {
        0: {"state": "Sunny", "icon": "mdi:weather-sunny"},
        1: {"state": "Clear", "icon": "mdi:weather-night"},
        2: {"state": "Rainy", "icon": "mdi:weather-rainy"},
        3: {"state": "Snowy", "icon": "mdi:weather-snowy"},
        4: {"state": "Haily", "icon": "mdi:weather-hail"},
        5: {"state": "Windy", "icon": "mdi:weather-windy"},
        6: {"state": "Misty", "icon": "mdi:weather-fog"},
        7: {"state": "Cloudy", "icon": "mdi:weather-cloudy"},
        8: {"state": "Partly Sunny", "icon": "mdi:weather-partlycloudy"},
        9: {"state": "Partly Cloudy", "icon": "mdi:cloud"},
        10: {"state": "Shower", "icon": "mdi:weather-pouring"},
        11: {"state": "Lightning", "icon": "mdi:weather-lightning"},
        12: {"state": "Hurricane", "icon": "mdi:weather-hurricane"},
        13: {"state": "Unknown", "icon": "mdi:cloud-question"},
    },
    'temp_unit': {
        0:'°C',
        1: '°F'
    },
    'ch_mode': {
        1: 'manual',
        2: 'auto',
        3: 'away',
        4: 'extend',
        5: 'boost',
    },
    'ch_control_mode': {
        0:"heat",
        1:"auto"
    }
}