from core.features.dialpad.iframe.external import config


class CodeGrantOAuthHelper:

  def __init__(
    self,
    redirect_uri=config.REDIRECT_URI,
    client_id=config.CLIENT_ID,
    client_secret=config.CLIENT_SECRET,
    authorization_url=config.AUTHORIZATION_URL,
    access_token_url=config.ACCESS_TOKEN_URL,
    refresh_token_url=config.REFRESH_TOKEN_URL,
    scope=config.SCOPE,
    state=None
  ):
    self.redirect_uri = redirect_uri
    self.client_id = client_id
    self.client_secret = client_secret
    self.authorization_url = authorization_url
    self.access_token_url = access_token_url
    self.refresh_token_url = refresh_token_url
    self.scope = scope
    self.state = state

  async def get_authorization_url(self) -> str:
    """Authorization server auth url."""
    return self.authorization_url

  async def get_authorization_params(self) -> dict:
    """Returns params to be used to make GET request to authorization url."""
    return {
      'response_type': 'code',
      'client_id': self.client_id,
      'redirect_uri': self.redirect_uri,
      'scope': self.scope,
      'state': self.state,
      'access_type': 'offline', # Zoho needs this
    }

  async def get_access_token_url(self, authorize_response: dict = None) -> str:
    """Returns access token url.

    Args:
      authentication_callback_payload: Authentication callback payload optionally can be used to
        create access token request url.
    """
    return self.access_token_url

  async def get_access_token_data(self, code: str) -> dict:
    """Returns payload to be used to make POST request to access token url.

    Args:
      authorize_response: Authentication callback payload optionally can be used to
        create access token request url.
    """
    return {
      'grant_type': 'authorization_code',
      'code': code,
      'redirect_uri': self.redirect_uri,
      'client_id': self.client_id,
      'client_secret': self.client_secret,
    }

  async def get_refresh_token_url(self) -> str:
    """Returns refresh token url."""
    return self.refresh_token_url

  async def get_refresh_token_data(self, refresh_token: str) -> dict:
    """Returns payload to be used to make POST request to refresh token url.

    Args:
      refresh_token: Refresh token

    Returns: A dictionary which contains required parameters to make POST request to refresh token
      url
    """
    return {
      'grant_type': 'refresh_token',
      'refresh_token': refresh_token,
      'client_id': self.client_id,
      'client_secret': self.client_secret,
    }

  async def parse_access_token_response(self, response_data: dict) -> dict:
    """Parses response of the request made to access token url.

    Args:
      response_data: Data of the response of request made to access token url.

    """
    return {
      'access_token': response_data['access_token'],
      'refresh_token': response_data['refresh_token'],
      'expires_in': response_data['expires_in'],
    }

  async def parse_refresh_token_response(self, response_data: dict) -> dict:
    """Parses response of the request made to refresh token url.

    Args:
      response_data: Data of the response of request made to refresh token url.

    """
    return {
      'access_token': response_data['access_token'],
      'expires_in': response_data['expires_in'],
    }
