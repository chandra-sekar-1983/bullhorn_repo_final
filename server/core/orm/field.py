import abc
import uuid
from typing import Any

from core.orm import exceptions
from core.orm.model_key import ModelKey
from core.orm.model_registry import ModelRegistry


def _default_unique_key():
  return str(uuid.uuid4())


class Field(abc.ABC):
  """Field is an abstract base class for fields on ORM models.

  Subclasses of Field are encouraged to use the following methods and attributes to customize
  behaviour:

  - type: If the "type" attribute is assigned, then field validation will enforce that type
          constraint.
  - validate: The validate method can be overridden to enforce nuanced value constraints.


  Subclasses of Field can implement much more complex behaviour as long as they respect the expected
  behaviour of the value interface methods.

  Fields are responsible for validating and storing data on behalf of the ORM Models that use them.
  To facilitate this, every instance of a Model creates new instances of its Fields to allow each
  Field to store data for that particular data entity.

  Internally, a Field can store its value however it likes, but there are two distinc ways that the
  field value can be accessed and mutated:
  - The consumer interface e.g.
    - print(user.some_field)
    - user.some_field = 5
  - The persistence interface e.g.
    - u = User.get('abc123')
    - u.put()

  When a model is being loaded or saved, the field data needs to be deserialized or serialized,
  whereas when model fields are being referenced or set, a different representation might be more
  convenient for the consumer. (Reference fields are a good example of this distinction)

  Subclasses can override the value getter and setter to customize the consumer interface, and they
  can override the serialize and deserialize methods to customize the persitence interface.

  To track pending changes to this field that have not yet been persisted, Field maintains a
  "committed" value, and a list of "staged" values. The "_value" getter and setter should be used
  by subclasses rather than directly mutating _committed_values and _staged_values.
  """
  def __init__(
    self,
    required: bool = False,
    choices: list = None,
    default: Any = None,
    indexed: bool = True,
    unique_key: bool = False,
    nullable: bool = True,
  ) -> None:
    if unique_key and default is None:
      default = _default_unique_key

    self.required = required
    self.indexed = indexed
    self._default = default
    self.choices = choices
    self.unique_key = unique_key
    self.nullable = nullable
    self._committed_value = None
    self._staged_values = []

  def __set_name__(self, model_class, name) -> None:
    self.model_class = model_class
    self.name = name
    if not ModelRegistry.get_class(model_class.kind):
      ModelRegistry.register_class(model_class)

    ModelRegistry.register_field(name, self, model_class.kind)

  @property
  def default(self):
    if callable(self._default):
      return self._default()

    return self._default

  @property
  def _value(self):
    """Returns the internally-stored value for this field."""
    return self._staged_values[-1] if len(self._staged_values) > 0 else self._committed_value

  @_value.setter
  def _value(self, val):
    """Set the internally-stored value for this field."""
    self._staged_values.append(val)

  @property
  def value(self):
    """Returns a model-facing representation of the field's value.

    i.e. `user.some_field` will return this value representation.
    """
    return self._value

  @value.setter
  def value(self, val):
    """model-facing setter for the field's value.

    i.e. `user.some_field = 5` will use this setter.
    """
    self._value = self.validate(val)

  def serialize(self):
    """Returns a perstintence-facing representation of the field's value.

    i.e. User(some_field=5).put() will persist this value to the database.
    """
    return self.value

  def deserialize(self, val):
    """db-facing setter for the field's value.

    i.e. User.get('abc123') will load this value from the database using this method.
    """
    self.value = val

  def set_persisted(self, persisted_value):
    """Remembers the currently-persisted value.

    This method should be called by the model after loading or saving an entity.
    """
    self._committed_value = persisted_value
    self._staged_values = []

  def validate(self, value):
    """Validates the given value, and either returns a validated value, or raises BadValueError.

    Validate can also be used for data normalization For example, user.number = '5' could be nice
    and convert '5' to an integer without becoming upset.
    """
    if value is None:
      if not self.nullable:
        raise exceptions.BadValueError(f'Field {self.name} is not nullable')
      return value

    if hasattr(self, 'type') and not isinstance(value, self.type):
      raise exceptions.BadValueError(
        f'{self.__class__.__name__} {self.name} must be {self.type}, '
        f'not a {type(value).__name__}'
      )

    if self.choices and value not in self.choices:
      raise exceptions.BadValueError(f'Field {self.name} is {value!r};'
                                     f' must be one of {self.choices!r}')

    return value
