class ClientError(Exception):
  pass


class ImproperlyConfigured(Exception):
  pass


class BadValueError(Exception):
  pass


class DoesNotExist(Exception):
  pass


class FieldError(Exception):
  pass


class ModelReferenceError(Exception):
  pass


class FieldDoesNotExist(Exception):
  pass


class EntityExists(Exception):
  pass


class MaxRetryExceeded(Exception):
  pass
