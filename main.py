import sqlite3
import time

from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types.message import ContentType

bot = Bot(token="YOUR_TOKEN")
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
    time.sleep(2)
    await message.answer("Готов работать, можете скинуть благодарности с #благодарю")

# Обработчик благодарностей
@dp.message_handler(content_types=[ContentType.TEXT])
async def handle_message(message: types.Message):
    if message.text.startswith('#благодарю'):
        # Извлекаем всех пользователей, которых упомянули в сообщении
        users = message.parse_entities(types.MessageEntityType.MENTION)
        if not users:
            await message.answer("К сожалению, я не могу найти пользователей.")
            return

        # Обновляем очки пользователей
        for user in users:
            username = user['user']['username']
            # Добавляем пользователя в базу данных, если его там еще нет
            cursor.execute('INSERT OR IGNORE INTO users (nickname, score) VALUES (?, 0)', (username,))
            # Увеличиваем баллы пользователя на 1
            cursor.execute('UPDATE users SET score = score + 1 WHERE nickname = ?', (username,))
            conn.commit()


        await message.answer("Бот записал всех пользователей")

# Обработчик команды show
@dp.message_handler(commands=['show'])
async def show_command(message: types.Message):
    # Извлекаем всех пользователей из базы данных
    cursor.execute('SELECT nickname, score FROM users ORDER BY score DESC')
    users = cursor.fetchall()
    if not users:
        await message.answer("К сожалению тир лист пуст(((")
        return

    # Формируем сообщение со списком пользователей и их баллами
    response = "<b>Топ пользователей:</b>\n\n"
    for user in users:
        response += f"{user[0]}: {user[1]}\n"

    await message.answer(response, parse_mode=ParseMode.HTML)

# Обработчик ошибок
@dp.errors_handler(exception=Exception)
async def errors_handler(update, exception):
    print(f"Ошибка обработки обновления {update}: {exception}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

