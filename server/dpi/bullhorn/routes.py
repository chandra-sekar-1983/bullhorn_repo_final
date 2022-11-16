from core import config
from core.decorators import templated_response
from core.sanic import Route


class Index(Route):
  """Index endpoint for the application. Renders the Vue app."""

  @templated_response(
    template_path=f'{config.TEMPLATES_FOLDER}/index.html',
    remote_localhost=True,
  )
  async def handler(request):
    pass
