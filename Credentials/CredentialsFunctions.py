from Credentials._local_resources import _local_credentials


def create_authorization_url(user_id:str)->str:
    """:returns authorization url"""
    _local_credentials.auth_into_db(user_id)
    return 'https://kairosai.pl'

def check_user_credentials(user_id:str)->bool:
    """:returns True if user_token exists and is valid else False"""
    return _local_credentials.check_user_credentials_from_db(user_id)
def get_user_credential(user_id:str)->dict | None:
    """:returns user credentials if exists else None"""
    return _local_credentials.get_credentials_from_db(user_id)

if __name__ == '__main__':
    from GoogleAPI import GoogleCalendarAPI
    #create_authorization_url('6')
    x = get_user_credential('6')
    if check_user_credentials('6'):
        for k,e in x.items():
            print(f'{k}: {e}')
    e = GoogleCalendarAPI.getEvents(x)
    for event in e:
        print(event)