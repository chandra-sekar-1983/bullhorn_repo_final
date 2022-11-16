import json
import re
import urllib.parse
from functools import wraps
from sanic.response import html
from sanic.response import redirect

from core import config


def templated_response(template_path, template_context=None, remote_localhost=False):
  """Decorator to route handler which manipulates given template file using template context.

  Any special placeholder defined in template will be replaced by the given data through template
  context.

  Args:
    template_path (str): The file path of the template to be rendered.
    template_context (dict): Extra template context want to be passed to request template_context.
    remote_localhost (bool): Whether or not the request should be redirected to local webpack dev
      server.

  i.e.

  class Index(Route):
    @templated_response(
      template_path=f'{config.TEMPLATES_FOLDER}/index.html',
      template_context={'TEST_VARIABLE': 'thisisatest'}
    )
    async def handler(request):
      pass

  **index.html**
  const __ACCESS_TOKEN__ = template.context.ACCESS_TOKEN # Set by default context
  const __TEST_VARIABLE__ = template.context.TEST_VARIABLE


  If REMOTE_LOCALHOST set to true on core config and remote_localhost set to true, request will
  be redirected to local webpack dev server.
  """
  def decorator(f):
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
      await f(request, *args, **kwargs)
      request.ctx.template_context = request.ctx.template_context or {}
      if template_context:
        request.ctx.template_context.update(template_context)

      if config.REMOTE_LOCALHOST and remote_localhost:
        query = urllib.parse.urlencode(request.ctx.template_context)
        return redirect(f'http://localhost:8087{request.path}?{query}')

      with open(template_path) as template:
        template_content = template.read()
        for key, value in request.ctx.template_context.items():
          value = value if value else ''
          template_content = re.sub(rf'template.context.{key}', json.dumps(value), template_content)

      return html(template_content)

    return decorated_function

  return decorator
