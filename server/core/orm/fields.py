import asyncio
import datetime
import threading

from core.orm import exceptions
from core.orm.field import Field
from core.orm.model import Model
from core.orm.model_key import ModelKey


class IntegerField(Field):
  type = int

  def validate(self, value):
    value = super().validate(value)

    if value and (value < -0x8000000000000000 or value > 0x7fffffffffffffff):
      raise exceptions.BadValueError(f'IntegerField {self.name} must fit in 64 bits')

    return value


class StringField(Field):
  type = str
  MAX_LENGTH = 1500

  def __init__(self, *args, max_length=None, multiline=False, **kwargs):
    super().__init__(*args, **kwargs)
    self.max_length = max_length or self.MAX_LENGTH
    self.multiline = multiline

  def validate(self, value):
    value = super().validate(value)
    if value is None:
      return

    if not self.multiline and value.find('\n') != -1:
      raise exceptions.BadValueError(f'StringField {self.name} cannot be multi-line')

    if len(value) > self.max_length:
      raise exceptions.BadValueError(
          f'StringField {self.name} is {len(value)} bytes long;'
          f'it must be {self.max_length} or less.'
      )

    return value


class TextField(Field):
  type = str


class DateTimeField(Field):
  type = datetime.datetime

  def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
    super().__init__(**kwargs)
    self.auto_now = auto_now
    self.auto_now_add = auto_now_add

  @property
  def default(self):
    # If we're using either auto-now flag, then the property should default to the current time.
    if self.auto_now or self.auto_now_add:
      return datetime.datetime.now()

    return super().default

  def serialize(self):
    # If the auto-now flag is set, then this property should be the current time whenever it gets
    # persisted.
    if self.auto_now:
      return datetime.datetime.now()

    return super().serialize()


class BooleanField(Field):
  type = bool


class ReferenceField(Field):

  def __init__(self, reference_model=None, *args, **kwargs):
    super().__init__(*args, **kwargs)

    if reference_model is not None and not issubclass(reference_model, Model):
      raise exceptions.ModelReferenceError(
        f'reference_model ({type(reference_model)}) must inherit from Model')

    self._reference_model = reference_model
    self._resolved_entity = None

  async def _fetch_from_key(self):
    self._resolved_entity = await self._value.fetch()

  def _fetch(self):
    loop = asyncio.new_event_loop()
    try:
      loop.run_until_complete(self._fetch_from_key())
    except Exception as e:
      raise e
    finally:
      loop.close()

  def fetch(self):
    thread = threading.Thread(target=self._fetch)
    thread.start()
    thread.join()

  @property
  def value(self):
    """A resolved instance of the referenced entity."""
    if self._value is None:
      return None

    if not isinstance(self._value, ModelKey) and self.kind is not None:
      self._value = ModelKey(self.kind, self._value)

    if self._resolved_entity is None:
      self.fetch()

    return self._resolved_entity

  @value.setter
  def value(self, val):
    """Takes a ModelKey or Model."""
    self._value = self.validate(val)

    # We can pre-cache the entity if we were given a full Model, but otherwise we need to
    # invalidate.
    self._resolved_entity = val if isinstance(val, Model) else None

  def set_persisted(self, persisted_value):
    """Remembers the currently-persisted value.

    This method should be called by the model after loading or saving an entity.
    """
    self._persisted_value = persisted_value

  @property
  def kind(self):
    if not self._reference_model:
      return None

    return self._reference_model.kind

  def validate(self, value):
    """Validates the given value, and either returns a validated value, or raises BadValueError.

    Validate can also be used for data normalization For example, user.number = '5' could be nice
    and convert '5' to an integer without becoming upset.
    """
    value = super().validate(value)

    if value is None:
      return value

    if isinstance(value, Model):
      value = value.key

    if isinstance(value, ModelKey):
      if self.kind is not None and value.kind != self.kind:
        msg = f'{self.name} expects values of kind "{self.kind}" but got "{value.kind}"'
        raise exceptions.BadValueError(msg)

    return value

  def serialize(self):
    value = self.value
    if isinstance(value, Model):
      return value.key

    if isinstance(value, ModelKey):
      return value

    return value
