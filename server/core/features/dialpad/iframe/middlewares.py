from core.sanic import OnRequest


class FetchOAuthAppSettings(OnRequest):
  """Fetches and adds OAuthApp settings to template context.

  template.context.OAUTH_APP_SETTINGS will be replaced by the fetched
  value on index.html when iframe Vue app loaded.
  """

  async def middleware(request):
    settings = request.ctx.dialpad_client.app_settings.get()
    request.ctx.template_context['OAUTH_APP_SETTINGS'] = settings
