import requests
from flask import current_app


def send_msg(text):
    url_req = f"https://api.telegram.org/bot{current_app.config['ALERTS_BOT_TOKEN']}/sendMessage?chat_id={current_app.config['ALERTS_BOT_CHATID']}&text={text}"
    result = requests.get(url_req)

    return result.json()
