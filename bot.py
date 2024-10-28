import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from db.db import DriverDB
from db.models import ImageHistoryEntity
from img_parser import ImgParser


class AppConfig(BaseSettings):
    """
    Загружаем токен и путь к базе.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="forbid",
    )
    BOT_TOKEN: str = Field(min_length=35)
    DATABASE_URL: str = Field(min_length=5)


app_config = AppConfig()
BOT_TOKEN = app_config.BOT_TOKEN
DATABASE_URL = app_config.DATABASE_URL

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()

DriverDB.create_db(DATABASE_URL)
db = DriverDB.get_repository()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
parser = ImgParser()


@dp.message(Command(commands='start'))
async def process_start_command(message: Message):
    """
    Приветственное сообщение, ответ на команду: /start
    """
    await message.answer('''Привет!\nCVC-бот!\nЯ могу читать текст на картинках. Давай попробуем!''')


@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    """
    Информация о поддерживаемых командах: /help
    """
    await message.answer('''/start - Приветственное сообщение\n/lang - Перечень часто используемых языков\
\n/setlang - смена языка распознавания\n/history - показать историю распознания изображений\
\n/history_clear - очистить историю\nПришли мне изображение, а я попробую прочитать текст.''')


@dp.message(Command(commands='lang'))
async def process_help_command(message: Message):
    """
    Список поддерживаемых языков: /lang
    """
    await message.answer('''Russian - ‘ru’\nEnglish - ‘en’\nGerman - ‘german’\nItalian - ‘it’\
\nFrench - ‘fr’\nПоддерживаются только эти языки.''')


@dp.message(Command(commands='setlang'))
async def set_language(message: types.Message):
    """
    Смена языка: /setlang <язык>
    """
    lang = message.text.strip().split()[-1].lower()
    await message.reply(parser.set_lang(lang))


@dp.message(Command(commands='history'))
async def show_history(message: types.Message):
    """
    Показывает историю парсинга сообщений: /history
    """
    user_id = message.from_user.id
    for msg in db.get_history(user_id):
        await message.answer(msg)


@dp.message(Command(commands='history_clear'))
async def show_history(message: types.Message):
    """
    Очистить историю: /history_clear
    """
    user_id = message.from_user.id
    text = db.clear_history(user_id=user_id)
    await message.answer(text=text)


@dp.message(F.photo)
async def handle_photo(message: types.Message):
    """
    Распознание текста на изображении: при получении изображения
    """
    try:
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        user_id = message.from_user.id
        text = parser.parser(downloaded_file.read())
        if text:
            entity = ImageHistoryEntity(file_id=file_id, text=text, user_id=user_id, datess=datetime.now())
            db.add(entity)
        await message.reply(text or "Текст не распознан.")
    except Exception as e:
        logging.error(f"Ошибка при обработке изображения: {e}")
        await message.reply("Произошла ошибка при обработке изображения.")


@dp.message()
async def send_echo(message: Message):
    """
    Заглушка на все неподдерживаемые команды и типы сообщений
    """
    await message.answer(text='Воспользуйтесь справкой /help')


if __name__ == '__main__':
    dp.run_polling(bot)
