import json

import requests

URL_app = 'https://kairosai.pl'
security_token = '0PHVCsD5u08geRLgcBhV3udq2mURwgrTcV8W2ZYdGEZcj754f4s17SMSSTyGTxmT'
def _request(user_id,security_token)->dict | None:
    data = {'security_token': security_token, 'user_id': user_id}
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.get(f"https://kairosai.pl/db", data=json.dumps(data), headers=headers)
        if r is None:
            return None
        else:
            return r.json()
    except requests.exceptions.RequestException:
        return None

def create_authorization_url(user_id:str)->str:
    """:returns authorization url"""
    return f'{URL_app}/auth?state={user_id}'

def check_user_credentials(user_id:str)->bool:
    """:returns True if user_token exists and is valid else False"""
    r = _request(user_id, security_token)
    return r is not None
def get_user_credential(user_id:str)->dict | None:
    """:returns user credentials if exists else None"""
    return _request(user_id, security_token)

if __name__ == '__main__':
    from GoogleAPI import GoogleCalendarAPI
    print(create_authorization_url('2257'))
    input('czekam')
    if check_user_credentials('2257'):
        r = get_user_credential('2257')
        e = GoogleCalendarAPI.getEvents(r)
        for event in e:
            print(event)
    else:
        print('nie dziala')