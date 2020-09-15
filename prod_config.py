import os


class Config(object):
    LOG_ENABLE = False
    APP_ID = int(os.environ.get("APP_ID", 6))
    API_HASH = os.environ.get("API_HASH", "bb06d4avfb49gc3eeb1aeb98ae0f571e")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", None)
    USER_SESSION_STRING = os.environ.get("USER_SESSION_STRING", None)
    MONGO_DB_URL = os.environ.get("MONGO_DB_URL", None)
    LOG_MAX_FILE_SIZE = 50000000
    STRIP_FILE_NAMES = os.environ.get("STRIP_FILE_NAMES", None)
    TAMILMV_URL = os.environ.get("TAMILMV_URL", None)
    SUDO_USERS = list(set(
        int(x) for x in os.environ.get("SUDO_USERS", "").split()
    ))
