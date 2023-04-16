import logging
import datetime
import itertools

import aiogram
from aiogram import Bot, Dispatcher, executor, types
import json
import string
from os import path
import pymorphy2
import os

from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import MessageEntityType

from dotenv import load_dotenv

load_dotenv()

# логирование, конфиг
logging.basicConfig(level=logging.INFO)
bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot)


async def on_startup(_):
    print('Bot has been connected')


def normal_mat(word: str):
    # делаем все нижним регистром (строчным), убираем все знаки ^$#^&**^$@#&*|/. и тд
    word = word.lower().translate(str.maketrans('', '', string.punctuation))
    # убираем все повторяющиеся буквы
    word = ''.join(i for i, _ in itertools.groupby(word))
    # склоняем по падежам/числам, все вариации мата крч
    morph = pymorphy2.MorphAnalyzer()
    parsed_token = morph.parse(word)
    # выводится нормальная форма. normal_form см. выше
    normal_form = parsed_token[0].normal_form
    # возвращаем результат всех процедур
    # print(normal_form)
    return normal_form


@dp.message_handler()
async def echo_send(message: types.Message):
    if message.chat.type == "private":
        return True

    # для поиска места директории указанного файла со словарем банвордов cenz.json
    parent_dir = path.dirname(path.abspath(__file__))
    # делаем проверку + всё в 1 строчку, разделяя пробелом
    if {normal_mat(i) for i in message.text.split(' ')}.intersection(
            set(json.load(open(path.join(parent_dir, 'cenz.json'))))) != set():
        await message.reply(
            'Твоє повідомлення містило непристойне слово, тому воно було видалене. Гравець замучений на 5хв')
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.restrict_chat_member(message.chat.id, message.from_user.id,
                                       types.ChatPermissions(can_send_messages=False),
                                       until_date=datetime.datetime.now() + datetime.timedelta(seconds=30))
        # print('Мут был выдан успешно')


class UrlMiddleWare(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        if message.chat.type == "private":
            return True

        # проверка на админа чата
        try:
            admins_list = [admin.user.id for admin in await bot.get_chat_administrators(chat_id=message.chat.id)]
        except aiogram.utils.exceptions.BotBlocked:
            return print("Бот был заблокирован в чате.")
        except aiogram.utils.exceptions.ChatNotFound:
            return print("Чат не найден.")
        except aiogram.utils.exceptions.ChatAdminRequired:
            return print("Бот не является администратором чата.")
        except aiogram.utils.exceptions.TelegramAPIError:
            return print("Произошла ошибка при получении списка администраторов чата.")

        if message.from_user.id not in admins_list:
            if msg_entities := (message.entities or message.caption_entities):
                for entitie in msg_entities:
                    if entitie.type in [MessageEntityType.URL, MessageEntityType.TEXT_LINK]:
                        # удаляем ссылки непохожие на эти
                        if message.text != 'https://forum.samp-ukraine.com/index.php':
                            await message.reply('Посилання видалено')
                            await message.delete()
                            # print("Посилання видалено")
                            raise CancelHandler()
                        elif message.text != 'https://www.samp-ukraine.com/':
                            await message.reply('Посилання видалено')
                            await message.delete()
                            # print("Посилання видалено")
                        elif message.text != 'https://discord.gg/Nng8YQqmmx':
                            await message.reply('Посилання видалено')
                            await message.delete()
                            # print("Посилання видалено")
                        elif message.text != 'https://t.me/samp_ukraine_bot':
                            await message.reply('Посилання видалено')
                            await message.delete()
                            # print("Посилання видалено")

                        raise CancelHandler()
                    else:
                        print('Не є заблокованим посиланням')


dp.setup_middleware(UrlMiddleWare())
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
