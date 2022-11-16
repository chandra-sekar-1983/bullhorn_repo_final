from core.sanic import Application
from core.sanic import OnRequest

from core.features.dialpad import config as dialpad_config
from core.features.dialpad import utils
from core.features.dialpad.models import DialpadUser
from core.models import User


class AuthenticateDialpad(OnRequest):
  """Bypass core authentication and uses Dialpad Iframe idtoken authentication."""

  async def middleware(request):
    path = f'/{request.route.path}' if request.route else request.path
    if (
      request.args.get('access_token') or
      request.ctx.allow_unauthenticated or
      (
        request.route and
        request.route.ctx and
        hasattr(request.route.ctx, 'allow_unauthenticated')
        and request.route.ctx.allow_unauthenticated
      ) or
      not path.startswith('/dialpad')
    ):
      return

    idtoken = request.args.get('idtoken')
    request.ctx.idtoken = idtoken
    payload = await utils.get_auth_payload_from_idtoken(
      idtoken, dialpad_config.DIALPAD_CLIENT_SECRET
    )
    dialpad_user_id = str(payload['user_id'])
    dialpad_api_key = str(payload['api_key'])

    dialpad_user = await DialpadUser.get_by_dialpad_user_id(dialpad_user_id)
    if not dialpad_user:
      user = await User.create()
      dialpad_user = await DialpadUser.create(
        user=user, dialpad_user_id=dialpad_user_id, dialpad_api_key=dialpad_api_key
      )
    else:
      await dialpad_user.update_api_key_if_needed(dialpad_api_key)

    request.ctx.dialpad_user = dialpad_user
    request.ctx.user = dialpad_user.user
    request.ctx.authenticated = True


dpi = Application.get_feature('dpi')
# Injects AuthenticateDialpad middleware before any root middleware injected. This will ensure
# that Dialpad Authentication will be prioritized over root middlewares.
dpi.inject_middleware(AuthenticateDialpad)
