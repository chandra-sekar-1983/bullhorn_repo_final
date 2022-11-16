import unittest

from unittest import mock
from unittest.mock import call
from unittest.mock import patch

from core.sanic import Application
from core.sanic import DPI
from core.sanic import Feature
from core.tests import mocks


class TestApplication(unittest.TestCase):
  maxDiff = None

  @patch.object(
    Feature, 'get_child_classes',
    side_effect=[
      [
        mocks.Sourced, mocks.SourcedInjectedToSourced, mocks.ModuleNamed,
        mocks.ModuleNamedInjectedToModuleNamed, mocks.SourcedInjectedToModuleNamed,
        mocks.ModuleNamedInjectedToSourced, mocks.InjectedToInjected,
        mocks.ModuleNamedInjectedToInjected
      ],
      [], [], [], [], [], [], [], []
    ]
  )
  def test_create_feature_tree(self, mock_get_child_classes):
    Application.create_feature_tree(DPI)
    self.assertEqual(
      ['dpi', 'dpi_sourced', 'dpi_sourced_sourced_injected_to_sourced', 'dpi_module_named',
       'dpi_module_named_module_named_injected_to_module_named',
       'dpi_module_named_sourced_injected_to_module_named',
       'dpi_sourced_module_named_injected_to_sourced',
       'dpi_module_named_sourced_injected_to_module_named_injected_to_injected',
       'dpi_module_named_module_named_injected_to_module_named_module_named_injected_to_injected'],
      list(Application._feature_registry.keys())
    )

    root = Application.get_feature('dpi')
    self.assertEqual(
      ['sourced', 'module_named'],
      [child.name for child in root.children]
    )

    sourced = Application.get_feature('dpi_sourced')
    self.assertIsNotNone(sourced)
    self.assertEqual(
      ['sourced_injected_to_sourced', 'module_named_injected_to_sourced'],
      [child.name for child in sourced.children]
    )

    sourced_injected_to_sourced = Application.get_feature('dpi_sourced_sourced_injected_to_sourced')
    self.assertIsNotNone(sourced_injected_to_sourced)
    self.assertEqual(
      [],
      [child.name for child in sourced_injected_to_sourced.children]
    )

    module_named = Application.get_feature('dpi_module_named')
    self.assertIsNotNone(module_named)
    self.assertEqual(
      ['module_named_injected_to_module_named', 'sourced_injected_to_module_named'],
      [child.name for child in module_named.children]
    )

    module_named_injected_to_module_named = Application.get_feature(
      'dpi_module_named_module_named_injected_to_module_named'
    )
    self.assertIsNotNone(module_named_injected_to_module_named)
    self.assertEqual(
      ['module_named_injected_to_injected'],
      [child.name for child in module_named_injected_to_module_named.children]
    )

    sourced_injected_to_module_named = Application.get_feature(
      'dpi_module_named_sourced_injected_to_module_named'
    )
    self.assertIsNotNone(sourced_injected_to_module_named)
    self.assertEqual(
      ['injected_to_injected'],
      [child.name for child in sourced_injected_to_module_named.children]
    )

    module_named_injected_to_sourced = Application.get_feature(
      'dpi_sourced_module_named_injected_to_sourced',
    )
    self.assertIsNotNone(module_named_injected_to_sourced)
    self.assertEqual(
      [],
      [child.name for child in module_named_injected_to_sourced.children]
    )

    injected_to_injected = Application.get_feature(
      'dpi_module_named_sourced_injected_to_module_named_injected_to_injected'
    )
    self.assertIsNotNone(injected_to_injected)
    self.assertEqual(
      [],
      [child.name for child in injected_to_injected.children]
    )

    module_named_injected_to_injected = Application.get_feature(
      'dpi_module_named_module_named_injected_to_module_named_module_named_injected_to_injected'
    )
    self.assertIsNotNone(module_named_injected_to_injected)
    self.assertEqual(
      [],
      [child.name for child in module_named_injected_to_injected.children]
    )

  @patch.object(
    Feature,
    'import_child_module',
    side_effect=lambda x, *args: mock.MagicMock(__name__=x)
  )
  @patch.object(
    Feature,
    'get_child_classes',
    side_effect=[
      [
        mocks.Sourced, mocks.SourcedInjectedToSourced, mocks.ModuleNamed,
        mocks.ModuleNamedInjectedToModuleNamed, mocks.SourcedInjectedToModuleNamed,
        mocks.ModuleNamedInjectedToSourced, mocks.InjectedToInjected,
        mocks.ModuleNamedInjectedToInjected
      ],
      [], [], [], [], [], [], [], []
    ]
  )
  @patch('core.sanic.Sanic', return_value=mock.MagicMock())
  @patch('core.sanic.Blueprint', return_value=mock.MagicMock())
  def test_create_sanic_app(self, mock_blueprint, mock_sanic, mock_get_child_classes, mock_import):
    Application.create_feature_tree(DPI)
    root = Application.get_feature('dpi')
    sourced = Application.get_feature('dpi_sourced')
    self.assertDictEqual(
      {
        'name': 'sourced',
        'unique_name': f'{root.unique_name}_sourced',
        'module_name': f'{root.module_name}.sourced',
        'url_prefix': '/sourced',
        'inject_to': None,
        'parent': root.unique_name,
      },
      sourced.json
    )

    sourced_injected_to_sourced = Application.get_feature('dpi_sourced_sourced_injected_to_sourced')
    self.assertDictEqual(
      {
        'name': 'sourced_injected_to_sourced',
        'unique_name': f'{sourced.unique_name}_sourced_injected_to_sourced',
        'module_name': f'{root.module_name}.sourced_injected_to_sourced',
        'url_prefix': '/sourced-injected-to-sourced',
        'inject_to': 'sourced',
        'parent': sourced.unique_name,
      },
      sourced_injected_to_sourced.json
    )

    module_named = Application.get_feature('dpi_module_named')
    self.assertDictEqual(
      {
        'name': 'module_named',
        'unique_name': f'{root.unique_name}_module_named',
        'module_name': 'core.features.module_sample_one',
        'url_prefix': '/module-named',
        'inject_to': None,
        'parent': root.unique_name,
      },
      module_named.json
    )

    module_named_injected_to_module_named = Application.get_feature(
      'dpi_module_named_module_named_injected_to_module_named'
    )

    self.assertDictEqual(
      {
        'name': 'module_named_injected_to_module_named',
        'unique_name': f'{module_named.unique_name}_module_named_injected_to_module_named',
        'module_name': 'core.features.module_sample_two',
        'url_prefix': '/module-named-injected-to-module-named',
        'inject_to': 'module_named',
        'parent': module_named.unique_name,
      },
      module_named_injected_to_module_named.json
    )

    sourced_injected_to_module_named = Application.get_feature(
      'dpi_module_named_sourced_injected_to_module_named'
    )
    self.assertDictEqual(
      {
        'name': 'sourced_injected_to_module_named',
        'unique_name': f'{module_named.unique_name}_sourced_injected_to_module_named',
        'module_name': f'{root.module_name}.sourced_injected_to_module_named',
        'url_prefix': '/sourced-injected-to-module-named',
        'inject_to': 'module_named',
        'parent': module_named.unique_name,
      },
      sourced_injected_to_module_named.json
    )

    module_named_injected_to_sourced = Application.get_feature(
      'dpi_sourced_module_named_injected_to_sourced'
    )
    self.assertDictEqual(
      {
        'name': 'module_named_injected_to_sourced',
        'unique_name': f'{sourced.unique_name}_module_named_injected_to_sourced',
        'module_name': 'core.features.module_sample_three',
        'url_prefix': '/module-named-injected-to-sourced',
        'inject_to': 'sourced',
        'parent': sourced.unique_name,
      },
      module_named_injected_to_sourced.json
    )

    injected_to_injected = Application.get_feature(
      'dpi_module_named_sourced_injected_to_module_named_injected_to_injected'
    )
    self.assertDictEqual(
      {
        'name': 'injected_to_injected',
        'unique_name': f'{sourced_injected_to_module_named.unique_name}_injected_to_injected',
        'module_name': f'{root.module_name}.injected_to_injected',
        'url_prefix': '/injected-to-injected',
        'inject_to': 'module_named_sourced_injected_to_module_named',
        'parent': sourced_injected_to_module_named.unique_name,
      },
      injected_to_injected.json
    )

    module_named_injected_to_injected = Application.get_feature(
      'dpi_module_named_module_named_injected_to_module_named_module_named_injected_to_injected'
    )
    self.assertDictEqual(
      {
        'name': 'module_named_injected_to_injected',
        'unique_name': (f'{module_named_injected_to_module_named.unique_name}'
                        '_module_named_injected_to_injected'),
        'module_name': 'core.features.module_sample_four',
        'url_prefix': '/module-named-injected-to-injected',
        'inject_to': 'module_named_module_named_injected_to_module_named',
        'parent': module_named_injected_to_module_named.unique_name,
      },
      module_named_injected_to_injected.json
    )

    # Test initialize
    mock_import.reset_mock()
    root.initialize()
    mock_import.assert_has_calls([
      call('lifehooks.init'), call('config'),
      call('lifehooks.init'), call('config'),
      call('lifehooks.init'), call('config'),
      call('lifehooks.init'), call('config'),
      call('lifehooks.init'), call('config'),
      call('lifehooks.init'), call('config'),
      call('lifehooks.init'), call('config'),
      call('lifehooks.init'), call('config'),
      call('lifehooks.init'), call('config'),
    ], any_order=True)
    self.assertEqual(18, mock_import.call_count)
    mock_sanic.assert_called_with(root.unique_name)
    mock_blueprint.assert_has_calls([
      call('dpi_sourced_sourced_injected_to_sourced', url_prefix='/sourced-injected-to-sourced'),
      call(
        'dpi_sourced_module_named_injected_to_sourced',
        url_prefix='/module-named-injected-to-sourced'
      ),
      call('dpi_sourced-virtual', url_prefix=''),
      call(
        'dpi_module_named_module_named_injected_to_module_named_module_named_injected_to_injected',
        url_prefix='/module-named-injected-to-injected'
      ),
      call('dpi_module_named_module_named_injected_to_module_named-virtual', url_prefix=''),
      call(
        'dpi_module_named_sourced_injected_to_module_named_injected_to_injected',
        url_prefix='/injected-to-injected'
      ),
      call('dpi_module_named_sourced_injected_to_module_named-virtual', url_prefix=''),
      call('dpi_module_named-virtual', url_prefix='')
    ], any_order=True)
    self.assertEqual(8, mock_blueprint.call_count)

    mock_blueprint.group.assert_has_calls([
      call(
        sourced._virtual_wrapper,
        sourced_injected_to_sourced.wrapper,
        module_named_injected_to_sourced.wrapper,
        url_prefix='/sourced'
      ),
      call(
        module_named_injected_to_module_named._virtual_wrapper,
        module_named_injected_to_injected.wrapper,
        url_prefix='/module-named-injected-to-module-named'
      ),
      call(
        sourced_injected_to_module_named._virtual_wrapper,
        injected_to_injected.wrapper,
        url_prefix='/sourced-injected-to-module-named'
      ),
      call(
        module_named._virtual_wrapper,
        module_named_injected_to_module_named.wrapper,
        sourced_injected_to_module_named.wrapper,
        url_prefix='/module-named'
      ),
    ], any_order=True)
    self.assertEqual(4, mock_blueprint.group.call_count)

    # Test pre create lifehook
    mock_import.reset_mock()
    root.pre_create()
    mock_import.assert_has_calls([call('lifehooks.pre_create'), call('lifehooks.pre_create'),
                                  call('lifehooks.pre_create'), call('lifehooks.pre_create'),
                                  call('lifehooks.pre_create'), call('lifehooks.pre_create'),
                                  call('lifehooks.pre_create'), call('lifehooks.pre_create'),
                                  call('lifehooks.pre_create')], any_order=True)
    self.assertEqual(9, mock_import.call_count)

    # Test configure sanic
    mock_import.reset_mock()
    with patch('core.utils.get_members', side_effect=mocks.MockMembers.get_members):
      root.configure_sanic()

    mock_import.assert_has_calls([call('middlewares'), call('routes'),
                                  call('middlewares'), call('routes'),
                                  call('middlewares'), call('routes'),
                                  call('middlewares'), call('routes'),
                                  call('middlewares'), call('routes'),
                                  call('middlewares'), call('routes'),
                                  call('middlewares'), call('routes'),
                                  call('middlewares'), call('routes'),
                                  call('middlewares'), call('routes')], any_order=True)
    self.assertEqual(18, mock_import.call_count)
    mock_sanic().assert_has_calls([
      call.on_request(mocks.MockOnRequest.middleware),
      call.on_response(mocks.MockOnResponse.middleware),
      call.add_route(mocks.MockRoute.handler, mocks.MockRoute.PATH,
                     methods=mocks.MockRoute.METHODS + ['OPTIONS'],
                     ctx_allow_unauthenticated=mocks.MockRoute.ALLOW_UNAUTHENTICATED)
    ])
    self.assertEqual(1, mock_sanic().on_request.call_count)
    self.assertEqual(1, mock_sanic().on_response.call_count)
    self.assertEqual(2, mock_sanic().add_route.call_count)
    self.assertEqual(4, mock_blueprint().on_request.call_count)
    self.assertEqual(4, mock_blueprint().on_response.call_count)
    self.assertEqual(16, mock_blueprint().add_route.call_count)
    self.assertEqual(4, mock_blueprint.group().on_request.call_count)
    self.assertEqual(4, mock_blueprint.group().on_response.call_count)
    self.assertEqual(0, mock_blueprint.group().add_route.call_count)


