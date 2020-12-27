"""Provides connection to ATAG One Thermostat REST API."""
from .const import DEFAULT_PORT  # noqa
from .errors import AtagException  # noqa
from .gateway import AtagOne  # noqa
