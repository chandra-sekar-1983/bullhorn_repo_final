from unittest.mock import patch

from core.features.dialpad import config
from core.features.dialpad import middlewares
from core.features.dialpad import utils
from core.features.dialpad.models import DialpadUser
from core.models import User
from core.tests import base
from core.tests import mocks


class TestDialpadMiddleware(base.TransactionalClassTestCase):

  async def asyncSetUp(self):
    await super().asyncSetUp()
    self.user = await User.create()
    self.dialpad_user = await DialpadUser.create(
      user=self.user, dialpad_user_id='1', dialpad_api_key='test-api-key'
    )

  def setUp(self):
    super().setUp()
    self.request = mocks.MockSanicRequest('/dialpad')

  async def test_add_dialpad_user(self):
    self.request.ctx.user = self.user
    self.request.ctx.authenticated = True
    await middlewares.AddDialpadUser.middleware(self.request)
    self.assertEqual(self.dialpad_user.id, self.request.ctx.dialpad_user.id)

    with patch.object(DialpadUser, 'get_by_id') as mock_dialpad_user:
      await middlewares.AddDialpadUser.middleware(self.request)
      mock_dialpad_user.assert_not_called()

  async def test_add_dialpad_client(self):
    self.request.ctx.authenticated = True
    self.request.ctx.dialpad_user = self.dialpad_user
    with patch('core.features.dialpad.middlewares.DialpadClient') as mock_dialpad_client:
      await middlewares.AddDialpadClient.middleware(self.request)
      mock_dialpad_client.assert_called_with(
        self.dialpad_user.dialpad_api_key, base_url=config.DIALPAD_URL
      )


class TestDialpad(base.TransactionalTestCase):

  async def asyncSetUp(self):
    await super().asyncSetUp()
    self.user = await User.create()
    self.dialpad_user = await DialpadUser.create(
      user=self.user, dialpad_user_id='1', dialpad_api_key='test-api-key'
    )
    self.idtoken = utils.get_mock_idtoken(
      user_id=self.dialpad_user.dialpad_user_id,
      api_key=self.dialpad_user.dialpad_api_key
    )

  async def test_expected(self):
    response = await self.make_middleware_test_request('/dialpad', params={'idtoken': self.idtoken})
    self.assertEqual(User, type(response.request_context.user))

  async def test_authentication_fails(self):
    response = await self.make_middleware_test_request('/dialpad')
    self.assertEqual(response.status_code, 403)
