import requests


TOKEN = '6873281226:AAHYloqhMG7uBfYRqTdLjHEszTI_Hm_3ewE'
MSG_TYPE = 'sendMessage'
CHAT_ID = -1001853532039

text = 'С 15:30 до 15:45 будут проводиться технические работы.'

msg = f'https://api.telegram.org/bot{TOKEN}/{MSG_TYPE}?chat_id={CHAT_ID}&text={text}'
telegram_msg = requests.get(msg)