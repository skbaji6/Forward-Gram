import os
import re

import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from urllib.parse import parse_qs

from telethon.tl.types import Message

from forward import bot, config, user
from forward import db
from forward import LOGGER
from forward.utils import get_next_value

no_of_posts_to_read = 5


def init():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(tmv_scrape, 'interval', minutes=60, id='tmv_scrape_job', args=[db])
    scheduler.add_job(post_to_leech, 'interval', minutes=30, id='post_to_leech_job', args=[bot, db])
    scheduler.start()


async def tmv_scrape(db):
    sub_urls = []

    response = requests.get(config.TAMILMV_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    tag = soup.find('div', {'class': 'ipsWidget_inner'})
    ptags = tag.find_all("p")
    link_info = dict()
    #magnets = set()
    torrents = set()
    post_count = 0
    for chi in ptags[1].children:
        if chi.name == 'br':
            # Every post is separated by <br> tag so when <br> tag appears will consider as a single post read is complete
            post_count = post_count + 1
            link_info['urls'] = list(set(sub_urls))
            for link in link_info['urls']:
                # Reading the Magnet links and torrent files and Post Date from the URL
                magents_res,torrents_res, time = await get_magnet_links(link)
                #magnets.update(magents_res)
                torrents.update(torrents_res)
            global no_of_posts_to_read
            if post_count == no_of_posts_to_read:
                break
        else:
            strong_tag = chi.find('strong')
            if not isinstance(strong_tag, int) and strong_tag is not None and len(strong_tag) > 0:
                atag = strong_tag.find('a')
                if atag is not None and len(atag) > -1:
                    sub_urls.append(atag.attrs['href'])

    for magnet in list(torrents):
        db_magnet = db.magnets.find_one({'magnet': magnet})
        if db_magnet is None :
            LOGGER.info("New Torrent Found Inserting into DB")
            db.magnets.find_one_and_update({'magnet': magnet},
                                           {'$setOnInsert': {'_id': await get_next_value(db, 'magnets_collection'),
                                                             'magnet': magnet, 'isProcessed': False}},
                                           upsert=True)


async def get_magnet_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    magnets = set()
    torrents = set()
    for ptag in soup.find_all('p'):
        for atag in ptag.find_all('a'):
            href = atag.get('href', None)
            if href and (href.startswith("magnet")):
                magnets.add(href)
    for atorrent in soup.find_all('a', {'class': 'ipsAttachLink'}):
        span = atorrent.find('span')
        if (span is not None and "torrent" in span.text) or "torrent" in atorrent.text:
            href = atorrent.get('href', None)
            if href and "attachment" in href:
                torrents.add(href)
    header_division = soup.find('div', {'class': 'ipsPageHeader ipsClearfix'})
    time = header_division.find('time').get('datetime')

    return magnets,torrents,time


async def post_to_leech(bot, db):
    last_processed_id_from_db = db.lastProcessedMagnet.find_one({"_id": 'tamilmv'})
    magnets = db.magnets.find({'_id': {'$gt': last_processed_id_from_db['value'], '$lt': last_processed_id_from_db['value'] + 5}});
    last_processed_id=last_processed_id_from_db
    target_user = None
    if magnets is not None and magnets.count() > 0:
        target_user = await user.get_entity(-1001297647039)
        sent_img_message: Message =await user.send_message(target_user, file="moviez_trends.jpg")
        await sent_img_message.reply(f"/savethumbnail")
    for mag in magnets:
        #parsed = urlparse.urlparse(mag['magnet'])
        #print(parse_qs(parsed.query)['dn'][0].replace('www.1TamilMV.life - ',''))
        #file_name=parse_qs(parsed.query)['dn'][0]
        downloaded_file=await download_from_url(mag['magnet'])
        file_name = downloaded_file
        if config.STRIP_FILE_NAMES:
            for fname in config.STRIP_FILE_NAMES.split("|"):
                file_name = file_name.replace(fname, "").strip()
            file_name = file_name.replace("Â", "").strip()
            file_name = file_name.replace(".torrent", "").strip()
        LOGGER.info(f"Processing id {mag['_id']} with name {file_name}")
        #sent_message: Message = await user.send_message(target_user, f"{mag['magnet']}")
        sent_message: Message = await user.send_message(target_user, file=downloaded_file)
        await sent_message.reply(f"/gtleech rename {file_name}")
        os.remove(downloaded_file)
        last_processed_id = mag['_id']
    if not last_processed_id_from_db == last_processed_id:
        db.lastProcessedMagnet.find_one_and_update({'_id': 'tamilmv'},
                                                     {'$set': {'value': last_processed_id}},
                                                     upsert=True)


async def download_from_url(url):
    r = requests.get(url)
    file_name = re.findall("filename=\"(.+)\"", r.headers["Content-Disposition"])[0]
    open(file_name, 'wb').write(r.content)
    return file_name
