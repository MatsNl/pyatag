#-*- coding:utf-8 -*-
'''
Provides connection to ATAG One Thermostat REST API
'''
from .gateway import AtagDataStore
from .errors import AtagException
from .const import *
from .discovery import discover_atag