import asyncio
import threading
from google.cloud import datastore

from core import config
from core import exceptions
from core import utils
from core.orm import model
from core.orm.clients.base import Client
from typing import Optional


class DatastoreClient(Client):
  client = datastore.Client()

  def _serialize_value(self, value):
    if isinstance(value, model.ModelKey):
      return self.client.key(value.kind, value.entity_id)

    return value

  def _deserialize_value(self, value):
    if isinstance(value, datastore.Key):
      return model.ModelKey(value.kind, value.name)

    return value

  async def get(self, key: 'model.ModelKey') -> 'model.Model':
    entity = self.client.get(self._serialize_value(key))
    if not entity:
      return
    data = {k: self._deserialize_value(v) for k, v in dict(entity).items()}
    return key.model_cls.from_database(**data)

  async def create(self, instance: 'model.Model') -> 'model.Model':
    ds_key = self._serialize_value(instance.key)
    entity = datastore.Entity(ds_key, exclude_from_indexes=instance.exclude_from_indexes)

    data = instance.serialize()
    entity.update({k: self._serialize_value(v) for k, v in data.items()})
    entity = self.client.put(entity)

    return instance.set_persisted(**data)

  async def update(self, instance: 'model.Model') -> 'model.Model':
    with self.client.transaction():
      entity = self.client.get(self._serialize_value(instance.key))
      if not entity:
        return

      data = instance.serialize()
      entity.update({k: self._serialize_value(v) for k, v in data.items()})
      entity = self.client.put(entity)

    return instance.set_persisted(**data)

  async def delete(self, key: 'model.ModelKey') -> None:
    self.client.delete(self._serialize_value(key))

  async def _flushall(self):
    await utils.make_request('POST', f"{utils.getenv('DATASTORE_HOST')}/reset")

  def _flushall_threadsafe(self):
    loop = asyncio.new_event_loop()
    try:
      loop.run_until_complete(self._flushall())
    except Exception as e:
      raise e
    finally:
      loop.close()

  def flushall(self):
    if not config.is_test():
      raise exceptions.BadRequestError('Can only flush data when on a emulator')

    thread = threading.Thread(target=self._flushall_threadsafe)
    thread.start()
    thread.join()

  async def run_query(
    self,
    model_cls: type['model.Model'],
    filters: list,
    order_by: str = None,
    limit: int = None,
    cursor: str = None,
  ) -> 'tuple[list[model.Model], Optional[str]]':

    query = self.client.query(kind=model_cls.kind)
    for item in filters:
      query.add_filter(*item)

    if order_by:
      query.order = order_by

    query_iterator = query.fetch(limit=limit, start_cursor=cursor)
    next_cursor = ''
    if query_iterator.next_page_token:
      next_cursor = query_iterator.next_page_token.decode('utf-8')
    return [
      model_cls.from_database(**{k: self._deserialize_value(v) for k, v in dict(entity).items()})
      for entity in query_iterator
    ], next_cursor
