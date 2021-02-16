#!/usr/bin/env python
# -*- coding: utf-8 -*-
import users
import settings
import telebot, xlrd, openpyxl, datetime
from openpyxl import load_workbook
from settings import KEYBOARD
import flask
from flask_sslify import SSLify

WEBHOOK_URL_BASE = "https://{}:{}".format(settings.WEBHOOK_HOST, settings.WEBHOOK_PORT)

bot = telebot.TeleBot(settings.BOT_TOKEN, threaded=True)

# удаляем предыдущие вебхуки, если они были
bot.remove_webhook()

# ставим новый вебхук = Слышь, если кто мне напишет, стукни сюда — url
bot.set_webhook(url=WEBHOOK_URL_BASE + settings.WEBHOOK_PATH)

app = flask.Flask(__name__)
sslify = SSLify(app)

with open('users.py', 'r') as fp:
    user_ids = [int(l) for l in fp.readlines()]

@bot.message_handler(func=lambda message: message.chat.id not in user_ids)
def access_msg(message):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(KEYBOARD['START'])
    name = message.chat.first_name + ' ' + (message.chat.last_name or '')
    dtn = datetime.datetime.now()
    botlogfile = open('bot_td_logs.txt', 'a', encoding='utf-8')
    print(dtn.strftime("[%d-%m-%Y %H:%M:%S]:"), "Доступ Bot 🚫 ({}, @{}, id:{}) -> {}".format(name, message.chat.username, message.from_user.id, message.text), file=botlogfile)
    botlogfile.close()
    msg = "<b>ДОСТУП ЗАБОРОНЕНО ТІЛЬКИ ДЛЯ ВИКЛАДАЧІВ </b>\n\n"
    
    bot.send_message(message.chat.id, text=msg, parse_mode='HTML', reply_markup=kb)

@bot.message_handler(commands=['start'])
def start_handler(message):
    name = message.chat.first_name + ' ' + (message.chat.last_name or '')    
    msg = "Вітаю, {} 😊. \n" \
          "Це Телефонний довідник , версія бота {} р.\n\n".format(name, settings.VERSION)
    kb = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, text=msg, parse_mode='HTML', reply_markup=kb)

@bot.message_handler(commands=['help'])
def get_text_messages(message):
    msg = "Щоб здійснит пошук ведіть <b>прізвище</b> або <b>ім'я</b> або <b>місяць народження</b>, повністю з великої літері та на українській мові. \n"
    
    bot.send_message(message.from_user.id, text=msg, parse_mode='HTML')

@bot.message_handler(commands=['log'])
def text(message):
    if message.chat.id == settings.ADMINS_ID:
        file = open('bot_td_logs.txt', 'rb')
        bot.send_document(message.chat.id, file)
    else:
        bot.send_message(message.chat.id, settings.NO_ADMIN)

client_status = {}
def save(data):
    with open('users.py', 'a') as id_file:
        id_file.write(data)

@bot.message_handler(commands=['add_user'])
def add_user(message):
    if message.chat.id == settings.ADMINS_ID:
        client_id = message.from_user.id
        client_status[client_id] = 'wait_for_data'
        bot.send_message(chat_id=client_id, text='Ведіть ID користувача: ')
    else:
        bot.send_message(message.chat.id, settings.NO_ADMIN)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.chat.id == settings.ADMINS_ID:
        client_id = message.from_user.id
        if client_id in client_status and client_status[client_id] == 'wait_for_data':
            save(message.text + '\n') # сохраняем данные
            bot.send_message(chat_id=client_id, text="Ви додали USER ID: {}!".format(message.text))
            del client_status[client_id]
    else:
        dtn = datetime.datetime.now()
        botlogfile = open('bot_td_logs.txt', 'a', encoding='utf-8')
        print(dtn.strftime("[%d-%m-%Y %H:%M:%S]:"), "Пошук ({}, id:{}) -> {}".format(message.chat.first_name + ' ' + (message.chat.last_name or ''), message.from_user.id, message.text), file=botlogfile)
        botlogfile.close()
    
        rb = xlrd.open_workbook(r'Телефонний довідник.xlsx')
        sheet = rb.sheet_by_index(0)
        rows = [sheet.row_values(rownum) for rownum in range(1, sheet.nrows)]
        orders = [item for item in rows if item[3] == message.text] + [item for item in rows if item[4] == message.text] + [item for item in rows if item[8] == message.text] + [item for item in rows if item[9] == message.text] + [item for item in rows if item[10] == message.text] + [item for item in rows if item[13] == message.text]

        if len(orders) == 0:
            bot.send_message(message.from_user.id, "Інформацію за вашим запитом  <b>{}</b>  ⛔️ не знайдено".format(message.text), parse_mode='HTML')
        else:
            for order in orders:
                
                bot.send_message(message.from_user.id, "<i>👤 <u>ПІБ</u></i>:  <b>{} {} {}</b>\n" \
                                                       "<i>📅 <u>Дата народження</u></i>:  <b>{}</b>\n" \
                                                       "<i>📑 <u>Підрозділ</u></i>:  <b>{}</b>\n" \
                                                       "<i>🖋 <u>Посада</u></i>:  <b>{}</b>\n" \
                                                       "<i>🚪 <u>Кабінет</u></i>:  <b>{}</b>\n" \
                                                       "<i>📞 <u>Тел. внутр.</u></i>:  {}\n" \
                                                       "<i>☎️ <u>Тел. місцев.</u></i>:  {}\n" \
                                                       "<i>📱 <u>Тел. моб. 1</u></i>:  {}\n" \
                                                       "<i>📱 <u>Тел. моб. 2</u></i>:  {}\n" \
                                                       "<i>📝 <u>Прийняття</u></i>:  <b>{}</b>\n" \
                                                       "<i>🛑 <u>Звільнення</u></i>:  <b>{}</b>\n".format(order[3], order[4], order[5], order[6], order[0], order[2], order[1], order[7], order[8], order[9], order[10], order[11], order[12]), parse_mode='HTML')



# пустая главная страничка для проверки
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'

# обрабатываем вызовы вебхука = функция, которая запускается, когда к нам постучался телеграм 
@app.route(settings.WEBHOOK_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

# Start polling server
#bot.polling(interval=settings.POLLING_INTERVAL, timeout=settings.POLLING_TIMEOUT, none_stop=True)

# Start flask server
app.run(host=settings.WEBHOOK_LISTEN,
        port=settings.WEBHOOK_PORT,
        ssl_context=(settings.WEBHOOK_SSL_CERT, settings.WEBHOOK_SSL_PRIV),
        debug=settings.WEBHOOK_DEBUG)