class TestFeature(unittest.TestCase):
  maxDiff = None

  def setUp(self):
    self.root = DPI()

  @patch('importlib.import_module')
  def test_import_child_module(self, mock_import):
    self.root.import_child_module('module_name')
    mock_import.assert_called_with(f'{self.root.module_name}.module_name')

    mock_import.side_effect = ModuleNotFoundError
    # Check ModuleNotFoundError is handled
    self.root.import_child_module('module_name')

    mock_import.side_effect = Exception
    with self.assertRaises(Exception):
      self.root.import_child_module('module_name')

  @patch.object(Feature, 'import_child_module', return_value=None)
  def test_import_init(self, mock_import):
    self.root.import_init()
    mock_import.assert_called_with('lifehooks.init')

  @patch.object(Feature, 'import_child_module', return_value=None)
  def test_import_config(self, mock_import):
    self.root.import_config()
    mock_import.assert_called_with('config')

  @patch.object(Feature, 'import_child_module', return_value=None)
  def test_import_pre_create(self, mock_import):
    self.root.import_pre_create()
    mock_import.assert_called_with('lifehooks.pre_create')

  @patch.object(Feature, 'import_child_module', return_value=None)
  def test_import_post_create(self, mock_import):
    self.root.import_post_create()
    mock_import.assert_called_with('lifehooks.post_create')

  @patch.object(Feature, 'import_child_module')
  @patch('core.utils.get_members', side_effect=mocks.MockMembers.get_members)
  def test_get_child_classes(self, mock_get_members, mock_import):
    mock_module = mock.MagicMock()
    mock_import.return_value = mock_module
    self.root.get_child_classes()
    mock_import.assert_called_with('children')
    mock_get_members.assert_called_with(mock_module, Feature)

  def test_add_child(self):
    self.root.add_child(mocks.Sourced)
    self.assertEqual(mocks.Sourced, self.root.children[0])

  @patch.object(Feature, 'import_child_module', return_value=None)
  @patch.object(Feature, 'create_wrapper', return_value=None)
  def test_initialize(self, mock_create_wrapper, mock_import):
    self.root.initialize()
    mock_import.assert_has_calls([call('lifehooks.init'), call('config')])
    mock_create_wrapper.assert_called()

  @patch('core.sanic.Sanic', return_value=mock.MagicMock())
  def test_root_create_wrapper(self, mock_sanic):
    self.root.create_wrapper()
    mock_sanic.assert_called_with(self.root.unique_name)

  @patch('core.sanic.Blueprint', return_value=mock.MagicMock())
  def test_parent_create_wrapper(self, mock_blueprint):
    parent = mocks.Sourced(parent=self.root)
    leaf = mocks.SourcedUnderInjected(parent=parent)
    self.root.children = [parent]
    parent.children = [leaf]
    parent.create_wrapper()
    mock_blueprint.assert_has_calls([
      call(f'{parent.unique_name}-virtual', url_prefix=''),
      call.group(parent._virtual_wrapper, leaf.wrapper, url_prefix=parent.url_prefix)
    ])

  @patch('core.sanic.Blueprint', return_value=mock.MagicMock())
  def test_leaf_create_wrapper(self, mock_blueprint):
    leaf = mocks.Sourced(parent=self.root)
    self.root.children = [leaf]
    leaf.create_wrapper()
    mock_blueprint.assert_called_with(leaf.unique_name, url_prefix=leaf.url_prefix)

  @patch.object(Feature, 'import_child_module', return_value=None)
  def test_pre_create(self, mock_import):
    self.root.pre_create()
    mock_import.assert_called_with('lifehooks.pre_create')

  @patch.object(Feature, 'import_child_module', return_value=None)
  def test_post_create(self, mock_import):
    self.root.post_create()
    mock_import.assert_called_with('lifehooks.post_create')

  def test_inject_route(self):
    wrapper = mock.MagicMock()
    self.root.inject_route(mocks.MockNotActiveRoute, wrapper)
    wrapper.assert_not_called()

    route = mocks.MockRoute
    self.root.inject_route(route, wrapper)
    wrapper.add_route.assert_called_with(
      route.default_function,
      route.path,
      methods=route.methods,
      ctx_allow_unauthenticated=route.allow_unauthenticated,
      **route.context
    )

  @patch.object(Feature, 'inject_route')
  def test_inject_routes(self, mock_inject_route):
    wrapper = mock.MagicMock()
    self.root.inject_routes([mocks.MockRoute], wrapper)
    mock_inject_route.assert_any_call(mocks.MockRoute, wrapper)

  @patch.object(Feature, 'wrapper')
  def test_inject_middleware(self, mock_wrapper):
    self.root.inject_middleware(mocks.MockNotActiveMiddleware)
    mock_wrapper.on_response.assert_not_called()
    mock_wrapper.on_request.assert_not_called()

    self.root.inject_middleware(mocks.MockOnRequest)
    mock_wrapper.on_request.assert_called_with(mocks.MockOnRequest.default_function)

    self.root.inject_middleware(mocks.MockOnResponse)
    mock_wrapper.on_response.assert_called_with(mocks.MockOnResponse.default_function)

  @patch.object(Feature, 'inject_middleware')
  def test_inject_middlewares(self, mock_inject_middleware):
    middlewares = [mocks.MockOnRequest, mocks.MockOnResponse]
    self.root.inject_middlewares(middlewares)
    mock_inject_middleware.assert_has_calls([call(middleware) for middleware in middlewares])

  @patch.object(Feature, 'import_child_module', return_value=None)
  def test_configure_sanic(self, mock_import):
    self.root._wrapper = mock.MagicMock()
    self.root.configure_sanic()
    mock_import.assert_has_calls([call('middlewares'), call('routes')])
