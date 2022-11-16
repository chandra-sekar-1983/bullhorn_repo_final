from core import utils


client = utils.load_class(
  f"{utils.getenv('ORM_CLIENT', 'core.orm.clients.redis.RedisClient')}"
)
