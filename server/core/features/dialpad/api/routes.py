from sanic.response import json

from core.sanic import Route


class GetSettings(Route):
  PATH = '/settings'

  async def handler(request):
    return json(request.ctx.dialpad_client.app_settings.get())
