from sanic import response
import json
import requests

from core.sanic import Route
from core.utils import make_request
from dpi.bullhorn.api.util import get_bhrest_token

from dpi.bullhorn.config import BullhornConfig
from dpi.bullhorn.api.util import BullhornAction

bh_config = BullhornConfig()

class TestEndpoint(Route):

  async def handler(request):
    return response.json({
      'rest_url': request.ctx.bullhorn_client.rest_url,
      'rest_token': request.ctx.bullhorn_client.rest_token,
    })

class Search(Route):
  PATH = "contact"

  async def handler(request):
    try:
      search = request.args.get("search", False)
      print("SEARCH : {}".format(search))

      bhrest_token = request.args.get("bhrest_token", None)
      if not bhrest_token:
        bhrest_token = get_bhrest_token()
      bh_access_token = request.args.get("bh_access_token", None)
      bh_action = BullhornAction(request=request, bhrest_token=bhrest_token, access_token=bh_access_token)

      result = bh_action.search_contact()
      print("RESULT : {}".format(result))
      if result.get('status') == 200:
        return response.json(result, 200)
      elif result.get('status') == 400:
        resp = {
          'message': result.get('errorMessage'),
          'status': 400
        }
        return response.json(resp, 400)
      elif result.get('status') == 401:
        return response.json(result, 401)
      else:
        return response.json(result, result.get('status'))
    except Exception as e:
      resp = {
        "message": "Internal server error",
        "details": str(e),
        "status": 500
      }
      print("Expenctions : {}".format(str(e)))
      return response.json(resp, 500)

class SampleEndpoint(Route):
    PATH = 'sample-endpoint'
    
    async def handler(request):
      try:
        print("candidate type name : {}".format(bh_config.entity_types['candidate']))
        resp = {
          'data': [
            {
                "id": 17,
                "name": "Ajit Jadhav",
                "firstName": "Ajit",
                "lastName": "Jadhav",
                "phone": 9096278534,
                "_score": 1.0,
                "entity_type": "candidate"
            },
            {
                "id": 17,
                "name": "Chandra Sekar",
                "firstName": "Chandra",
                "lastName": "Sekar",
                "phone": 9096278534,
                "_score": 1.0,
                "entity_type": "lead"
            },
            {
                "id": 17,
                "name": "Vineet Kumar",
                "firstName": "Vineet",
                "lastName": "Kumar",
                "phone": 9096278534,
                "_score": 1.0,
                "entity_type": "candidate"
            }
          ],
          "count": 3,
          "status": 200,
          "message": "This is the static data at backend"
        }
        return response.json(resp, 200)
      except Exception as e:
        resp = {
          'message': "Internal server error",
          'details': str(e),
          'status': 500
        }
        return response.json(resp, 500)

