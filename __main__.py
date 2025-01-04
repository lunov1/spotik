import asyncio
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import aioschedule as schedule
from listener.listener import Listener

load_dotenv('.env')

session = AiohttpSession()
bot = Bot(
    getenv('BOT_TOKEN'), session,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

listener = Listener(
    bot=bot,
    refresh_token=getenv('SPOTIFY_REFRESH_TOKEN'),
    channel_username=getenv('MUSIC_CHANNEL_ID'),
    client_id=getenv('CLIENT_ID'),
    client_secret=getenv('CLIENT_SECRET'),
    default_img=getenv('DEFAULT_CHANNEL_PHOTO_SRC'),
    default_title=getenv('DEFAUL_CHANNEL_NAME'),
)


async def update_schedule():

    schedule.every(20).minutes.do(listener.update_refresh_token)
    schedule.every(10).seconds.do(listener.update_current_track)

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)


async def main():

    await listener.update_refresh_token()
    await listener.update_current_track()

    await update_schedule()


if __name__ == '__main__':
    asyncio.run(main())
