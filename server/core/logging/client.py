from core.logging import config


class LoggerClient:
  """A client to orchastrate stdout logging using injectable formatter.

  Only writes logs if the requested level equal or above the determined log level on the config.

  **config.py**

  LEVELS = {
    TRACE: 1,
    DEBUG: 2,
    WARNING: 3,
    INFO: 4,
    ERROR: 5,
    CRITICAL: 6,
  }
  """

  def __init__(self, name=config.NAME, formatter=None):
    """Initializes the client.

    Args:
      name (str): The name of the streamer.
      formatter (core.logging.formatter.Formatter): The message formatter for the client.
    """
    self.name = name
    self.formatter = formatter or config.formatter()

  def _stdout(self, message, level):
    if config.is_enabled(level):
      print(self.formatter.format(message=f'{message}', level=level, streamer=self.name))

  def trace(self, message):
    """Logs trace level message."""
    self._stdout(message, level=config.TRACE)

  def debug(self, message):
    """Logs debug level message."""
    self._stdout(message, level=config.DEBUG)

  def warning(self, message):
    """Logs warning level message."""
    self._stdout(message, level=config.INFO)

  def info(self, message):
    """Logs info level message."""
    self._stdout(message, level=config.INFO)

  def error(self, message):
    """Logs error level message."""
    self._stdout(message, level=config.ERROR)

  def critical(self, message):
    """Logs critical level message."""
    self._stdout(message, level=config.CRITICAL)
