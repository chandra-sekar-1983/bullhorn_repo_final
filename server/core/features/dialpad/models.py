from core.orm import fields
from core.orm.model import Model

from core.models import User


class DialpadUser(Model):
  user = fields.ReferenceField(User, unique_key=True)
  dialpad_user_id = fields.StringField()
  dialpad_api_key = fields.StringField(indexed=False)

  @classmethod
  async def get_by_dialpad_user_id(cls, dialpad_user_id):
    results = [
      user async for user in cls.all().filter('dialpad_user_id', '=', dialpad_user_id).limit(1)
    ]
    return results[0] if results else None

  async def update_api_key_if_needed(self, api_key):
    if self.dialpad_api_key != api_key:
      self.dialpad_api_key = api_key
      return await self.update()

    return self
