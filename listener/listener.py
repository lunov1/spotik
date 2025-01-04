import aiohttp

from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramBadRequest


class Listener():
    def __init__(
            self,
            bot: Bot,
            refresh_token: str,
            channel_username: str,
            client_id: str,
            client_secret: str,
            default_img: str,
            default_title: str
    ):

        self.bot = bot
        self.channel_username = channel_username
        self.token = None
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.now_is_playing = None
        self.default_img = default_img
        self.default_title = default_title
        self.last_track_id = None
        self.already_stopped = False

    async def update_refresh_token(self):
        params = {
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://accounts.spotify.com/api/token',
                params=params,
                headers=headers
            ) as response:

                response_json = await response.json()
                self.token = response_json['access_token']

    async def download_track_image(self):

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.track_image_url,
            ) as response:

                with open('track.png', 'wb') as file:
                    file.write(bytes(await response.content.read()))

    async def update_current_track(self):

        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://api.spotify.com/v1/me/player/currently-playing',
                headers=headers
            ) as response:

                if response.status != 200:
                    return

                response_json = await response.json()

                if response_json is None or not response_json['is_playing']:
                    self.now_is_playing = False
                    self.new_tip_message = 'time to relax!'
                    await self.update_channel_bio()
                    self.last_track_id = None
                    return

                elif self.already_stopped is True:
                    self.already_stopped = False

                track = response_json['item']

                self.track_name = track['name']
                self.track_authors = (
                    ', '.join([artist['name'] for artist in track['artists']])
                )
                self.track_image_url = track['album']['images'][0]['url']
                await self.download_track_image()

                if self.last_track_id != track['id']:
                    self.new_tip_message = (
                        f'Next track: <b>{self.track_name}</b>'
                    )
                    await self.update_channel_bio(
                        default=False
                    )

                    self.last_track_id = track['id']

                self.now_is_playing = True

    async def update_channel_bio(self, default=True):
        photo = (
            FSInputFile(self.default_img)
            if default
            else FSInputFile('track.png')
        )
        if default and self.already_stopped is False:
            title = self.default_title

            message = await self.bot.send_message(
                self.channel_username, self.new_tip_message
            )
            await self.bot.set_chat_photo(self.channel_username, photo)
            await self.bot.set_chat_title(self.channel_username, title)

            try:
                await self.bot.delete_messages(
                    self.channel_username,
                    [message.message_id + i for i in range(0, 3)]
                )
            except TelegramBadRequest:
                pass

            self.already_stopped = True

        elif default is False:
            title = '♪ ' + self.track_name + ' - ' + self.track_authors

            message = await self.bot.send_message(
                self.channel_username, self.new_tip_message
            )
            await self.bot.set_chat_photo(self.channel_username, photo)
            await self.bot.set_chat_title(self.channel_username, title)

            try:
                await self.bot.delete_messages(
                    self.channel_username,
                    [message.message_id + i for i in range(0, 3)]
                )
            except TelegramBadRequest:
                pass
