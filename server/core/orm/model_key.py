# Author: Jake Nielsen

from core.orm.model_registry import ModelRegistry


class ModelKey:
  """A structure that uniquely identifies a particular ORM entity."""

  def __init__(self, kind, entity_id):
    self.kind = kind
    self.entity_id = entity_id

  def __hash__(self):
    return hash((self.kind, self.entity_id))

  def __str__(self):
    return self.entity_id

  @property
  def model_cls(self):
    return ModelRegistry.get_class(self.kind)

  async def fetch(self):
    return await self.model_cls.get_by_id(self.entity_id)
