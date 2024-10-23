import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from paddleocr import PaddleOCR

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
API_TOKEN = '7080042676:AAEdnnmLcG_xoaiQuCPYq8EiI56TZTf8iU4'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Инициализация PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')  # Измените 'en' на нужный язык

@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    try:
        # Получение ID файла и загрузка изображения
        file_id = message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)

        # Выполнение OCR на изображении
        result = ocr.ocr(downloaded_file.read(), cls=True)
        text = "\n".join([line[1][0] for line in result[0]])  # Извлечение текста из результатов

        # Отправка распознанного текста пользователю
        await message.reply(text or "Текст не распознан.")

    except Exception as e:
        logging.error(f"Ошибка при обработке изображения: {e}")
        await message.reply("Произошла ошибка при обработке изображения.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)