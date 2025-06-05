import flask
import Models
import json
app = flask.Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    return 'hello world'

@app.route('/auth',methods=['POST'])
def post_auth():
    user_id = flask.request.form.get('state')
    data = flask.request.get_json()
    if data is None or user_id is None:
        return flask.Response(status=400)
    data = json.loads(data)
    user = Models.user_google_token.get(Models.user_google_token.id==user_id)
    if user is None:
        return flask.Response(status=404)


if __name__ == '__main__':
    app.run(port=5000,debug=True)