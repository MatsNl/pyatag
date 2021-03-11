"""Provides connection to ATAG One Thermostat REST API."""

__version__ = "0.3.5.3"

from .errors import *  # noqa
from .gateway import AtagOne

assert AtagOne
