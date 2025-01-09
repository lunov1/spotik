import asyncio

from os import getenv
from os.path import exists
from dotenv import load_dotenv

from colorama import Fore, init

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import aioschedule as schedule
from listener.listener import Listener
from listener.getter import start, IP

import socket

load_dotenv('.env')

init()

hostname = socket.gethostname()


async def update_schedule(listener):

    schedule.every(20).minutes.do(listener.update_refresh_token)
    schedule.every(10).seconds.do(listener.update_current_track)

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)


async def main():

    default_channel_photo_src = getenv('DEFAULT_CHANNEL_PHOTO_SRC')
    bot_token = getenv('BOT_TOKEN')
    music_channel = getenv('MUSIC_CHANNEL_ID')
    client_id = getenv('CLIENT_ID')
    client_secret = getenv('CLIENT_SECRET')
    client_refresh_token = getenv('SPOTIFY_REFRESH_TOKEN')
    default_channel_photo_src = getenv('DEFAULT_CHANNEL_PHOTO_SRC')
    default_channel_name = getenv('DEFAULT_CHANNEL_NAME')

    print(
        f'{Fore.LIGHTGREEN_EX}Spotik{Fore.RESET} - translate your tracks '
        f'in {Fore.CYAN}Telegram Profile{Fore.RESET}'
    )
    action = input(
        'What you want to do?\n\n'
        '1 - Start Spotik\n' '2 - Get Refresh Token\n\n> '
    )

    while not action.isdigit():
        action = input(
            'What you want to do?\n\n'
            '1 - Start Spotik\n' '2 - Get Refresh Token\n\n> '
        )
    action = int(action)

    if action == 2:
        dependent = (
            client_id, client_secret
        )

        if any([True for attr in dependent if attr == '']):
            print(
                f'{Fore.LIGHTRED_EX}problem | {Fore.RESET}'
                'One of the variables (client_id, client_secret) '
                'in the file ".env" is not filled in'
            )
            print(
                'You need to create you app via https://developer.spotify.com/dashboard'
                ' and get client_id, client_secret from this app'
            )
            return
        print(
            'To work with Sportik, you will need to'
            'log in to https://developer.spotify.com/dashboard, '
            'then in the settings, '
            f'in the Redirect URIs, add: \nhttp://{IP}:8888/callback'
        )
        input("Write anything if you've done all the steps above: ")
        return True

    if not exists(default_channel_photo_src) and action == 1:
        print(
            f'{Fore.LIGHTRED_EX}problem | {Fore.RESET}Your picture '
            f'was not found on the path {default_channel_photo_src}'
        )
        return

    dependent = (
        bot_token, music_channel, client_id, client_secret,
        client_refresh_token, default_channel_name
    )

    if any([True for attr in dependent if attr == '']):
        print(
            f'{Fore.LIGHTRED_EX}problem | {Fore.RESET}One of the variables '
            'in the file ".env" is not filled in'
        )
        return

    session = AiohttpSession()
    bot = Bot(
        getenv('BOT_TOKEN'), session
    )

    listener = Listener(
        bot=bot,
        refresh_token=client_refresh_token,
        channel_username=music_channel,
        client_id=client_id,
        client_secret=client_secret,
        default_img=default_channel_photo_src,
        default_title=default_channel_name,
    )

    print('Spotik is started!')

    await listener.update_refresh_token()
    await listener.update_current_track()

    await update_schedule(listener)


if __name__ == '__main__':
    result = asyncio.run(main())

    if result is True:
        start()
