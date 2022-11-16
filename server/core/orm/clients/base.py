import abc
from typing import Optional

from core.orm import model
from core.orm.query import Query


class Client(metaclass=abc.ABCMeta):
  """Generic storage interface.

  Client implementations should use Model.serialize to convert the model into a dict of the form:
  {
    '<field_name>': <field_value>,
    ...
  }

  The field_names are guaranteed to be strings, and field_values will be either a primative type
  (str, int, etc), a datetime, or a ModelKey.

  It is the client's responsibility to transform that dict into a form that can be written to the
  underlying database.

  Similarly, clients should be able to reconstruct the identical dict when reading from the database
  and feed them to Model.from_database(**the_dict) to convert them back into Model objects.
  """

  @abc.abstractmethod
  async def get(self, key: 'model.ModelKey') -> 'model.Model':
    pass

  @abc.abstractmethod
  async def create(self, instance: 'model.Model') -> 'model.Model':
    pass

  @abc.abstractmethod
  async def update(self, instance: 'model.Model') -> 'model.Model':
    pass

  @abc.abstractmethod
  async def delete(self, key: 'model.ModelKey') -> None:
    pass

  @abc.abstractmethod
  async def flushall(self) -> None:
    pass

  @abc.abstractmethod
  async def run_query(
    self,
    model_cls: type['model.Model'],
    filters: dict,
    order_by: list = None,
    limit: int = None,
    cursor: str = None,
  ) -> 'tuple[list[model.Model], Optional[str]]':
    """Returns a tuple containing a list of models and a cursor."""
    pass

  def query(self, model_cls):
    return Query(self, model_cls)
