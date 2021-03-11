"""Error handling for atag_Thermostat."""


class AtagException(Exception):
    """Base error for AtagOne devices."""


class Unauthorized(AtagException):
    """Failed to authenticate."""


class RequestError(AtagException):
    """Unable to fulfill request."""


class ConnectionError(AtagException):
    """Unable to fulfill request."""


class ResponseError(AtagException):
    """Invalid response."""


class UnknownAtagError(AtagException):
    """Invalid response."""
