import collections
import importlib
import inspect
import os

from sanic import Blueprint
from sanic import Sanic
from sanic.response import text

from core import config
from core import exceptions
from core import utils
from core.logging import logger
from core.models import User


_REQUIRED_MODULES = []


class Application:
  """Orchestrates the creation of fully initialized feature tree.

  Attributes:
    _feature_registry (dict): A dictionary which keeps a feature unique name and feature instance
      map.
    root (Feature): The root feature instance of the application.
  """
  _feature_registry = {}
  root = None

  @classmethod
  def get_feature(cls, name):
    """Returns a feature instance by its unique name.

    Args:
      name (str): The unique name of the feature.

    Returns:
      Feature: The feature registered by passed unique name.
    """
    return cls._feature_registry.get(name)

  @classmethod
  def register_feature(cls, feature):
    """Registers a feature instance to the feature registry.

    Args:
      feature (Feature): The feature instance to be registered to feature registry.
    """
    cls._feature_registry[feature.unique_name] = feature

  @classmethod
  def create_feature_tree(cls, feature_class, parent=None):
    """Creates feature tree for the application.

    Recursively creates instance for given feature class and its children without initializing.
    Injects each instance to appropriate position in the feature tree.

    Args:
      feature_class (type(Feature)): The feature class passed.
      parent (Feature): The parent feature instance.
    """
    feature = feature_class(parent=parent)
    if not feature.is_enabled:
      return

    cls.register_feature(feature)
    if feature.parent:
      feature.parent.add_child(feature)

    for child_class in feature.child_classes:
      cls.create_feature_tree(child_class, parent=feature)

  @classmethod
  def create_sanic_app(cls):
    """Creates feature tree and completes each feature lifecycle.

    - Creates feature tree
    - Initializes features (pre-order traversal)
    - Injects core pre-create middlewares
    - Runs pre-create lifehooks (pre-order traversal)
    - Injects core post-create middlewares
    - Configures Sanic
    - Runs post-create lifehooks (pre-order traversal)

    Returns:
      Sanic: The Sanic app object that would be used for running Sanic server.
    """
    cls.create_feature_tree(DPI)
    cls.root = cls.get_feature(DPI.name)
    cls.root.initialize()
    cls.root.inject_middlewares([
      InitializeContext,
    ])
    cls.root.pre_create()
    cls.root.inject_middlewares([
      Authenticate,
      TemplateDefaultContext,
      AddWildCardCorsHeaders,
    ])
    cls.root.configure_sanic()
    for feature in cls.root.children:
      cls.root.wrapper.blueprint(feature.wrapper)
    cls.root.post_create()

    logger.trace(f'App created: FEATURES {list(cls._feature_registry.keys())}')
    return cls.root.wrapper


