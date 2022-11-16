import operator
import redis

from core import config
from core.orm import exceptions


class RedisDB:
  MAX_RETRY = 10

  def __init__(self):
    self.client = redis.Redis(decode_responses=True, port=config.REDIS_PORT, host=config.REDIS_HOST)

  def create(self, kind, id, data):
    entity_key = f'{kind}:{id}'
    try:
      pipeline = self.client.pipeline()
      pipeline.watch(entity_key)
      entity = pipeline.hgetall(entity_key)
      if entity:
        raise exceptions.EntityExists()

      pipeline.multi()
      pipeline.hset(entity_key, mapping=data)
      pipeline.sadd(kind, entity_key)

      for key, value in data.items():
        field_key = f'{kind}:{id}:{key}:{value}'
        pipeline.set(field_key, 1)

      count_meta_key = f'{kind}:meta:count'
      pipeline.incrby(count_meta_key)
      pipeline.execute()
    except redis.exceptions.WatchError:
      raise exceptions.EntityExists('Entity is already created')

  def flushall(self):
    self.client.flushall()

  def get(self, kind, id):
    return self.client.hgetall(f'{kind}:{id}')

  def delete(self, kind, id):
    deleted = self.client.delete(f'{kind}:{id}')
    if not deleted:
      return 0

    pipeline = self.client.pipeline()
    pipeline.srem(kind, id)
    [
      pipeline.delete(field_key)
      for field_key in self.client.scan_iter(match=f'{kind}:{id}:*:*')
    ]
    pipeline.decrby(f'{kind}:meta:count')
    pipeline.execute()
    return 1

  def update(self, kind, id, data):
    pipeline = self.client.pipeline()
    entity_key = f'{kind}:{id}'
    deleted = pipeline.delete(f'{kind}:{id}')
    if not deleted:
      return

    pipeline.multi()
    pipeline.hset(entity_key, mapping=data)
    pipeline.execute()

  def query(self, kind, filters):

    def _compare(inp, relate, cut):
      ops = {'>': operator.gt,
             '<': operator.lt,
             '>=': operator.ge,
             '<=': operator.le,
             '=': operator.eq}
      return ops[relate](inp, cut)

    pipeline = self.client.pipeline()
    filtered = []
    if not filters:
      entity_keys = self.client.smembers(kind)
      [pipeline.hgetall(entity_key) for entity_key in entity_keys]

    else:
      for field_name, cmp, value in filters:
        _, matches = self.client.scan(match=f'{kind}:*:{field_name}:*')
        filtered += filter(lambda x: _compare(x.split(':')[-1], cmp, value), matches)

      entity_ids = set([key.split(':')[1] for key in filtered])
      [pipeline.hgetall(f'{kind}:{entity_id}') for entity_id in entity_ids]

    return pipeline.execute()
