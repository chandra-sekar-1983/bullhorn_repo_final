import os

from sanic.response import json

from core import exceptions
from core.decorators import templated_response
from core.sanic import Route


class OAuthRedirect(Route):
  PATH = '/oauth-redirect'
  ALLOW_UNAUTHENTICATED = True

  @templated_response(
    template_path=(
      os.path.join(
        os.path.dirname(__file__),
        'templates',
        'post_event_close_popup.html'
      )
    )
  )
  async def handler(request):
    try:
      await request.ctx.external_client.fetch_access_token(request.args)
    except Exception as e:
      raise exceptions.BadRequestError(f'Cannot fetch access token on OAuth redirect: \n {e}')


class GetConnection(Route):
  PATH = '/connection'

  async def handler(request):
    return json(await request.ctx.external_client.get_connection(request.ctx.user.id))
