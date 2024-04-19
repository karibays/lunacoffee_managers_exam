import telebot
from telebot import types
import datetime
from loguru import logger
import pandas as pd
import requests
from google_sheets import GoogleAPI
from save_data_manually import Saver


# The bot's token. You can access it from @BotFather
TOKEN = "6857486215:AAGc3NTseGbEJ96lQmrPZPFw_X54Dpo9sUg"
bot = telebot.TeleBot(TOKEN)

SPREADSHEET_ID = "1-VRDJGJIXXUxmqx4uPs7GCnVPq4Fpi94QCJEtR_cqkM"

# Logging parameters
logger.add("logs/logs.log", rotation="1 day", compression="zip")


# Users' answers
user_data = {}
user_reports = {}

# Decorator
def check_restart(f):
    def inner(message):
        if message.text == '/restart':
            restart(message)
        elif message.text == '/start':
            bot.reply_to(message, "Используйте команду '/restart' для того, чтобы начать заново. Команда /start используется для начало опроса")
            restart(message)
        else:
            f(message)
    return inner

# Static markup
def create_static_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Начать обход')

    return markup

def create_yes_no_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Да', 'Нет')

    return markup

# If user sends '/start', then the bot starts a survey 
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}

    # logging
    logger.info(f"User-{message.chat.id} opened the chat")

    markup = create_static_markup()
    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите 'Начать обход', чтобы начать.", reply_markup=markup)

# If '/restart' was sent, then the bot restarts the survey
def restart(message):
    user_data[message.chat.id] = {}
    send_welcome(message)

# The start of the survey
@bot.message_handler(func=lambda message: message.text == "Начать обход")

@check_restart
def question_1(message):
    user_data[message.chat.id] = {}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for cafe in [
        'Мәңгілік Ел 37',
        'Мәңгілік Ел 40',
        'Мухамедханов',
        'Таха Хусейна 2/1',
        'Тәуелсіздік 34']:

        markup.add(cafe)
    msg = bot.send_message(message.chat.id, "Выберите точку", reply_markup=markup)

    bot.register_next_step_handler(msg, question_2)


@check_restart
def question_2(message):
    text = message.text
    if text in ['Мәңгілік Ел 37', 'Мәңгілік Ел 40', 'Мухамедханов', 'Таха Хусейна 2/1', 'Тәуелсіздік 34']:
        now = (datetime.datetime.now() + datetime.timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
        user_data[message.chat.id]['Дата'] = now

        user_data[message.chat.id]['Точка'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, выберите из списка")
        bot.register_next_step_handler(msg, question_2)
        return    

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, "Ваше имя")

    bot.register_next_step_handler(msg, question_3)


@check_restart
def question_3(message):
    user_data[message.chat.id]['Менеджер'] = message.text
    
    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, "Имя баристы")

    markup = create_yes_no_markup()
    bot.register_next_step_handler(msg, question_4)


@check_restart
def question_4(message):
    user_data[message.chat.id]['Бариста'] = message.text

    bot.send_message(message.chat.id, "1. Тех.состояние помещения")

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, "Вывеска в норме?", reply_markup=markup)

    bot.register_next_step_handler(msg, question_5)


@check_restart
def question_5(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Вывеска в норме'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_5)
        return  
    
    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Освещение зала в норме?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_6)


@check_restart
def question_6(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Освещение зала в норме'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_6)
        return  
    
    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Камеры работают?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_7)


@check_restart
def question_7(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Камеры работают'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_7)
        return  
    
    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Музыка играет?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_8)


