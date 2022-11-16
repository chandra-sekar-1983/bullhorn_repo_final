from core import config
from core.features.dialpad.iframe.external.core.client import ExternalClient
from core.features.dialpad.iframe.external.core.oauth import CodeGrantOAuthHelper
from core.sanic import OnRequest


class AddExternalClient(OnRequest):

  async def middleware(request):
    redirect_uri = f"{config.BASE_URL}{request.path.split('external')[0]}external/oauth-redirect"
    request.ctx.external_client = ExternalClient(CodeGrantOAuthHelper(redirect_uri=redirect_uri))
    if request.ctx.user:
      await request.ctx.external_client.get_connection(request.ctx.user.id)
