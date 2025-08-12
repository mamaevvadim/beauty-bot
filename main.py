import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)


# Генерация кнопок со временем
def generate_time_slots(start=10, end=21):
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for hour in range(start, end + 1):
        time_str = f"{hour:02d}:00"
        buttons.append(InlineKeyboardButton(text=time_str, callback_data=f"time_{time_str}"))
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Привет! Выберите удобное время для записи:",
        reply_markup=generate_time_slots()
    )


@dp.callback_query_handler(lambda c: c.data.startswith("time_"))
async def process_time_selection(callback_query: types.CallbackQuery):
    selected_time = callback_query.data.split("_")[1]
    await callback_query.answer()
    await callback_query.message.answer(f"Вы выбрали время: {selected_time}")
    # Здесь можно добавить сохранение выбора в БД или отправку администратору


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
