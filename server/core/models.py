import uuid

from core.orm import fields
from core.orm.model import Model


class User(Model):
  """Core User model."""
  key_name = fields.StringField(unique_key=True)
  access_token = fields.StringField(default=str(uuid.uuid4()))

  @classmethod
  async def get_or_create(cls, user_id):
    instance = await cls.get_by_id(user_id)
    if not instance:
      return await cls.create(user_id=user_id), True
    return instance, False

  @classmethod
  async def get_by_access_token(cls, access_token):
    results = [user async for user in cls.all().filter('access_token', '=', access_token).limit(1)]
    return results[0] if results else None
