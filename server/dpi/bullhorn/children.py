"""Contains information about any children feature defined.

Examples:

  # Defined directly in source code.
  class Sourced(Feature):
    pass

  # Defined directly in source code, injected as a child to source feature.
  class SourcedInjectedToSourced(Feature):
    inject_to = 'sourced'

  # Defined as a core feature.
  class ModuleNamed(Feature):
    module_name = 'core.features.module_sample_one'

  # Defined as a core feature injected to a core feature.
  class ModuleNamedInjectedToModuleNamed(Feature):
    module_name = 'core.features.module_sample_two'
    inject_to = 'module_named'

  # Defined directly in source code, injected to a core feature.
  class SourcedInjectedToModuleNamed(Feature):
    inject_to = 'module_named'

  # Defined as a core feature, injected to source feature.
  class ModuleNamedInjectedToSourced(Feature):
    module_name = 'core.features.module_sample_three'
    inject_to = 'sourced'
"""
from core.sanic import Feature


class Api(Feature):
  pass
