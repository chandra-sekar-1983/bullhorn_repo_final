from core.orm import model
from core.orm.clients.base import Client
from core.orm.redis_db import RedisDB


class RedisClient(Client):
  client = RedisDB()
  MAX_RETRY = 5

  def _serialize_value(self, value):
    if isinstance(value, model.ModelKey):
      return value.entity_id

    return value

  async def get(self, key):
    entity = self.client.get(key.kind, key.entity_id)
    if not entity:
      return

    return key.model_cls.from_database(**entity)

  async def create(self, instance):
    data = instance.serialize()
    self.client.create(
      instance.kind, instance.id, {k: self._serialize_value(v) for k, v in data.items()}
    )
    return instance.set_persisted(**data)

  async def update(self, instance):
    data = instance.serialize()
    self.client.update(instance.kind, instance.id, data)
    return instance.set_persisted(**data)

  async def delete(self, key):
    self.client.delete(key.kind, key.entity_id)

  def flushall(self):
    self.client.flushall()

  async def run_query(
    self,
    model_cls,
    filters,
    order_by=None,
    limit=None,
    cursor=None,
  ):
    result_list = self.client.query(model_cls.kind, filters)
    return [
      model_cls.from_database(**entity)
      for entity in result_list
    ], None
