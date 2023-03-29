import logging
import datetime
import itertools
from aiogram import Bot, Dispatcher, executor, types
import json
import string
import pymorphy2
import os

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import MessageEntityType

logging.basicConfig(level=logging.INFO)
bot = Bot('6140941878:AAGrkh469KVD1OZWsPe9PZIMtiqckBFGLXg')
dp = Dispatcher(bot)

async def on_startup(_):
    print('Bot has been connected')

def normal_mat(word:str):
    word = word.lower().translate(str.maketrans('','',string.punctuation))
    morph = pymorphy2.MorphAnalyzer()
    parsed_token = morph.parse(word)
    #выводится нормальная форма. normal_form см. выше
    normal_form = parsed_token[0].normal_form
    #делаем проверку на повторяющиеся символы и удаляем их
    r = ''.join(i for i, _ in itertools.groupby(normal_form))
    return r

@dp.message_handler()
async def echo_send(message : types.Message):
    admins_list = [admin.user.id for admin in await bot.get_chat_administrators(chat_id=message.chat.id)]
    if message.from_user.id not in admins_list:
        if {normal_mat(i) for i in message.text.split(' ')}.intersection(set(json.load(open('E:\pythonProject\oigram bot\cenz.json')))) != set():  
            await message.reply('Погане повідомлення')
            await bot.delete_message(message.chat.id, message.message_id)
            await bot.restrict_chat_member(message.chat.id, message.from_user.id, types.ChatPermissions(can_send_messages=False), until_date = datetime.datetime.now() + datetime.timedelta(seconds=30))
            print('Мут был выдан успешно')
    else:
        print('Повідомлення написав адміністратор')

@dp.message_handler(content_types=['text'])
async def delete_messages(message: types.Message):
    for entity in message.entities:
        if entity.type in ["url", "text_link", "https"]:
            
            await message.delete()

class UrlMiddleWare(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
            if msg_entities := (message.entities or message.caption_entities):
                for entitie in msg_entities:
                    if entitie.type in [MessageEntityType.URL, MessageEntityType.TEXT_LINK]:
                        if message.text != 'https://twitter.com/home?lang=ru':
                            await message.reply('Посилання видалено')
                            await message.delete()
                            print("Посилання видалено")
                            raise CancelHandler()
                        else:
                            print('Не є заблокованим посиланням')





dp.setup_middleware(UrlMiddleWare())
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)