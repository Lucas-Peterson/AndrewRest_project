import sqlite3
import re
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext


class CancelState(StatesGroup):
    waiting_for_usernames = State()

# Создаем подключение к базе данных
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Создаем таблицу для хранения данных о пользователях
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (user_id INTEGER PRIMARY KEY, user_name TEXT, points INTEGER)''')
conn.commit()

bot = Bot(token="5938916690:AAHOOZ08Cxf3ARylBtqDk4fMJqtB0lOwPLk")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def process_start_command(message: Message):
    # Приветственное сообщение
    await bot.send_message(message.chat.id, "Привет! Отправь сообщение с никами пользователей. Если нужно удалить, то используй /cancel. Показ стата /show")


@dp.message_handler()
async def handle_message(message: Message):
    # Извлекаем текст сообщения
    message_text = message.text

    # Извлекаем все упоминания пользователей из текста сообщения
    users_mentions = re.findall(r'@(\w+)', message_text)

    # Если есть упоминания пользователей, добавляем очки каждому из них
    if users_mentions:
        for user_mention in users_mentions:
            cursor.execute("SELECT * FROM users WHERE user_name=?", (user_mention,))
            user = cursor.fetchone()
            if user is None:
                cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (None, user_mention, 1))
            else:
                cursor.execute("UPDATE users SET points=? WHERE user_name=?", (user[2]+1, user_mention))
        conn.commit()

    await message.answer("Записал все ники")


# Обработчик команды /show
@dp.message_handler(Command("show"))
async def cmd_show(message: Message):
    # Получаем данные всех пользователей и формируем сообщение
    cursor.execute("SELECT user_name, points FROM users")
    users = cursor.fetchall()
    message_text = "Текущие баллы:\n"
    for user in users:
        message_text += f"{user[0]} | {user[1]}\n"

    # Отправляем сообщение с текущими баллами
    await message.answer(message_text)


# Обработчик команды /cancel
@dp.message_handler(Command("cancel"))
async def cmd_cancel(message: Message):

    await CancelState.waiting_for_usernames.set()

    await message.answer("Введите ники для удаления")


# Обработчик сообщений в состоянии "waiting_for_usernames"
@dp.message_handler(state=CancelState.waiting_for_usernames)
async def process_usernames(message: Message, state: FSMContext):
    # Извлекаем ники из сообщения
    usernames = []
    for entity in message.entities:
        if entity.type == "mention":
            usernames.append(entity.user.username)
    if not usernames:
        await message.answer("Не найдено упоминаний пользователей. Попробуйте еще раз")
        return

    # Вычитаем баллы у пользователей и записываем изменения в БД
    for username in usernames:
        cursor.execute("SELECT * FROM users WHERE user_name=?", (username,))
        user = cursor.fetchone()
        if user is not None:
            cursor.execute("UPDATE users SET points=? WHERE user_id=?", (user[2]-1, user[0]))
    conn.commit()

    await message.answer("Баллы вычтены")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
