import httpx
import jsonpickle
import unittest

from core import config
from core.orm import config as orm_config


class TestCase(unittest.IsolatedAsyncioTestCase):

  @staticmethod
  def _setup():
    db_client = orm_config.client()
    db_client.flushall()
    client = httpx.AsyncClient(base_url=config.BASE_URL)
    httpx_client = httpx.AsyncClient()
    return db_client, client, httpx_client

  async def make_middleware_test_request(
    self, url_prefix, method='GET', params=None, data=None, headers=None
  ):
    response = await self.client.request(
      method,
      f'{url_prefix}/--middleware-test--',
      params=params,
      data=data,
      headers=headers
    )
    if response.status_code != httpx.codes.OK:
      return response

    response.request_context = jsonpickle.decode(response.text)
    return response


class TransactionalTestCase(TestCase):

  def setUp(self):
    self.db_client, self.client, self.httpx_client = self._setup()

  def tearDown(self):
    self.db_client.flushall()


class TransactionalClassTestCase(TestCase):

  @classmethod
  def setUpClass(cls):
    cls.db_client, cls.client, cls.httpx_client = cls._setup()

  @classmethod
  def tearDownClass(cls):
    cls.db_client.flushall()