@check_restart
def question_8(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Музыка играет'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_8)
        return  
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for cafe in [
        'Плохо',
        'Удовлетворительно',
        'Хорошо',
        'Отлично']:

        markup.add(cafe)

    msg = bot.send_message(message.chat.id, 'Состояние помещения?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_9)


@check_restart
def question_9(message):
    text = message.text
    if text in ['Плохо', 'Удовлетворительно', 'Хорошо', 'Отлично']:
        user_data[message.chat.id]['Состояние помещения'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_9)
        return  
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Нет')
    msg = bot.send_message(message.chat.id, 'Примечания по тех.состоянию помещения\nЕсли примечания есть, то напишите в формате\nПроблема - дата решения (день.месяц.год)', reply_markup=markup)

    bot.register_next_step_handler(msg, comment_1)


@check_restart
def comment_1(message):
    user_data[message.chat.id]['Примечания по тех.состоянию помещения'] = message.text

    bot.send_message(message.chat.id, '2. Внешний вид')

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Футболка баристы в норме?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_10)


@check_restart
def question_10(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Футболка баристы в норме'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_10)
        return  
    

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Кепка надета?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_11)


@check_restart
def question_11(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Кепка надета'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_11)
        return  
    

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Бейдж надет?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_12)


@check_restart
def question_12(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Бейдж надет'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_12)
        return  
    

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Фартук надет?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_13)


@check_restart
def question_13(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Фартук надет'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_13)
        return  
    

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Волосы баристы чистые?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_14)


@check_restart
def question_14(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Волосы баристы чистые'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_14)
        return  
    

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Ногти баристы подстрижены?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_15)


@check_restart
def question_15(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Ногти баристы подстрижены'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_15)
        return  

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Нет')
    msg = bot.send_message(message.chat.id, 'Примечания по внешнему виду барист\nЕсли примечания есть, то напишите в формате\nПроблема - дата решения (день.месяц.год)', reply_markup=markup)

    bot.register_next_step_handler(msg, comment_2)


@check_restart
def comment_2(message):
    user_data[message.chat.id]['Примечания по внешнему виду барист'] = message.text

    bot.send_message(message.chat.id, '3. Чистота зала')    

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Диванчики чистые?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_16)


@check_restart
def question_16(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Диванчики чистые'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_16)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Ножки столов чистые?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_17)


@check_restart
def question_17(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Ножки столов чистые'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_17)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Столы протёрты?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_18)


@check_restart
def question_18(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Столы протёрты'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_18)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Полы чистые?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_19)


@check_restart
def question_19(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Полы чистые'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_19)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Зеркала чистые?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_20)


@check_restart
def question_20(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Зеркала чистые'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_20)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Окна чистые?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_21)


@check_restart
def question_21(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Окна чистые'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_21)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Входная часть чистая?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_22)


@check_restart
def question_22(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Входная часть чистая'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_22)
        return  

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Нет')
    msg = bot.send_message(message.chat.id, 'Примечания по чистоте зала\nЕсли примечания есть, то напишите в формате\nПроблема - дата решения (день.месяц.год)', reply_markup=markup)

    bot.register_next_step_handler(msg, comment_3)


@check_restart
def comment_3(message):
    user_data[message.chat.id]['Примечания по чистоте зала'] = message.text

    bot.send_message(message.chat.id, '4. Чистота уборной')

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Унитаз чистый?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_23)


@check_restart
def question_23(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Унитаз чистый'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_23)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Раковина чистая?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_24)


@check_restart
def question_24(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Раковина чистая'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_24)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Мусор выброшен?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_25)


@check_restart
def question_25(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Мусор выброшен'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_25)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Расходники в наличии?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_26)


@check_restart
def question_26(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Расходники в наличии'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_26)
        return  

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Нет')
    msg = bot.send_message(message.chat.id, 'Примечания по чистоте уборной\nЕсли примечания есть, то напишите в формате\nПроблема - дата решения (день.месяц.год)', reply_markup=markup)

    bot.register_next_step_handler(msg, comment_4)

@check_restart
def comment_4(message):
    user_data[message.chat.id]['Примечания по чистоте уборной'] = message.text

    bot.send_message(message.chat.id, '5. Бар')

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Бар чистый?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_27)


@check_restart
def question_27(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Бар чистый'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_27)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Витрина чистая?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_28)


@check_restart
def question_28(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Витрина чистая'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_28)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'На всех позициях есть ценники?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_29)


@check_restart
def question_29(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['На всех позициях есть ценники'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_29)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Есть ли позиции на стоп листе?', reply_markup=markup)

    bot.register_next_step_handler(msg, question_30)


@check_restart
def question_30(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Есть ли позиции на стоп листе'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, question_30)
        return  

    markup = create_yes_no_markup()
    msg = bot.send_message(message.chat.id, 'Продукция проротирована', reply_markup=markup)

    bot.register_next_step_handler(msg, finish_survey)


@check_restart
def finish_survey(message):
    text = message.text
    if text in ['Да', 'Нет']:
        user_data[message.chat.id]['Ротация продукции'] = message.text
    else:
        msg = bot.send_message(message.chat.id, "Пожалуйста, ответьте Да или Нет")
        bot.register_next_step_handler(msg, finish_survey)
        return  

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Нет')
    msg = bot.send_message(message.chat.id, 'Примечания по бару\nЕсли примечания есть, то напишите в формате\nПроблема - дата решения (день.месяц.год)', reply_markup=markup)

    bot.register_next_step_handler(msg, comment_5)


@check_restart
def comment_5(message):
    user_data[message.chat.id]['Примечания по бару'] = message.text

    markup = create_static_markup()
    msg = bot.send_message(message.chat.id, 'Обход окончен!', reply_markup=markup)

    # Saving data to google sheets
    logger.info("Trying to save user data to the google sheets...")

    values = [list(user_data[message.chat.id].values())]

    Saver().save_user_data_manually(values)
    notify_telegram_group(user_data[message.chat.id])

    save_survey_data_to_google_sheets(message.chat.id) 
    

def save_survey_data_to_google_sheets(chat_id):
    values = [list(user_data[chat_id].values())]

    if not GoogleAPI().check_token_expicicy_and_refresh():
        logger.info("Token is valid")
    else:
        logger.error("Failed to refresh the token while saving user data to google sheets")
        return

    try: 
        GoogleAPI().append_values(
            spreadsheet_id=SPREADSHEET_ID,
            range_name='A:Z',
            value_input_option="USER_ENTERED",
            values=values,
        ) # type: ignore
    except:
        logger.error("Failed to save the data to google sheets!")



def notify_telegram_group(user_data):
    MSG_TYPE = 'sendMessage'
    CHAT_ID = -4182366162

    keys1 = [
    '1. Тех.состояние помещения',
    'Вывеска в норме',
    'Освещение зала в норме',
    'Камеры работают',
    'Музыка играет',
    'Состояние помещения'
    ]

    keys2 = [
        '2. Внешний вид',
        'Футболка баристы в норме',
        'Кепка надета',
        'Бейдж надет',
        'Фартук надет',
        'Волосы баристы чистые',
        'Ногти баристы подстрижены'
    ]

    keys3 = [
        '3. Чистота зала',
        'Диванчики чистые',
        'Ножки столов чистые',
        'Столы протёрты',
        'Полы чистые',
        'Зеркала чистые',
        'Окна чистые',
        'Входная часть чистая'
    ]

    keys4 = [
        '4. Чистота уборной',
        'Унитаз чистый',
        'Раковина чистая',
        'Мусор выброшен',
        'Расходники в наличии'
    ]

    keys5 = [
        '5. Бар',
        'Бар чистый',
        'Витрина чистая',
        'На всех позициях есть ценники',
        'Есть ли позиции на стоп листе',
        'Ротация продукции'
    ]

    value1 = value2 = value3 = value4 = value5 = ''

    selected = [k for k in user_data if user_data[k] == 'Нет']
    for i in selected:
        if i in keys1:
            value1 = value1 + i + ': ' + user_data[i] + '\n'

        if i in keys2:
            value2 = value2 + i + ': ' + user_data[i] + '\n'

        if i in keys3:
            value3 = value3 + i + ': ' + user_data[i] + '\n'

        if i in keys4:
            value4 = value4 + i + ': ' + user_data[i] + '\n'

        if i in keys5:
            value5 = value5 + i + ': ' + user_data[i] + '\n'


    # Initialize the text
    text = f"Дата: {user_data.get('Дата', '')}\n" \
        f"Точка: {user_data.get('Точка', '')}\n" \
        f"Менеджер: {user_data.get('Менеджер', '')}\n" \
        f"Бариста: {user_data.get('Бариста', '')}\n\n"

    # Define the data including section notes and comments
    data = [
        (value1, keys1, "1. Техническое состояние помещения", user_data.get("Примечания по тех.состоянию помещения", "")),
        (value2, keys2, "2. Внешний вид", user_data.get("Примечания по внешнему виду барист", "")),
        (value3, keys3, "3. Чистота зала", user_data.get("Примечания по чистоте зала", "")),
        (value4, keys4, "4. Чистота уборной", user_data.get("Примечания по чистоте уборной", "")),
        (value5, keys5, "5. Бар", user_data.get("Примечания по бару", ""))
    ]

    # Iterate through data to construct text
    for value, keys, section_note, comments in data:
        if value:
            text += f"{section_note}\n{value}"
            if comments:  # Append comments if available
                text += f"Примечания: {comments}\n\n"

    msg = f'https://api.telegram.org/bot{TOKEN}/{MSG_TYPE}?chat_id={CHAT_ID}&text={text}&parse_mode=Markdown'

    try:
        telegram_msg = requests.get(msg)
        logger.info("The admins have been notified.")
    except Exception as e:
        logger.error(f"Failed to notify the admins: {e}")


# --------------------START--------------------
import os, sys
from requests.exceptions import ConnectionError, ReadTimeout

try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
except (ConnectionError, ReadTimeout) as e:
    sys.stdout.flush()
    os.execv(sys.argv[0], sys.argv)
else:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)