import datetime

from core.orm import fields
from core.orm.model import Model
from core.orm.model_key import ModelKey

from core.models import User


class ExternalUser(Model):
  user = fields.ReferenceField(User, unique_key=True)
  access_token = fields.TextField(required=True, indexed=False)
  refresh_token = fields.TextField(indexed=False)
  token_expires_in = fields.IntegerField(indexed=False)
  created = fields.DateTimeField(auto_now_add=True, indexed=False)
  updated = fields.DateTimeField(auto_now=True)

  @property
  def is_token_expired(self):
    if self.token_expires_in:
      return (
        datetime.datetime.now(datetime.timezone.utc).timestamp() > (
          (self.updated + datetime.timedelta(seconds=self.token_expires_in)).timestamp()
        )
      )
    return False

  @classmethod
  async def get_or_create(cls, user, **kwargs):
    instance = await cls.get_by_id(user)
    if not instance:
      return await cls.create(
        user=ModelKey('User', user),
        **kwargs
      ), True
    return instance, False
