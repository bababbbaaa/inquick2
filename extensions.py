import re
import requests


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

class Mailer:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
