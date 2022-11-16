from dialpad import DialpadClient

from core import config as core_config
from core import utils as core_utils
from core.features.dialpad import config as dialpad_config
from core.features.dialpad.models import DialpadUser
from core.sanic import OnRequest
from core.sanic import OnResponse


class AddDialpadUser(OnRequest):
  """Adds DialpadUser to the request context."""

  async def middleware(request):
    if not request.ctx.authenticated:
      return

    if not hasattr(request.ctx, 'dialpad_user') or not request.ctx.dialpad_user:
      request.ctx.dialpad_user = await DialpadUser.get_by_id(request.ctx.user.id)


class AddDialpadClient(OnRequest):
  """Adds DialpadClient to the request context."""

  async def middleware(request):
    request.ctx.dialpad_client = None
    if request.ctx.authenticated:
      request.ctx.dialpad_client = DialpadClient(
        request.ctx.dialpad_user.dialpad_api_key,
        base_url=dialpad_config.DIALPAD_URL,
      )


class AddCorsHeaders(OnResponse):
  """Adds CORS headers to the response if application running in dev or remote localhost mode."""
  ACTIVE = not (core_config.is_dev() or core_config.REMOTE_LOCALHOST)

  async def middleware(request, response):
    headers = core_utils.get_cors_headers(
      allow_methods=['GET', 'OPTIONS'],
      allow_origins=[dialpad_config.DIALPAD_URL],
    )
    response.headers.extend(headers)
