from aiohttp import web
import aiohttp

import asyncio

from colorama import Fore

import logging
from os import getenv
from dotenv import load_dotenv

import socket

logging.basicConfig(level=logging.ERROR)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception as e:
        ip_address = str(e)
    finally:
        s.close()

    return ip_address


load_dotenv('../.env')

IP = get_local_ip()
REDIRECT_URL = f'http://{IP}:8888/callback'
CLIENT_ID = getenv('CLIENT_ID')
CLIENT_SECRET = getenv('CLIENT_SECRET')


async def callback(request):
    auth_code = request.rel_url.query.get('code')
    if not auth_code:
        return web.Response(text="Authorization code not found.", status=400)

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
                error_message = await response.text()
                raise Exception(
                    f"Token receipt error: {response.status} - {error_message}"
                )


async def get_authorization_code(client_id, redirect_uri):
    auth_url = (
        f'https://accounts.spotify.com/authorize'
        f'?client_id={client_id}'
        '&response_type=code'
        f'&redirect_uri={redirect_uri}'
        '&scope=user-read-currently-playing'
    )
    print(f"Follow the link in any browser:\n{auth_url}\n")
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
        web.run_app(app, host=IP, port=8888)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    start()
