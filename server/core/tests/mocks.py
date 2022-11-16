import collections

from core.sanic import Feature
from core.sanic import OnRequest
from core.sanic import OnResponse
from core.sanic import Route
from core.sanic import initialize_request_context


class MockSanicRoute():

  def __init__(self):
    self.ctx = collections.OrderedDict()


class MockSanicRequest():

  def __init__(self, path):
    self.ctx = collections.OrderedDict()
    self.path = path
    self.route = MockSanicRoute()
    initialize_request_context(self)


class MockNotActiveRoute(Route):
  ACTIVE = False

  async def handler(request):
    pass


class MockRoute(Route):
  async def handler(request):
    pass


class MockNotActiveMiddleware(OnRequest):
  ACTIVE = False

  async def middleware(request):
    pass


class MockOnRequest(OnRequest):
  async def middleware(request):
    pass


class MockOnResponse(OnResponse):
  async def middleware(request):
    pass


class MockMembers:
  ON_REQUEST = OnRequest
  ON_RESPONSE = OnResponse
  ROUTE = Route
  FEATURE = Feature

  @staticmethod
  def get_members(module, cls):
    match cls:
      case MockMembers.ON_REQUEST:
        return [MockOnRequest]

      case MockMembers.ON_RESPONSE:
        return [MockOnResponse]

      case MockMembers.ROUTE:
        return [MockRoute]

      case MockMembers.FEATURE:
        return [Sourced]


class Sourced(Feature):
  pass


class SourcedUnderInjected(Feature):
  pass


class SourcedInjectedToSourced(Feature):
  inject_to = 'sourced'


class ModuleNamed(Feature):
  module_name = 'core.features.module_sample_one'


class ModuleNamedInjectedToModuleNamed(Feature):
  module_name = 'core.features.module_sample_two'
  inject_to = 'module_named'


class SourcedInjectedToModuleNamed(Feature):
  inject_to = 'module_named'


class ModuleNamedInjectedToSourced(Feature):
  module_name = 'core.features.module_sample_three'
  inject_to = 'sourced'


class InjectedToInjected(Feature):
  inject_to = 'module_named_sourced_injected_to_module_named'


class ModuleNamedInjectedToInjected(Feature):
  module_name = 'core.features.module_sample_four'
  inject_to = 'module_named_module_named_injected_to_module_named'
