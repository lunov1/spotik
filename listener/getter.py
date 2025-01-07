import webbrowser

import aiohttp
import asyncio

from aiohttp import web
from colorama import Fore

import logging
from os import getenv

logging.basicConfig(level=logging.ERROR)

REDIRECT_URL = 'http://127.0.0.1:8888/callback'
CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')


async def callback(request):
    auth_code = request.rel_url.query.get('code')
    token = await get_access_token(
        CLIENT_ID, CLIENT_SECRET, auth_code, REDIRECT_URL
    )

    print(
        "Refresh Token (paste it into .env in SPOTIFY_REFRESH_TOKEN=)"
        "(CTRL +C to finish executing this code):\n"
        f'{Fore.BLUE}{token}{Fore.RESET}'
    )

    await request.app.shutdown()
    return web.Response(text="Refresh Token received, you can close the tab.")


async def get_access_token(client_id, client_secret, code, redirect_uri):
    token_url = 'https://accounts.spotify.com/api/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(token_url, data=data) as response:
            if response.status == 200:
                access_token = (await response.json()).get('refresh_token')
                return access_token
            else:
                raise Exception(
                    "Token receipt error: ",
                    response.status,
                    await response.text()
                )


async def get_authorization_code(client_id, redirect_uri):
    auth_url = (
        f'https://accounts.spotify.com/authorize'
        f'?client_id={client_id}'
        '&response_type=code'
        f'&redirect_uri={redirect_uri}'
        '&scope=user-read-currently-playing'
    )
    webbrowser.open(auth_url)
    print("Waiting for the authorization code to be received...")


async def init_app():
    app = web.Application()
    app.router.add_get('/callback', callback)
    return app


async def main():
    await get_authorization_code(CLIENT_ID, REDIRECT_URL)
    app = await init_app()
    return app


def start():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        app = loop.run_until_complete(main())
        web.run_app(app, port=8888)
    except KeyboardInterrupt:
        pass
