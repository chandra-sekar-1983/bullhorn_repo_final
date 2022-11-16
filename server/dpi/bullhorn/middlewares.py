from core.sanic import OnRequest

from dpi.bullhorn.client import BullhornClient


# class AddBullhornClient(OnRequest):

#   async def middleware(request):
#     if request.ctx.external_client.is_connected:
#       request.ctx.bullhorn_client = BullhornClient(
#         request.ctx.external_client.access_token
#       )
#       await request.ctx.bullhorn_client.login()