class Feature:
  """An object that orchestrates feature configuration and holds all the information that shapes
  the routes, middlewares, and children features.

  Attributes:
    _name (str): The name of the feature. Default to snake and lower case name of the feature class.
    module_name (str): The module name of the feature if it's externally sourced.
      Default to feature name.
    inject_to (str): The name of feature which the feature will be injected as a child.
    url_prefix (str): The url prefix of the feature. Default to name of the feature.
    context (collections.OrderedDict): The context of the feature which is used to share data
      between features, also to be used internal feature operations.
  """
  _name = None
  module_name = None
  inject_to = None
  url_prefix = None
  context = collections.OrderedDict()

  def __init__(self, parent=None):
    """Initializes the feature.

     - Sets default values of class attributes.
     - Re-configure parent if the feature is intented to be injected.
     - Identifies children classes.

    Args:
      parent (Feature): The parent feature. Root feature doesn't have a parent.
    """
    self._name = None
    self._unique_name = None
    self._virtual_wrapper = None
    self._wrapper = None
    self.children = []
    self.parent = parent
    self.url_prefix = self.url_prefix or f"/{self.name.replace('_', '-')}"
    if self.module_name is None:
      self.module_name = f'{self.parent.module_name}.{self.name}' if self.parent else self.name

    if self.inject_to:
      inject_to_unique_name = f'{self.parent.unique_name}_{self.inject_to}'
      self.parent = Application.get_feature(inject_to_unique_name)

      if not self.parent:
        raise exceptions.ImproperlyConfigured(
          f'Cannot inject to feature ({self.inject_to}), it does not exists'
        )

    if self.parent:
      self._unique_name = f'{self.parent.unique_name}_{self.name}'

    self.child_classes = self.get_child_classes()

  @classmethod
  @property
  def name(cls):
    """The name of the feature.

    Defaults to snake case name of the feature class name.

    Returns:
      str: The name of the feature.
    """
    if cls._name is None:
      cls._name = utils.camel_to_snake(cls.__name__)

    return cls._name

  @property
  def unique_name(self):
    """The unique name of the feature.

    The name of the feature cannot be unique if same feature is injected more than once inside of
    a single application. It's structured by using unique name of each feature on the path.
    """
    if self._unique_name is None:
      self._unique_name = self.name

    return self._unique_name

  @property
  def wrapper(self):
    """Read-only property of private property _wrapper.
    Root feature wrapper: Sanic
    Middle nodes wrapper: BlueprintGroup
    Leaf nodes wrapper: Blueprint

    Returns:
      Sanic, Blueprint, BlueprintGroup: The Sanic wrapper of the feature. Wrapper changes depends
        on whether feature is root, middle node, or leaf node.
    """
    return self._wrapper

  @property
  def virtual_wrapper(self):
    """Read-only property of private property _virtual_wrapper.

    Virtual wrapper is being used to add routes to middle nodes. Because Sanic won't allow adding
    routes to BlueprintGroups. That's why, only middle nodes have virtual wrapper.

    Returns:
      Blueprint: The Sanic Blueprint.
    """
    return self._virtual_wrapper

  @property
  def is_root(self):
    """Returns whether feature is root or not."""
    return not self.parent

  @property
  def is_enabled(self):
    """Returns whether feature is enabled or not."""
    return int(utils.getenv(f'{self.unique_name.upper()}_ENABLED', default=1))

  @property
  def json(self):
    """Returns JSON representation of the feature."""
    return {
      'name': self.name,
      'unique_name': self.unique_name,
      'module_name': self.module_name,
      'url_prefix': self.url_prefix,
      'inject_to': self.inject_to,
      'parent': self.parent.unique_name if self.parent else None
    }

  def initialize(self):
    """Initializes the feature.

    Runs recursively (pre-order traversal) to initalize all children feature.
    Imports init lifehook, config module of the feature, and creates appropriate Sanic wrapper.

    Returns:
      None
    """
    logger.trace(f'Feature {self.unique_name}: Initializing {self.json}')
    self.import_init()
    self.import_config()
    logger.trace(f'Feature {self.unique_name}: Children list {self.children}')
    for feature in self.children:
      feature.initialize()

    self.create_wrapper()
    logger.trace(f'Feature {self.unique_name}: Initialized {self.json}')

  def create_wrapper(self):
    """Creates sanic wrapper for the feature.

    - If feature is root, Sanic app will be the wrapper.
    - If feature is middle node, BlueprintGroup will be the wrapper and
      Blueprint will be the virtual wrapper.
    - If feature is leaf node, Blueprint will be the wrapper.

    Returns:
      None
    """
    if self.is_root:
      self._wrapper = Sanic(self.unique_name)

    elif self.children:
      # Creating virtual wrapper to have top '/' level routes for features with children
      self._virtual_wrapper = Blueprint(f'{self.unique_name}-virtual', url_prefix='')
      self._wrapper = Blueprint.group(
        self._virtual_wrapper,
        *[feature.wrapper for feature in self.children],
        url_prefix=self.url_prefix
      )
    else:
      self._wrapper = Blueprint(self.unique_name, url_prefix=self.url_prefix)

  def configure_sanic(self):
    """Configures Sanic objects recursively for every feature on the feature tree.
    (pre-order traversal)

    - Import and inject middlewares to wrapper.
    - Import and inject routes to wrapper or virtual wrapper.

    Returns:
      None
    """
    middlewares = self.import_middlewares()
    routes = self.import_routes()

    self.inject_middlewares(middlewares)
    routes = routes + [MiddlewareTest] if config.is_test() else routes
    self.inject_routes(routes, self.virtual_wrapper or self.wrapper)
    for feature in self.children:
      feature.configure_sanic()

  def pre_create(self):
    """Runs pre create lifehooks recursively for every feature on the feature tree.

    (pre-order traversal)

    Returns:
      None
    """
    self.import_pre_create()
    for feature in self.children:
      feature.pre_create()

  def post_create(self):
    """Runs post create lifehooks recursively for every feature on the feature tree.

    (pre-order traversal)

    Returns:
      None
    """
    self.import_post_create()
    for feature in self.children:
      feature.post_create()

  def inject_middleware(self, middleware):
    """Injects middleware to the feature's wrapper if it's active."""
    if not middleware.ACTIVE:
      return

    logger.trace(f'Feature {self.unique_name}: Injecting middleware {middleware.log()}')
    if middleware.is_request:
      self.wrapper.on_request(middleware.default_function)
    elif middleware.is_response:
      self.wrapper.on_response(middleware.default_function)

  def inject_middlewares(self, middlewares):
    """Injects identified middlewares to the feature's wrapper."""
    for middleware in middlewares:
      self.inject_middleware(middleware)

  def inject_route(self, route, wrapper):
    """Injects route to the feature's wrapper if it's active."""
    if not route.ACTIVE:
      return

    logger.trace(
      f'Feature {self.unique_name}: injecting route {route.log()}'
    )
    wrapper.add_route(
      route.default_function,
      route.path,
      methods=route.methods,
      ctx_allow_unauthenticated=route.allow_unauthenticated,
      **route.context
    )

  def inject_routes(self, routes, wrapper):
    """Injects identified routes to the feature's wrapper."""
    for route in routes:
      self.inject_route(route, wrapper)

  def import_init(self):
    """Runs init lifehook."""
    logger.trace(f'Feature {self.unique_name}: Running init')
    self.import_child_module('lifehooks.init')

  def add_child(self, child):
    """Adds the given feature to the children list."""
    self.children.append(child)

  def get_child_classes(self):
    """Imports children module and identify all occurances of Feature class as a child.

    Return:
      list<Feature>: The children features.
    """
    children_module = self.import_child_module('children')
    return utils.get_members(children_module, Feature)

  def import_config(self):
    """Imports feature configuration module."""
    self.config = self.import_child_module('config')
    logger.trace(f'Feature {self.unique_name}: Config {self.config}')

  def import_routes(self):
    """Import routes module and identify all occurances of Route class as a route.

    Returns:
      list<Route>: The list of routes defined for the feature.
    """
    routes = self.import_child_module('routes')
    if not routes:
      return []

    return utils.get_members(routes, Route)

  def import_middlewares(self):
    """Import middlewares module and identify all occurances of Middleware class as a route.

    Returns:
      list<Middleware>: The list of routes defined for the feature.
    """
    middlewares = self.import_child_module('middlewares')
    if not middlewares:
      return []

    return utils.get_members(middlewares, OnRequest) + utils.get_members(middlewares, OnResponse)

  def import_pre_create(self):
    """Imports pre create lifehook module."""
    self.import_child_module('lifehooks.pre_create')

  def import_post_create(self):
    """Imports post create lifehook module."""
    self.import_child_module('lifehooks.post_create')

  def import_child_module(self, child_module_name):
    """A helper to dynamically import relatively the feature with given child."""
    module_name = f'{self.module_name}.{child_module_name}'
    try:
      return importlib.import_module(module_name)
    except ModuleNotFoundError as e:
      if module_name in _REQUIRED_MODULES:
        raise exceptions.ImproperlyConfigured(f'''
          {module_name} must be implemented! ({module_name}) \n
          Exception: {e}
        ''')

    except Exception as e:
      raise exceptions.ImproperlyConfigured(f'''
        Something went wrong loading module ({module_name}):
        Exception: {e}
      ''')


