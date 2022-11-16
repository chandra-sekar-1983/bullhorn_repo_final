import httpx
import importlib
import inspect
import os
import re

from core import exceptions


def getenv(key, default=None, required=True):
  """Returns environment variable by the given key.

  Args:
    default (ANY): The default value.
    required (bool): Whether or not env var is required.
  """
  try:
    return os.environ[key]
  except KeyError:
    if required and default is None:
      raise exceptions.ImproperlyConfigured(f'Environment var {key} is required')

    return default


def make_list(val):
  """Wraps a val into a list if it's not already a list."""
  return list(val) if not isinstance(val, list) else val


async def make_request(method, url, params=None, data=None, headers=None):
  """Makes HTTP Request using AsyncClient inside the application event loop.

  Args:
    method (str): The HTTP method for this request.
    url (str): The url to be called.
    params (dict): The request parameters.
    data (dict): The body of the request.
    headers (dict): The headers of the request.

  Returns:
    HTTPResponse
  """
  async with httpx.AsyncClient() as client:
    response = await client.request(method, url, params=params, data=data, headers=headers)
    try:
      response.raise_for_status()
    except httpx._exceptions.HTTPStatusError as e:
      raise exceptions.BadRequestError(f'{method} request error to {url}: {e}')

    return response


def get_cors_headers(allow_methods=None, allow_origins=None, allow_headers=None):
  """Configures headers for CORS.

  Args:
    allow_methods (list): List of methods should be allowed.
    allow_origins (list): List of origins should be allowed.
    allow_headers (list): List of headers should be allowed.
  """
  headers = {}
  if allow_methods:
    allow_methods = make_list(allow_methods)
    headers['Access-Control-Allow-Methods'] = ','.join(allow_methods)

  if allow_origins:
    allow_origins = make_list(allow_origins)
    headers['Access-Control-Allow-Origin'] = ','.join(allow_origins)

  if allow_headers:
    allow_headers = make_list(allow_headers)
    headers['Accces-Control-Allow-Headers'] = ','.join(allow_headers)

  return headers


def load_class(class_path):
  """Dynamically loads a class with the given class path.

  Args:
    class_path (str): The full path of the class.

  i.e.
    client = utils.load_class('core.orm.clients.redis.RedisClient')

  """
  class_name = class_path.split('.')[-1]
  module_name = class_path.replace(f'.{class_name}', '')

  module = importlib.import_module(module_name)
  if not module:
    return

  return getattr(module, class_name)


def camel_to_snake(string):
  """Returns snake case string for given camel case string.

  i.e.
    camel_to_snake('TestFeature') # Returns 'test_feature'
  """
  rgx = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
  return rgx.sub(r'_\1', string).lower()


def get_members(module, cls):
  """Returns all occurances of a given class inside of a given module.

  i.e. middlewares.py

  from core.sanic import Middleware
  class TestMiddleware(Middleware):
    pass

  middlewares = importlib.import_module('middlewares')
  get_members(middlewares, Middleware) # Returns [TestMiddleware]
  """
  if not module:
    return []

  members = []
  for name, member in module.__dict__.items():
    if (
      inspect.isclass(member) and
      issubclass(member, cls) and
      member != cls
    ):
      members.append(member)

  return members
