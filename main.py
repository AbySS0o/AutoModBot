import logging
import datetime
import itertools
import asyncio
import aiogram
import pymorphy2
import os
import json
import string
import pathlib

from word import morph
from os import path
from pathlib import Path
from modcommands import mute_command, unmute_command

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import MessageEntityType

API_TOKEN = 'YOUR TOKEN'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def on_startup(_):
    print('Bot has been connected')


@dp.message_handler(Command('mute'))
async def mute(message: types.Message):
    await mute_command(bot, message)


@dp.message_handler(Command('unmute'))
async def unmute(message: types.Message):
    await unmute_command(bot, message)


@dp.message_handler()
async def echo_send(message: types.Message):
    admins_list = [admin.user.id for admin in await bot.get_chat_administrators(chat_id=message.chat.id)]
    if message.from_user.id not in admins_list:
        parent_dir = path.dirname(path.abspath(__file__))
        mention = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'

        if {morph(i) for i in message.text.split(' ')}.intersection(
                set(json.load(open(path.join(parent_dir, 'cenz.json'))))) != set():

            date = datetime.datetime.now()
            log_file = open('AutoModWords.log', 'a')

            print(date.strftime("%d-%m-%Y %H:%M"), 'Гравець: ' + message.from_user.first_name, message.from_user.id,
                  'Повідомлення з порушенням: : ' + message.text, file=log_file)
            log_file.close()

            await message.reply(
                f'Повідомлення {mention} містило непристойне слово, тому воно було видалене. Користувач замучений на 5 хв.',
                parse_mode="HTML")

            await bot.delete_message(message.chat.id, message.message_id)
            await bot.restrict_chat_member(message.chat.id, message.from_user.id,
                                           types.ChatPermissions(can_send_messages=False),
                                           until_date=datetime.datetime.now() + datetime.timedelta(seconds=300))
            print('Мут успішно видано')


class UrlMiddleWare(BaseMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_links = self.load_allowed_links()

    def load_allowed_links(self):
        allowed_links = []
        file_path = os.path.join(os.path.dirname(__file__), 'allowed_links.txt')
        with open(file_path, 'r') as file:
            allowed_links = [line.strip() for line in file.readlines()]
        return allowed_links

    async def on_pre_process_message(self, message: types.Message, data: dict):
        admins_list = [admin.user.id for admin in await bot.get_chat_administrators(chat_id=message.chat.id)]
        if message.from_user.id not in admins_list:
            if msg_entities := (message.entities or message.caption_entities):
                for entity in msg_entities:
                    if entity.type in [MessageEntityType.URL, MessageEntityType.TEXT_LINK]:
                        url = message.text[entity.offset:entity.offset + entity.length]
                        mention = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'

                        if not any(url.startswith(allowed_link) for allowed_link in self.allowed_links):
                            await message.reply(f'Посилання відправлене користувачем {mention} видалено', parse_mode='HTML')
                            await message.delete()
                            print("Посилання видалено")
                            raise CancelHandler()
                        else:
                            print("Дозволене посилання")


dp.setup_middleware(UrlMiddleWare())
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
