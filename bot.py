import os
import logging

import dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from imgParser import ImgParser
from db import DriverDB

dotenv.load_dotenv('.env')
BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()

db = DriverDB(DATABASE_URL)
db.create_db()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
parser = ImgParser()

@dp.message(Command(commands='start'))
async def process_start_command(message: Message):
    '''
    Приветственное сообщение, ответ на команду: /start
    '''
    await message.answer(
'''Привет!
CVC-бот!
Я могу читать текст на картинках. Давай попробуем!''')

@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    '''
    Информация о поддерживаемых командах: /help
    '''
    await message.answer(
'''/start - Приветственное сообщение
/lang - Перечень часто используемых языков
/setlang - смена языка распознавания
/history - показать историю распознания изображений
/history_clear - очистить историю
Пришли мне изображение, а я попробую прочитать текст.''')

@dp.message(Command(commands='lang'))
async def process_help_command(message: Message):
    '''
    Список поддерживаемых языков: /lang
    '''
    await message.answer(
'''Russian - ‘ru’
English - ‘en’
German - ‘german’
Italian - ‘it’
French - ‘fr’
Поддерживаются только эти языки.''')

@dp.message(Command(commands='setlang'))
async def set_language(message: types.Message):
    '''
    Смена языка: /setlang <язык>
    '''
    lang = message.text.strip().split()[-1].lower()
    await message.reply(parser.set_lang(lang))


@dp.message(Command(commands='history'))
async def show_history(message: types.Message):
    '''
    Показывает историю парсинга сообщений: /history
    '''
    user_id = message.from_user.id
    for msg in db.history(user_id):
        await message.answer(msg)

@dp.message(Command(commands='history_clear'))
async def show_history(message: types.Message):
    '''
    Очистить историю: /history_clear
    '''
    user_id = message.from_user.id
    text = db.clear(user_id=user_id)
    await message.answer(text=text)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    '''
    Распознание текста на изображении: при получении изображения
    '''
    try:
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        user_id = message.from_user.id

        text = parser.parser(downloaded_file.read()) or "Текст не распознан."
        db.add(file_id=file_id, text=text, user_id=user_id)

        await message.reply(text)

    except Exception as e:
        logging.error(f"Ошибка при обработке изображения: {e}")
        await message.reply("Произошла ошибка при обработке изображения.")

@dp.message()
async def send_echo(message: Message):
    '''
    Заглушка на все неподдерживаемые команды и типы сообщений
    '''
    await message.answer(text='Воспользуйтесь справкой /help')


if __name__ == '__main__':
    dp.run_polling(bot)