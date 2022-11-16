from sanic.response import json

from core import exceptions
from core.sanic import Route
from core.models import User


class GetUser(Route):
  PATH = '/user/<user_id>'

  async def handler(request, user_id):
    user = await User.get_by_id(user_id)
    if not user:
      raise exceptions.NotFound(f'User not found: {user_id}')
    return json({'user': user.id})
