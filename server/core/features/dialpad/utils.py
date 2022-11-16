from jose import jwe
from jose import jwt

from core import exceptions
from core.features.dialpad import config


async def get_auth_payload_from_idtoken(id_token, secret):
  """Returns decrypted Dialpad user payload from given id token using given secret."""
  async def _extract_payload_from_idtoken(id_token, secret):
    if not id_token:
      raise exceptions.Forbidden('Authentication failed')

    try:
      jwt_token = jwe.decrypt(id_token, secret[:32])
      return jwt.decode(jwt_token, secret, algorithms=['HS256'])
    except Exception:
      raise exceptions.Forbidden('Authentication failed')

  payload = await _extract_payload_from_idtoken(id_token, secret)
  if not payload or 'api_key' not in payload or 'user_id' not in payload:
    raise exceptions.Forbidden('Authentication failed')

  return payload


def get_mock_idtoken(user_id='test-dialpad-user-id', api_key='test-dialpad-api-key'):
  """Returns mock encrypted idtoken in the same format Dialpad using."""
  jwt_token = jwt.encode({'user_id': user_id, 'api_key': api_key}, config.DIALPAD_CLIENT_SECRET)
  return jwe.encrypt(jwt_token, config.DIALPAD_CLIENT_SECRET[:32])
