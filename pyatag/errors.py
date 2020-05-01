"""Error handling for atag_Thermostat."""

class AtagException(Exception):
    """Base error for atag_Thermostat."""


class Unauthorized(AtagException):
    """Failed to authenticate."""

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

ERRORS = {1: Unauthorized, 2: RequestError, 3: ResponseError,4: Response404Error,5: SensorNoLongerAvailable}

def raise_error(error,type=None):
    cls = ERRORS.get(type, AtagException)
    raise cls(error)
