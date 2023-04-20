import re
import requests
from itsdangerous import URLSafeTimedSerializer
from config import Config

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def send_message(self, text):
        text = text.replace('_',' ')
        params = {'chat_id': '344130137', 'text': text, 'parse_mode': 'Markdown'}
        method = 'sendMessage'
        try:
            resp = requests.post(self.api_url + method, params)
        except Exception as e:
            print('Telegram Error: ', e)
        return resp


def formaturl(url):
    if not re.match('(?:http|https)://', url):
        return 'https://{}'.format(url)
    return url



def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    return serializer.dumps(email, salt=Config.SECURITY_PASSWORD_SALT)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=Config.SECURITY_PASSWORD_SALT,
            max_age=expiration
        )
    except:
        return False
    return email