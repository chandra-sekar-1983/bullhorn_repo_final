import abc
import copy

from functools import cached_property

from core.orm import exceptions
from core.orm.config import client
from core.orm.model_registry import ModelRegistry
from core.orm.model_key import ModelKey
from core.orm.query import Query


class Model(abc.ABC):
  _special_attrs = {
    '_instance_fields'
  }

  def __new__(cls, _from_database=False, **values):
    # Whenever we construct a new instance, we need to make a deep copy of the class fields to
    # allow each entity to store values within thier own field instances.
    self = super().__new__(cls)
    self._instance_fields = copy.deepcopy(ModelRegistry.get_fields(cls.kind))

    # Either initialize or deserialize the field values depending on whether we're being populated
    # from the database or from a developer hitting the constructor.
    if _from_database:
      self._deserialize_values(**values)
    else:
      self._initialize_values(**values)

    return self

  def __init_subclass__(cls) -> None:
    super().__init_subclass__()
    # Check if model is not registered, if so register. This could only happen if no field is
    # declared for this model.
    if not ModelRegistry.get_class(cls.kind):
      ModelRegistry.register_class(cls)

  @classmethod
  def from_database(cls, **values):
    """Convenience method for loading an entity from raw database values."""
    return cls(_from_database=True, **values)

  @cached_property
  def _unique_key_fields(self):
    return [f for f in self.fields.values() if f.unique_key]

  @property
  def id(self):
    return ':'.join(str(f.serialize()) for f in self._unique_key_fields)

  def _initialize_values(self, **values):
    """Initializes field values for newly-created entities."""
    if len(self._unique_key_fields) < 1:
      msg = 'Model subclasses must define at least one unique key field'
      raise exceptions.ImproperlyConfigured(msg)

    unrecognized_fields = set(values) - set(self.fields)
    if unrecognized_fields:
      msg = f'"{self.kind}" was given unrecognize fields: "{unrecognized_fields}"'
      raise exceptions.FieldDoesNotExist(msg)

    # Use the field setters to populate values.
    for name, field in self.fields.items():
      # Default values should be used for new entities.
      if name not in values and field.default is not None:
        values[name] = field.default

      # Required fields must be explicitly set for new entities.
      if field.required and name not in values:
        raise exceptions.BadValueError(f'Missing value for required field "{name}"')

      setattr(self, name, values.get(name))

    return self

  def _deserialize_values(self, **values):
    """Deserializes field values to load entities from a database."""
    # Use the fields' deserialize method to load values from their serialized form.
    for name, field in self.fields.items():
      # Any fields that have explicitly-prescribed values should be deserialized.
      if name in values:
        field.deserialize(values[name])

      # Regardless of which fields were present in the database, this state is currently persisted.
      field.set_persisted(values.get(name))

    return self

  def set_persisted(self, **persisted_values):
    for name, field in self.fields.items():
      field.set_persisted(persisted_values.get(name))

    return self

  @classmethod
  @property
  def class_fields(cls):
    return ModelRegistry.get_fields(cls.kind)

  @property
  def fields(self):
    return self._instance_fields

  @property
  def values(self):
    return {f.name: f.value for f in self.fields.values()}

  def __iter__(self):
    return self.values.items()

  def __setattr__(self, name, value):
    if name in super().__getattribute__('_special_attrs'):
      return super().__setattr__(name, value)
    if name not in super().__getattribute__('class_fields'):
      raise exceptions.FieldDoesNotExist(f'Field {name} does not exists!')

    self.fields[name].value = value

  def __getattribute__(self, name):
    if name in super().__getattribute__('_special_attrs'):
      return super().__getattribute__(name)

    fields = super().__getattribute__('fields')
    if name in fields:
      return fields[name].value

    return super().__getattribute__(name)

  @cached_property
  def exclude_from_indexes(self):
    return [name for name, field in self.fields.items() if not field.indexed]

  def serialize(self):
    return {name: field.serialize() for name, field in self.fields.items()}

  @classmethod
  @property
  def kind(cls):
    return cls.__name__

  @classmethod
  def has_field(cls, name):
    return name in cls.class_fields

  @classmethod
  @property
  def client(cls):
    return client()

  @property
  def key(self):
    return ModelKey(self.kind, self.id)

  @classmethod
  async def get_by_id(cls, enitity_id):
    if not enitity_id:
      return

    return await cls.client.get(ModelKey(cls.kind, enitity_id))

  @classmethod
  async def create(cls, **kwargs):
    return await cls.client.create(cls(**kwargs))

  async def update(self):
    return await self.client.update(self)

  async def delete(self):
    await self.client.delete(self.key)

  @classmethod
  async def delete_by_id(cls, entity_id):
    await cls.client.delete(ModelKey(cls.kind, entity_id))

  @classmethod
  def all(cls):
    return Query(cls.client, cls)
