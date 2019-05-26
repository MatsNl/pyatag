"""Base data to initiate an AtagDataStore."""

host_config = {
    "host": "",  # atag IP
    "port": 10000,
    "mail": "",  # email registered in portal
    "scan_interval": 30,
    "interface": "en0",  # interface on which API runs
    "sensors": [  # sensors to test, see const.py
        "temperature",
        "current_temp"
    ]
}
