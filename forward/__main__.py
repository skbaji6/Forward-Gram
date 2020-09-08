import logging
import os
from logging.handlers import RotatingFileHandler

import pymongo
from telethon import TelegramClient

from forward import core

ENV = bool(os.environ.get('ENV', False))

if ENV:
    from prod_config import Config
else:
    from dev_config import Development as Config

# Log Configuration
if os.path.exists("Forward-Gram.log"):
    with open("Forward-Gram.log", "r+") as f_d:
        f_d.truncate(0)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            "Forward-Gram.log",
            maxBytes=Config.LOG_MAX_FILE_SIZE,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("telethon").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

# mongo_client = pymongo.MongoClient(Config.MONGO_DB_URL)
# db = mongo_client.samaydb

if __name__ == '__main__':
    core.main()