class DPI(Feature):
  """The root feature."""
  url_prefix = '/'


class Base:
  """A helper base that defines required function and be able to return the member of the class.

  Attribute:
    DEFAULT_FUNCTION_NAME (str): The name of the default function.
  """
  DEFAULT_FUNCTION_NAME = 'default'

  @classmethod
  def get_required_member(cls, member_name):
    """Returns the member of the class named as DEFAULT_FUNCTION_NAME."""
    try:
      if not callable(cls.__dict__[member_name]):
        raise exceptions.ImproperlyConfigured(
          f'{cls.__name__} {member_name} method must be callable'
        )
    except KeyError:
      raise exceptions.ImproperlyConfigured(
        f'{cls.__name__} {member_name} method must be implemented'
      )
    return cls.__dict__[member_name]

  @classmethod
  @property
  def default_function(cls):
    """Returns the default function object for the helper."""
    return cls.get_required_member(member_name=cls.DEFAULT_FUNCTION_NAME)


class Route(Base):
  """Route definition class.

  Configures an endpoint.

  Attributes:
    DEFAULT_FUNCTION_NAME: The name of the default function which will be run when endpoint called.
    ACTIVE (bool): Whether the endpoint is active or not.
    PATH (str): The url path of the endpoint. Relative to it's position in the feature tree.
    METHODS (list<str>): A list of allowed HTTP methods for the endpoint.
    ALLOW_UNAUTHENTICATED (bool): Whether the endpoint should go through authentication or not.
    context (dict): The context of the route which can be used inside handler function on runtime.
  """
  DEFAULT_FUNCTION_NAME = 'handler'
  ACTIVE = True
  PATH = '/'
  METHODS = ['GET']
  ALLOW_UNAUTHENTICATED = False
  context = {}

  def __new__(cls):
    """Checks if required default function is implemented."""
    handler_args = inspect.getargspec(cls.default_func).args
    if len(handler_args) < 1:
      raise exceptions.ImproperlyConfigured(
        f'{cls.__name__} {cls.DEFAULT_FUNCTION_NAME} function '
        'must at least take "request" as a parameter'
      )

    return super().__new__(cls)

  @classmethod
  def log(cls):
    """JSON representation of the route."""
    return {
      'NAME': cls.__name__,
      'ACTIVE': cls.ACTIVE,
      'PATH': cls.PATH,
      'METHODS': cls.METHODS,
      'ALLOW_UNAUTHENTICATED': cls.ALLOW_UNAUTHENTICATED,
      'context': cls.context,
    }

  @classmethod
  @property
  def methods(cls):
    """Returns HTTP Methods that the route allows."""
    return cls.METHODS + ['OPTIONS']

  @classmethod
  @property
  def path(cls):
    """Returns URL path of the route."""
    return cls.PATH

  @classmethod
  @property
  def template_path(cls):
    """Returns template path of the route based on the file location of the route."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')

  @classmethod
  @property
  def allow_unauthenticated(cls):
    """Returns whether or not endpoint handler should go through the authentication or not."""
    return cls.ALLOW_UNAUTHENTICATED


class Middleware(Base):
  """Middleware definition class.

  Configures a middleware.

  Attributes:
    DEFAULT_FUNCTION_NAME: The name of the default function which will be run as a middleware.
    ACTIVE (bool): Whether the middleware is active or not.
    TYPE (str): The type of the middleware. Determines whether the middleware should run on request
      time or response time. It can only be one of the CHOICES[request, response].
  """
  DEFAULT_FUNCTION_NAME = 'middleware'
  ACTIVE = True
  TYPE = None
  CHOICES = ['request', 'response']

  def __new__(cls):
    """Checks if the middleware properly configured.


    - TYPE should be one of the CHOICES.
    - On request middlewares should accept single parameter (request) to default function.
    - On response middlewares should accept two parameters (request, response) to default function.
    """
    middleware_type = getattr(cls, 'TYPE')
    if middleware_type is None:
      raise exceptions.ImproperlyConfigured(f'''
        {cls.__name__} TYPE must be defined. \n
        Choices: {cls.CHOICES}
     ''')

    if middleware_type not in cls.CHOICES:
      raise exceptions.ImproperlyConfigured(f'{cls.__name__} TYPE must be one of {cls.CHOICES}')

    middleware_args = inspect.getargspec(cls.default_func).args
    if cls.TYPE == 'request' and len(middleware_args) != 1:
      raise exceptions.ImproperlyConfigured(
        f'{cls.__name__} {cls.DEFAULT_FUNCTION_NAME} method '
        'must only take request as a parameter'
      )

    if cls.TYPE == 'response' and len(middleware_args) != 2:
      raise exceptions.ImproperlyConfigured(
        f'{cls.__name__} {cls.DEFAULT_FUNCTION_NAME} method must only take '
        'request and response as a parameter'
      )

    return super().__new__(cls)

  @classmethod
  def log(cls):
    """JSON representation of the middleware."""
    return {
      'NAME': cls.__name__,
      'TYPE': cls.TYPE,
      'ACTIVE': cls.ACTIVE,
    }

  @classmethod
  @property
  def is_request(cls):
    """Returns whether middleware type is on request."""
    return cls.TYPE == 'request'

  @classmethod
  @property
  def is_response(cls):
    """Returns whether middleware type is on response."""
    return cls.TYPE == 'response'


class OnRequest(Middleware):
  """Middleware definition class for request type."""
  TYPE = 'request'


class OnResponse(Middleware):
  """Middleware definition class for response type."""
  TYPE = 'response'


def initialize_request_context(request):
  """Initializes request context with initial values."""
  request.ctx.user = None
  request.ctx.template_context = {}
  request.ctx.path = request.path
  request.ctx.allow_unauthenticated = (
    (
      request.route and
      request.route.ctx and
      hasattr(request.route.ctx, 'allow_unauthenticated') and
      request.route.ctx.allow_unauthenticated
    )
    or any(request.ctx.path.startswith(allowed) for allowed in config.ALLOW_UNAUTHENTICATED)
  )
  request.ctx.authenticated = False


class InitializeContext(OnRequest):
  """A request type middleware initializes request context with initial values.

  Injected as a core pre-create filter, has the #1 priority in terms of run time.
  """

  async def middleware(request):
    initialize_request_context(request)


class Authenticate(OnRequest):
  """Authentication middleware."""

  async def middleware(request):
    """Authenticates the request.

    - Checks request context if route is allowed without authentication.
    - Checks request context if the request is already.
    - Seeks for access_token parameter as a request parameter and fetches user with the given
      access_token.
    - Marks request context's authenticated parameter.
    """
    if request.ctx.allow_unauthenticated or request.ctx.authenticated:
      return

    access_token = request.args.get('access_token')
    if access_token:
      request.ctx.user = await User.get_by_access_token(access_token)

    if not request.ctx.user:
      raise exceptions.Forbidden('Not authenticated')

    request.ctx.authenticated = True


class TemplateDefaultContext(OnRequest):
  """Initializes the template context with initial values.

  Template context is being used to manipulate template content before rendering. To take advantage
  of template context, route must define templated_response decorator.

  Any parameter defined in context, can be accessible on any HTML file by referencing like
  template.context.<VAR_NAME>

  i.e. index.html
    const __ACCESS_TOKEN__ = template.context.ACCESS_TOKEN

  """

  async def middleware(request):
    request.ctx.template_context.update({
      'ACCESS_TOKEN': request.ctx.user.access_token if request.ctx.user else None
    })


class AddWildCardCorsHeaders(OnResponse):
  """Adds localhost cors headers for webpack dev server."""
  ACTIVE = config.REMOTE_LOCALHOST or config.is_dev()

  async def middleware(request, response):
    headers = utils.get_cors_headers(
      allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allow_origins=['http://localhost:8087'],
    )
    response.headers.extend(headers)


class MiddlewareTest(Route):
  """A sample middleware to be used for testing suite."""
  ACTIVE = config.is_test()
  PATH = '/--middleware-test--'
  METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

  def handler(request):
    import jsonpickle
    return text(jsonpickle.encode(request.ctx))
