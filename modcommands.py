import asyncio
from aiogram import types
from aiogram.dispatcher.filters import Command


async def mute_command(bot, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        mention = f'<a href="tg://user?id={user_id}">{message.reply_to_message.from_user.first_name}</a>'
        time = int(message.text[6:8])
        num = ""
        time_2 = ""
        if message.text.endswith("хв") or message.text.endswith("m"):
            time = 60 * time
            num = "хв"
            time_2 = time // 60
        elif message.text.endswith("год") or message.text.endswith("h"):
            time = 60 * 60 * time
            num = "год"
            time_2 = time // 3600
        elif message.text.endswith("д") or message.text.endswith("d"):
            time = 60 * 60 * 24 * time
            num = "дн"
            time_2 = time // 86400
        else:
            pass

        await bot.restrict_chat_member(message.chat.id, user_id, types.ChatPermissions(can_send_messages=False))
        await message.reply(f"Користувач {mention} замучений на {time_2} {num}", parse_mode="HTML")

        await asyncio.sleep(time)

        chat_member = await bot.get_chat_member(message.chat.id, user_id)

        if chat_member.can_send_messages:
            return

        if not chat_member.can_send_messages:
            await bot.restrict_chat_member(message.chat.id, user_id, types.ChatPermissions(can_send_messages=True))
            await message.reply(f"Користувач {mention} розмучений", parse_mode="HTML")
            return
    else:
        await message.reply("Команда повинна бути відповіддю на повідомлення!")


async def unmute_command(bot, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        mention = f'<a href="tg://user?id={user_id}">{message.reply_to_message.from_user.first_name}</a>'

        chat_member = await bot.get_chat_member(message.chat.id, user_id)
        if chat_member.can_send_messages:
            await message.reply(f"Користувач {mention} не замучений", parse_mode="HTML")
            return

        await bot.restrict_chat_member(message.chat.id, user_id, types.ChatPermissions(can_send_messages=True))
        await message.reply(f"Користувач {mention} розмучений", parse_mode="HTML")
    else:
        await message.reply("Команда повинна бути відповіддю на повідомлення!")
