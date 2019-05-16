#-*- coding:utf-8 -*-

'''
Provides connection to ATAG One Thermostat REST API

#__version__ = '0.1.5'
__all__ = ["pytag"]

from pytag.gateway import AtagDataStore
'''
import asyncio
import pyatag.test

asyncio.get_event_loop().run_until_complete(pyatag.test.test())
