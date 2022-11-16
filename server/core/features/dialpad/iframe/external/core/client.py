from urllib.parse import urlencode

from core.logging import logger
from core.utils import make_request
from core.features.dialpad.iframe.external.models import ExternalUser


class ExternalClient:
  api_url = None
  external_user = None

  def __init__(self, oauth):
    self.oauth = oauth
    self.external_user = None

  @property
  def access_token(self):
    return self.external_user.access_token if self.is_connected else None

  @property
  def refresh_token(self):
    return self.external_user.refresh_token if self.is_connected else None

  @property
  def is_connected(self):
    return self.external_user is not None

  async def get_connection(self, user_id):
    self.external_user = await ExternalUser.get_by_id(user_id)
    if not self.external_user:
      self.oauth.state = user_id
      params = await self.oauth.get_authorization_params()
      authorization_url = await self.oauth.get_authorization_url()
      query = urlencode(params)
      return {'connected': False, 'authorization_url': f'{authorization_url}?{query}'}

    if self.external_user.is_token_expired:
      await self.refresh_access_token()

    return {'connected': True, 'auth_url': None}

  async def fetch_access_token(self, args):
    user_id = args['state'][0]
    token_url = await self.oauth.get_access_token_url(args)
    data = await self.oauth.get_access_token_data(args['code'])
    response = await make_request('POST', token_url, data=data)
    token_response = await self.oauth.parse_access_token_response(response.json())
    await ExternalUser.get_or_create(
      user_id,
      access_token=token_response['access_token'],
      refresh_token=token_response['refresh_token'],
      token_expires_in=token_response['expires_in'],
    )

  async def refresh_access_token(self):
    logger.debug('Refreshing token')
    token_url = await self.oauth.get_refresh_token_url()
    data = await self.oauth.get_refresh_token_data(self.external_user.refresh_token)
    response = await make_request('POST', token_url, data=data)
    token_response = await self.oauth.parse_refresh_token_response(response.json())
    self.external_user.access_token = token_response['access_token']
    self.external_user.token_expires_in = token_response['expires_in']
    self.external_user = await self.external_user.update()
