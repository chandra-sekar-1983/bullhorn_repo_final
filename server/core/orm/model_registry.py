import copy


class ModelRegistry:
  _class_registry = {}
  _fields_registry = {}

  @classmethod
  def register_class(cls, model_class):
    cls._class_registry[model_class.kind] = model_class

  @classmethod
  def register_field(cls, name, field, model_kind):
    if model_kind not in cls._fields_registry:
      cls._fields_registry[model_kind] = {}

    cls._fields_registry[model_kind][name] = copy.deepcopy(field)

  @classmethod
  def get_class(cls, kind):
    return cls._class_registry.get(kind)

  @classmethod
  def get_classes(cls):
    return cls._class_registry.items()

  @classmethod
  def get_kinds(cls):
    return cls._class_registry.keys()

  @classmethod
  def get_fields(cls, kind):
    return cls._fields_registry.get(kind)
