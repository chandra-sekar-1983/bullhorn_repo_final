import os

from core import utils


ENV = utils.getenv('ENV', default='dev')
NAME = utils.getenv('NAME', default='dpi')
DEBUG = int(utils.getenv('DEBUG', default=0))
SANIC_FAST = int(utils.getenv('SANIC_FAST', default=0))
STATIC_PUBLIC_URL = '/static'
REPO_DIR = os.path.join('..', '..', os.path.dirname(os.path.dirname(__file__)))
STATIC_FOLDER = os.path.join(REPO_DIR, 'static')
TEMPLATES_FOLDER = os.path.join(REPO_DIR, 'templates')
PORT = int(utils.getenv('PORT', default=8088))
BASE_URL = utils.getenv('BASE_URL', default='http://localhost:8088')
REMOTE_LOCALHOST = int(utils.getenv('REMOTE_LOCALHOST', default=0))
ALLOW_UNAUTHENTICATED = [STATIC_PUBLIC_URL]
REDIS_PORT = utils.getenv('REDIS_PORT', default=8082)
REDIS_HOST = utils.getenv('REDIS_HOST', default='localhost')


def is_dev():
  return ENV == 'dev'


def is_debug():
  return is_dev() or DEBUG or is_test()


def is_beta():
  return ENV == 'beta'


def is_test():
  return ENV == 'test'


def is_production():
  return ENV == 'production'
