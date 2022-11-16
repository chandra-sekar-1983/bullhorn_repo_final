import abc
import json

from pygments import formatters
from pygments import highlight
from pygments import lexers

from core.logging import config


class Formatter(metaclass=abc.ABCMeta):
  """Abstract class for log formatter.

  Attributes:
    colored (bool): Whether or not message should be colored.
    context (dict): Extra context to be added to message.

  """
  colored = False
  context = {}

  @abc.abstractmethod
  def format(self, message=None, level=config.TRACE, streamer='root', **kwargs):
    pass


class TextFormatter(Formatter):
  """Text log formatter."""
  colored = True
  YELLOW = '\033[93m'
  ENDC = '\033[0m'

  def format(self, message=None, level=config.TRACE, streamer='root', **kwargs):
    if self.colored:
      return f'{self.YELLOW}{message}{self.ENDC}'


class JSONFormatter(Formatter):
  """JSON log formatter."""
  colored = True

  def format(self, message=None, level=config.TRACE, streamer='root', **kwargs):
    self.context.update(kwargs)
    entry = dict(
        streamer=streamer,
        severity=level,
        message=message,
        **self.context
    )
    formatted_json = json.dumps(entry)
    if self.colored:
      return highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())

    return formatted_json


class GCPFormatter(JSONFormatter):
  """Special GCP formatter which includes necessary parameters to bind request with messages."""
  colored = False

  def __init__(self):
    request_is_defined = 'request' in globals() or 'request' in locals()
    if config.GCP_PROJECT_ID and request_is_defined and request:  # noqa: F821
      trace_header = request.headers.get('X-Cloud-Trace-Context')  # noqa: F821
      if trace_header:
        trace = trace_header.split('/')
        key = 'logging.googleapis.com/trace'
        value = f'projects/{config.GCP_PROJECT_ID}/traces/{trace[0]}'
        self.context[key] = [value]
