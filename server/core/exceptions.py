from sanic.exceptions import *


class ImproperlyConfigured(ServerError):
  pass


class DBClientError(ServerError):
  pass


class BadRequestError(InvalidUsage):
  pass
