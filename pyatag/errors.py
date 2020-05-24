"""Error handling for atag_Thermostat."""


class AtagException(Exception):
    """Base error for AtagOne devices."""


class Unauthorized(AtagException):
    """Failed to authenticate."""


class RequestError(AtagException):
    """Unable to fulfill request."""


class ResponseError(AtagException):
    """Invalid response."""


class Response404Error(AtagException):
    """Invalid response."""


class UnknownAtagError(AtagException):
    """Invalid response."""


ERRORS = {
    1: Unauthorized,
    2: RequestError,
    3: ResponseError,
    4: Response404Error,
    5: UnknownAtagError,
}


def raise_error(err, errortype=None):
    """Raise the appropriate error."""
    cls = ERRORS.get(errortype, AtagException)
    raise cls(err)
