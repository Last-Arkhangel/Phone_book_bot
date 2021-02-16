# -*- coding: utf-8 -*-
import os

# если выкладываем на heroku
WEBHOOK_HOST = ''

# телеграм может работать с портами 443, 80, 88 или 8443
WEBHOOK_PORT = '8443'

# In some VPS you may need to put here the IP addr
WEBHOOK_LISTEN = '192.168.1.1'  

# Path to the ssl certificate
WEBHOOK_SSL_CERT = 'server.crt'  

# Path to the ssl private key
WEBHOOK_SSL_PRIV = 'server.key'  

# Path that telegram sends updates
WEBHOOK_PATH = "/pbb/"

# Bot version
VERSION = '1.1.1 від 08.01.2021'

# Admin id: my
ADMINS_ID = 112233444

#not admin
NO_ADMIN = "Ви не адміністратор 👿!"

# Telegram Bot token
BOT_TOKEN = ''

# Base folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Interval to polling telegram servers (Uses if USE_WEBHOOK sets False)
POLLING_INTERVAL = 2

# Timeout to polling telegram servers
POLLING_TIMEOUT = 25

# Debug 'True sets False'
WEBHOOK_DEBUG = False

# Keyboard buttons
KEYBOARD = {
    'START': '/start',
    'HELP': '/help',
}