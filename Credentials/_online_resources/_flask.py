import flask
import requests
import json
import urllib.parse
import Models
class Meta:
    scope = 'https://www.googleapis.com/auth/calendar'
    client_id =''
    project_id =''
    auth_uri =''
    token_uri =''
    auth_provider_x509_cert_url=''
    client_secret=''
    redirect_uris=''
    javascript_origins =''
    def __init__(self,SECRET_CLIENT_PATH):
        d = dict()
        with open(SECRET_CLIENT_PATH,'r') as f:
            d = json.load(f)
        d = d['web']
        for k,v in d.items():
            if not hasattr(self, k):
                raise RuntimeError(f'non valid json {k}')
            setattr(self,k,v)
    def test(self):
        for k,v in self.__dict__.items():
            print(k,v)
m = Meta('client_secret.json')

app = flask.Flask(__name__)

@app.route('/')
def index():
   return 'dzien dobry'

@app.route('/auth',methods=['GET'])
def get_auth():
    user_id = flask.request.args.get('state')
    if user_id is None:
        return flask.Response("Missing state", status=400)
    params = {
        "client_id": m.client_id,
        "redirect_uri": m.redirect_uris[0],
        "scope": m.scope,
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
        "state": user_id
    }
    auth_url = f"{m.auth_uri}?{urllib.parse.urlencode(params)}"
    return flask.redirect(auth_url)
@app.route('/auth/callback',methods=['GET','POST'])
def callback():
    auth_code = flask.request.args.get("code")
    user_id = flask.request.args.get("state")
    scope = flask.request.args.get("scope")

    data = {
        "code": auth_code,
        "client_id": m.client_id,
        "client_secret": m.client_secret,
        "redirect_uri": m.redirect_uris[0],
        "grant_type": "authorization_code"
    }

    response = requests.post(m.token_uri, data=data)
    if response.status_code != 200:
        error = flask.request.args.get("error")
        if error is None:
            return flask.Response(f'request.post from {m.token_uri} failed with status {response.status_code}', status=response.status_code)
        else:
            return flask.Response(f'error: {error}', status=response.status_code)

    data_token = convert_response(user_id,scope,response.json())
    if data_token is None:
        return flask.Response(f'non valid reponse {response.json()}', status=400)
    print('adding token:')
    for k,v in data_token.items():
        print(k,v)
    Models.user_google_token.insert(**data_token).on_conflict_replace().execute()
    return flask.Response('Działa!', status=200)

def convert_response(user_id,scope,d:dict):
    try:
        result = dict()
        result['id'] = user_id
        result['token'] = d['access_token']
        result['refresh_token'] = d['refresh_token']
        result['token_uri'] = m.token_uri
        result['client_id'] = m.client_id
        result['client_secret'] = m.client_secret
        result['scopes'] = scope
        result['universe_domain'] = ''
        result['account'] = ''
        result['expiry'] = d['expires_in']
    except Exception as e:
        print(e)
        return None
    return result
@app.route('/db',methods=['GET'])
def get_record_db():
    data = flask.request.json()
    if data is None:
        return flask.Response('No data', status=400)
    if 'token' not in data:
        return flask.Response('Missing token', status=400)
if __name__ == '__main__':
    app.run(port=5000,debug=True)
