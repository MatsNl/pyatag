class AtagException(Exception):
    """Base error for atag_Thermostat."""

class RequestError(AtagException):
    """
    Invalid request.
    Unable to fulfill request.
    Raised when host or API cannot be reached.
    """

class ResponseError(AtagException):
    """Invalid response."""


class Response404Error(AtagException):
    """Invalid response."""


class SensorNoLongerAvailable(AtagException):
    """Invalid response."""

