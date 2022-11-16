from core.utils import make_request


class BullhornClient:

  def __init__(self, access_token):
    self.access_token = access_token
    self.login_url = (
      'https://rest.bullhornstaffing.com/rest-services/login'
      f'?version=*&access_token={self.access_token}'
    )
    self.rest_url = None

  async def login(self):
    response = await make_request('POST', self.login_url)
    response_json = response.json()
    self.rest_token = response_json['BhRestToken']
    self.rest_url = response_json['restUrl']

  async def make_request(self, method, uri, params=None, data=None, headers=None):
    url = f'{self.rest_url}{uri}'
    params = params or {}
    params.update({'BhRestToken={self.rest_token}'})
    return await make_request(method, url, params=params, data=data, headers=headers)
