from core import config
from core import utils


CLIENT_ID = utils.getenv('EXTERNAL_CLIENT_ID')
CLIENT_SECRET = utils.getenv('EXTERNAL_CLIENT_SECRET')
SCOPE = utils.getenv('EXTERNAL_SCOPE')
AUTHORIZATION_URL = utils.getenv('EXTERNAL_AUTHORIZATION_URL')
ACCESS_TOKEN_URL = utils.getenv('EXTERNAL_ACCESS_TOKEN_URL')
REFRESH_TOKEN_URL = utils.getenv('EXTERNAL_REFRESH_TOKEN_URL')
REDIRECT_URI = utils.getenv('EXTERNAL_REDIRECT_URI', default='')
