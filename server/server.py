from core import config
from core.sanic import Application


sanic_app = Application.create_sanic_app()
sanic_app.static(config.STATIC_PUBLIC_URL, config.STATIC_FOLDER)


if __name__ == '__main__':
  sanic_app.run(
    host='0.0.0.0',
    port=config.PORT,
    debug=config.is_debug(),
    fast=config.SANIC_FAST
  )
