import logging
import os
from logging.handlers import RotatingFileHandler

import pymongo
from telethon import events, TelegramClient

from forward.__main__ import LOGGER
from prod_config import Config

ENV = bool(os.environ.get('ENV', False))

if ENV:
    from prod_config import Config
else:
    from dev_config import Development as Config

bot = TelegramClient("ForwardBot", api_id=Config.APP_ID,
                     api_hash=Config.API_HASH).start(bot_token=Config.BOT_TOKEN)
mongo_client = pymongo.MongoClient(Config.MONGO_DB_URL)
db = mongo_client.samaydb
forward_map = dict()

def update_forward_map():
    global forward_map
    for forid in list(db.forwards.find({})):
        forward_map[forid['_id']] = forid['forwardTo']

update_forward_map()

@bot.on(events.NewMessage(pattern='/setforward',from_users=list(Config.SUDO_USERS)))
async def seforward(event):
    command = event.text.split()
    if len(command) > 2 :
        db.forwards.find_one_and_update({'_id': command[1]}, {'$set': {'_id': command[1], 'forwardTo': command[2]}}, upsert=True)
        update_forward_map()
        await event.respond(f"Forward set {command[1]} ==> {command[2]}")
        raise events.StopPropagation
    else :
        await event.respond("Please Enter Source and Destination chat Ids Ex:/setforward 123456 789101")


@bot.on(events.NewMessage(pattern='/getid'))
async def getid(event):
    await event.respond(f'{event.message.chat_id}')
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/removeforward',from_users=list(Config.SUDO_USERS)))
async def removeforward(event):
    command = event.text.split()
    if len(command) > 1:
        db.forwards.delete_one({'_id': f'{command[1]}'})
        update_forward_map()
        await event.respond(f"removed forward config for {command[1]}")
    else:
        await event.respond("Please Enter chat id to remove forward Ex:/removeforward 123456")
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/help'))
async def help(event):
    await event.respond("Step 1: Add this Bot to your group or Channel as admin\n"
                        "Step 2: Get ids from channel or group using /getid command from respective channel or group "
                        "Step 3: By using those ids configure forwards using following Commands"
                        "\n /setforward source-channel-id destination-channel-id (Ex:/setforward 123456 789101)"
                        "\n /removeforward source-channel-id (Ex:/setforward 123456)")
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/start'))
async def help(event):
    await event.respond("Step 1: Add this Bot to your group or Channel as admin\n"
                        "Step 2: Get ids from channel or group using /getid command from respective channel or group "
                        "Step 3: By using those ids configure forwards using following Commands"
                        "\n /setforward source-channel-id destination-channel-id (Ex:/setforward 123456 789101)"
                        "\n /removeforward source-channel-id (Ex:/setforward 123456)")
    raise events.StopPropagation


@bot.on(events.NewMessage)
async def echo(event):
    #user = await event.client.get_entity(-1001297647039)
    if  event.message.document is not None or event.message.video is not None and f'{event.message.chat_id}' in forward_map :
        user = await event.client.get_entity(int(forward_map[f'{event.message.chat_id}']))
        print(f">> get it {event.text}")
        await event.client.send_message(user, event.message)


def main():
    if Config.BOT_TOKEN is not None:

        global bot
        bot.run_until_disconnected()
    else:
        LOGGER.error("BOT_TOKEN is mandatory to start session"
                     "\n please Enter BOT_TOKEN and restart")
