from peewee import *
from db import db

class user_google_token(Model):
    id = CharField(primary_key=True)
    token = CharField()
    refresh_token = CharField(null=True)
    token_uri = CharField()
    client_id = CharField()
    client_secret = CharField()
    scopes = TextField()
    universe_domain = CharField()
    account = CharField(null=True)
    expiry = TextField()
    class Meta:
        database = db

if __name__ == '__main__':
    if input('do you want to create user_google_token? (y/n) ') == 'y':
        db.create_tables([user_google_token], safe=True)

    from GoogleAPI import get_credentials
    import json
    cred = get_credentials.get_credentials()

    d = {'id':'5'}
    cred = json.loads(cred.to_json())
    d.update(cred.items())
    user_google_token.create(**d)