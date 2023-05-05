import sqlite3
import csv

from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor


bot = Bot(token="5938916690:AAHOOZ08Cxf3ARylBtqDk4fMJqtB0lOwPLk")
dp = Dispatcher(bot)

# Создаем подключение к базе данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создаем таблицу, если она еще не создана
cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, nickname TEXT, score INTEGER)')


# Обработчик команды start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Bot ready to work")


# Ищем пользователя в базе данных по id
async def get_user_by_id(user_id: int):
    cursor.execute('SELECT id, nickname, score FROM users WHERE id = ?', (user_id,))
    return cursor.fetchone()


# Добавляем пользователя в базу данных
async def add_user(user_id: int, nickname: str):
    cursor.execute('INSERT INTO users (id, nickname, score) VALUES (?, ?, 0)', (user_id, nickname))
    conn.commit()


# Увеличиваем баллы пользователя на 1
async def update_user_score(user_id: int, new_score: int):
    cursor.execute('UPDATE users SET score = ? WHERE id = ?', (new_score, user_id))
    conn.commit()


async def handle_message(message: types.Message):
    if message.text.startswith('#благодарю'):
        # Ищем упоминания пользователей в тексте сообщения
        mentions = []
        for entity in message.entities:
            if entity.type == 'mention':
                if entity.user and entity.user.id is not None:
                    mentions.append(entity.user.id)
                else:
                    mention_text = message.text[entity.offset:entity.offset + entity.length]
                    mentions.append(mention_text.strip('@'))
        if not mentions:
            await message.answer("К сожалению, я не могу найти пользователей.")
            return
        for user_id in mentions:
            # Ищем пользователя в базе данных
            user_data = await get_user_by_id(user_id)
            if user_data:
                # Если пользователь найден, увеличиваем его баллы на 1
                user_id, nickname, score = user_data
                await update_user_score(user_id, score + 1)
            else:
                # Если пользователь не найден, добавляем его в базу данных
                if isinstance(user_id, str):
                    nickname = user_id
                else:
                    nickname = (await bot.get_chat_member(message.chat.id, user_id)).user.username
                await add_user(user_id, nickname)
        await message.answer("Бот записал всех пользователей")


# Обработчик команды show
@dp.message_handler(commands=['show'])
async def show_command(message: types.Message):
    # Извлекаем всех пользователей из базы данных
    cursor.execute('SELECT nickname, score FROM users ORDER BY score DESC')
    users = cursor.fetchall()
    if not users:
        await message.answer("К сожалению, тир лист пуст(((")
        return

    # Формируем сообщение со списком пользователей и их баллами
    response = "<b>Топ пользователей:</b>\n\n"
    for user in users:
        response += f"{user[0]}: {user[1]}\n"

    await message.answer(response, parse_mode=ParseMode.HTML)

    # Записываем базу данных в файл CSV
    with open('users.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Nickname', 'Score'])
        for user in users:
            writer.writerow([user[0], user[1]])

    # Отправляем файл пользователю
    with open('users.csv', 'rb') as file:
        await message.answer_document(file)


# Обработчик команды cancel
@dp.message_handler(commands=['cancel'])
async def cancel_command(message: types.Message):
    # Получаем сообщение, на которое данное сообщение является ответом
    reply_to_message = message.reply_to_message
    if not reply_to_message:
        await message.answer("К сожалению, я не могу найти сообщение, на которое вы хотите ответить.")
        return

    # Получаем id пользователя, на которого было данное сообщение ответом
    user_id = reply_to_message.from_user.id

    # Уменьшаем баллы пользователя на 1
    cursor.execute('UPDATE users SET score = score - 1 WHERE id = ?', (user_id,))
    conn.commit()

    await message.answer("Бот уменьшил баллы данному пользователю.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
