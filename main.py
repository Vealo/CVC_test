import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from paddleocr import PaddleOCR
from sqlalchemy import create_engine, Column, Integer, String, Sequence, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# TOKEN полученный у @BotFather
BOT_TOKEN = "7080042676:AAH00axQnqkUtc3fpm6NY0FovoyoLPN8-lM"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
storage = MemoryStorage()

# Инициализация PaddleOCR
current_lang = 'ru'
ocr = PaddleOCR(use_angle_cls=True, lang=current_lang)  # Измените 'en' на нужный язык

# Настройка базы данных SQLite с SQLAlchemy
DATABASE_URL = 'history.db'
Base = declarative_base()
engine = create_engine(f'sqlite:///{DATABASE_URL}', echo=True)  # Создание базы данных history.db
Session = sessionmaker(bind=engine)
session = Session()

class ImageHistory(Base):
    __tablename__ = 'image_history'
    id = Column(Integer, Sequence('image_id_seq'), primary_key=True)
    user_id = Column(String)
    datess = Column(DateTime, default=datetime.today())
    file_id = Column(String)
    text = Column(String)

# Создание таблицы в базе данных
if not os.path.exists(DATABASE_URL):
    Base.metadata.create_all(engine)
    logging.info("Создана новая база данных.")

# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands='start'))
async def process_start_command(message: Message):
    await message.answer('Привет!\nCVC-бот!\nЯ могу читать текст на картинках. Давай попробуем!')


# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(
        '/start - Приветсвеное сообещение\n'
        '/lang - Перечень часто используемых языков\n'
        '/setlang - смена языка распознования'
        'Пришли мне изображение, а я попробую прочитать текст.'
    )
# Этот хэндлер будет срабатывать на команду "/lang"
@dp.message(Command(commands='lang'))
async def process_help_command(message: Message):
    await message.answer(
    'Russian - ‘ru’\n'
    'English - ‘en’\n'
    'German - ‘german’\n'
    'Italian - ‘it’\n'
    'French - ‘fr’\n'
    'В настоящее время идет поддержка только этих языков.'
    )

# Этот хэндлер будет срабатывать на команду "/setlang"
@dp.message(Command(commands='setlang'))
async def set_language(message: types.Message):
    global current_lang, ocr
    lang = message.text.strip().split()[-1].lower()  # Получаем аргумент команды и убираем пробелы
    # Проверяем поддерживаемые языки
    supported_languages = ['en', 'ru', 'fr', 'german', 'it', 'fr']  # Добавьте другие поддерживаемые языки по мере необходимости

    if lang in supported_languages:
        current_lang = lang  # Устанавливаем текущий язык
        ocr = PaddleOCR(use_angle_cls=True, lang=current_lang)  # Инициализируем OCR с новым языком
        await message.reply(f"Язык установлен на: {lang}.")
    else:
        await message.reply("Неподдерживаемый язык. Пожалуйста, выберите из: " + ", ".join(supported_languages))

# Этот хэндлер для получения истории
@dp.message(Command(commands='history'))
async def show_history(message: types.Message):
    user_id = message.from_user.id
    history = session.query(ImageHistory).filter_by(user_id=user_id).all()

    if not history:
        await message.reply("История пуста.")
        return

    await message.reply(f"История обработанных изображений.")
    for number, row in enumerate(history, start=1):
        text = f"Дата: {row.datess}\nСообщение: {number}\nРаспознано:\n{row.text}"
        await message.answer(text=text)


# Этот хэндлер будет распозновать изображения в ваших сообщения
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    try:
        # Получение ID файла и загрузка изображения
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        user_id = message.from_user.id
        # Выполнение OCR на изображении
        result = ocr.ocr(downloaded_file.read(), cls=True)
        text = "\n".join([line[1][0] for line in result[0]])  # Извлечение текста из результатов

        # Запись в БД
        new_entry = ImageHistory(file_id=file_id, text=text, user_id=user_id)
        session.add(new_entry)
        session.commit()
        # Отправка распознанного текста пользователю
        await message.reply(text or "Текст не распознан.")

    except Exception as e:
        logging.error(f"Ошибка при обработке изображения: {e}")
        await message.reply("Произошла ошибка при обработке изображения.")


# Этот хэндлер будет срабатывать на любые ваши сообщения, кроме команд
@dp.message()
async def send_echo(message: Message):
    try:
        await message.answer(text='Воспользуйтесь справкой /help')
    except TypeError:
        await message.reply(
            text='Непредвиденная ошибка'
        )


if __name__ == '__main__':
    dp.run_polling(bot)