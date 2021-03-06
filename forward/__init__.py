import logging
import os
import pymongo

from logging.handlers import RotatingFileHandler
from telethon import TelegramClient
from telethon.sessions import StringSession

ENV = bool(os.environ.get('ENV', False))

if ENV:
    from prod_config import Config
else:
    from dev_config import Development as Config

config = Config

# Log Configuration
if os.path.exists("Forward-Gram.txt"):
    with open("Forward-Gram.txt", "r+") as f_d:
        f_d.truncate(0)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "Forward-Gram.txt",
            maxBytes=Config.LOG_MAX_FILE_SIZE,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("telethon").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

bot = TelegramClient("ForwardBot", api_id=Config.APP_ID,
                     api_hash=Config.API_HASH).start(bot_token=Config.BOT_TOKEN)
session_string = str(Config.USER_SESSION_STRING)
user = TelegramClient(StringSession(session_string), api_id=Config.APP_ID,
                     api_hash=Config.API_HASH).start()
mongo_client = pymongo.MongoClient(Config.MONGO_DB_URL)
db = mongo_client.samaydb
