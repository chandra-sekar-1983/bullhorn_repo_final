import requests
import json

from dpi.bullhorn.config import BullhornConfig

def get_bhrest_token():
    ## Required details to get Authentication code, Access code and BhRestToken
    client_id = "5166a72d-6ddc-454c-aa35-b287d085be8a"
    client_secret = "QLcu3T9vSSB0QXsdkH6KIrfn"
    username = "dialpad.api"
    password = "T32F3kv$P!S][TQ1"
    response_type = "code"
    action = "Login"
    state = ""
    grant_type = "authorization_code"
    redirect_uri = ""
    version = "*"

    ## Bullhorn Authentication base-urls
    get_auth_code_url = "https://auth.bullhornstaffing.com/oauth/authorize"
    get_access_token_url = "https://auth.bullhornstaffing.com/oauth/token"
    get_bhrest_token_url = "https://rest.bullhornstaffing.com/rest-services/login"

    ## Request to get Authentication code
    get_auth_code_url += "?client_id={}&password={}&username={}&action={}&response_type={}".format(client_id, password, username, action, response_type)
    auth_code_resp = requests.get(url=get_auth_code_url, allow_redirects=False)
    location = auth_code_resp.headers['Location']
    print("Auth code resp : {}".format(location))
    from urllib.parse import urlparse
    parsed_url = urlparse(location)
    print("Parsed URL : {}".format(parsed_url))
    print("Code : {}".format(parsed_url.query[5:]))
    code = parsed_url.query[5:]

    ## Request to get Access Token
    get_access_token_url += "?client_id={}&client_secret={}&grant_type={}&code={}".format(client_id, client_secret, grant_type, code)
    access_token_resp = requests.post(url=get_access_token_url)
    json_resp = json.loads(access_token_resp.text)
    print("Access Token resp : {}".format(json_resp))
    access_token = json_resp['access_token']

    ## Request to get BhRestToken
    get_bhrest_token_url += "?version={}&access_token={}".format(version, access_token)
    bhrest_token_resp = requests.post(url=get_bhrest_token_url)
    parsed_resp =  json.loads(bhrest_token_resp.text) 
    print("BhRestToken resp : {}".format(parsed_resp))
    bhrest_token = parsed_resp.get('BhRestToken')
    return bhrest_token



class BullhornAction():

    def __init__(self, request, access_token=None, bhrest_token=None):
        self.request = request
        self.access_token = access_token
        self.bhrest_token = bhrest_token
        self.bh_config = BullhornConfig()

    def build_free_search_query(self, entity_type, search_val):
        print("\n---------------------- In build_free_search_query() ---------------------\n")
        query = ""
        search_val = search_val.strip()
        for i, field in enumerate(self.bh_config.entity_types.get(entity_type).get('search_query_fields')):
            if i == 0:
                query += "{}:{}*".format(field, search_val)
            else: 
                query += " OR {}:{}*".format(field, search_val)
        print("QUERY = {}".format(query))
        return query

    def build_auto_search_query(self, params):
        print("\n----------------------In build_auto_search_query(params = {}) ---------------------\n".format(params))
        
        query = ""
        i = 0
        for key, val in params.items():
            if i == 0:
                query += "{}:{}".format(key, val[0])
            else: 
                query += " AND {}:{}".format(key, val[0])
            i +=1
        print("AUTO SEARCH QUERY -- = {}".format(query))
        return query
    
    def make_request(self, url, method, body=dict()):
        print("\n---------------------- In make_request(url={}, method={}, body={}) ---------------------\n".format(url, method, body))
        request_resp = None
        resp = {}
        if method == "GET":
            request_resp = requests.get(url)
        elif method == "POST":
            request_resp = requests.post(url, data=body)
        elif method == "PUT":
            request_resp = requests.put(url, data=body)
        elif method == "PATCH":
            request_resp = requests.patch(url, data=body)
        
        if request_resp.status_code == 200:
            resp.update(json.loads(request_resp.text))
            resp['status'] = 200
        elif request_resp.status_code == 400:
            resp.update(json.loads(request_resp.text))
            resp['status'] = 400
        elif request_resp.status_code == 401:
            resp.update(json.loads(request_resp.text))
            resp['status'] = 401
        elif request_resp.status_code == 403:
            resp.update(json.loads(request_resp.text))
            resp['status'] = 403
        else:
            resp.update(json.loads(request_resp.text))
            resp['status'] = 500
        return resp
        
    def search_contact(self):
        print("\n----------------------In search_contact() ---------------------\n")
        search = self.request.args.get("search", False)
        query = ""
        
        entity_types = [key for key,val in self.bh_config.entity_types.items()]
        final_response = {
            'data' : list(),
            'count' : 0,
            'status': None
        }
        for entity_type in entity_types:
            if not self.bh_config.entity_types.get(entity_type).get('is_contact_entity'):
                continue
            print("\n***************************** Start Searching for {}s ***************************** ".format(entity_type.capitalize()))
            if search:
                query = self.build_free_search_query(entity_type, search)
            else:
                params = self.request.args
                if params.get('bhrest_token'):
                    del params['bhrest_token']
                if params.get('access_token'):
                    del params['access_token']
                query = self.build_auto_search_query(params)
                
            fields = ','.join(self.bh_config.entity_types.get(entity_type).get('response_fields'))
            url = self.bh_config.rest_base_url+self.bh_config.get_entity_url+"?query={}&fields={}"
            url = url.format(self.bh_config.entity_types.get(entity_type).get('name'), query, fields)
            url = url+"&BhRestToken={}".format(self.bhrest_token)
            print("\nURL : {}".format(url))
            resp = self.make_request(url, "GET")

            print("REQUEST RESPONSE : {}".format(resp))

            if resp.get('status') == 200:
                final_response['status'] = 200 
                if resp.get('count') > 0:
                    data = resp.get('data')
                    for rec in data:
                        rec['entity_type'] = entity_type
                    final_response['data'].extend(data)
                    final_response['count'] = final_response['count'] + resp.get('count')
            elif resp.get('status') == 401 or resp.get('status') == 403:
                final_response = resp
                break
            else:
                final_response = resp
            print("******************************** End Search for {}'s ******************************\n".format(entity_type.capitalize()))
            print("\nTotal Response : {}\n".format(final_response))
        return final_response


    def create_contact(self):
        pass

    def create_note(self):
        pass

    def get_notes(self):
        pass

    def create_task(self):
        pass
    
    def get_tasks(self):
        pass

    