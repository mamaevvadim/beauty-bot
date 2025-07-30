import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = "7969547988:AAH6HDCiyVWC1Bf4b9-KbpF9t4YN3Pq-uZg"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Booking(StatesGroup):
    service = State()
    master = State()
    time = State()
    name = State()
    phone = State()

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📅 Записаться", callback_data="book"),
        InlineKeyboardButton("💇 Услуги", callback_data="services"),
        InlineKeyboardButton("❓ Вопросы", callback_data="faq"),
        InlineKeyboardButton("📞 Контакты", callback_data="contacts")
    )
    await message.answer_photo(photo="https://i.imgur.com/DeNIkQm.jpeg", caption=(
        "🌸 Добро пожаловать в салон красоты BEAUTY BOSS! 🌸\n"
        "Я помогу вам записаться, узнать цены и получить ответы на вопросы.\n\n"
        "Выберите, что вас интересует 👇"
    ), reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data == "book")
async def start_booking(callback_query: types.CallbackQuery):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("💅 Маникюр", callback_data="service_Маникюр"),
        InlineKeyboardButton("💇 Стрижка", callback_data="service_Стрижка"),
        InlineKeyboardButton("🎨 Окрашивание", callback_data="service_Окрашивание"),
        InlineKeyboardButton("👁 Брови", callback_data="service_Брови")
    )
    await bot.send_message(callback_query.from_user.id, "Выберите услугу:", reply_markup=kb)
    await Booking.service.set()

@dp.callback_query_handler(lambda c: c.data.startswith("service_"), state=Booking.service)
async def choose_master(callback_query: types.CallbackQuery, state: FSMContext):
    service = callback_query.data.split("_")[1]
    await state.update_data(service=service)

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("👱‍♀️ Екатерина", callback_data="master_Екатерина"),
        InlineKeyboardButton("👩‍🦰 Мария", callback_data="master_Мария"),
        InlineKeyboardButton("👤 Не важно", callback_data="master_Не важно")
    )
    await bot.send_message(callback_query.from_user.id, "Выберите мастера:", reply_markup=kb)
    await Booking.next()

@dp.callback_query_handler(lambda c: c.data.startswith("master_"), state=Booking.master)
async def choose_time(callback_query: types.CallbackQuery, state: FSMContext):
    master = callback_query.data.split("_")[1]
    await state.update_data(master=master)

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📆 Сегодня", callback_data="time_Сегодня"),
        InlineKeyboardButton("📆 Завтра", callback_data="time_Завтра"),
        InlineKeyboardButton("📝 Указать вручную", callback_data="time_Указать")
    )
    await bot.send_message(callback_query.from_user.id, "Когда вам удобно записаться?", reply_markup=kb)
    await Booking.next()

@dp.callback_query_handler(lambda c: c.data.startswith("time_"), state=Booking.time)
async def ask_name(callback_query: types.CallbackQuery, state: FSMContext):
    time = callback_query.data.split("_")[1]
    if time == "Указать":
        await bot.send_message(callback_query.from_user.id, "Напишите удобное время:")
    else:
        await state.update_data(time=time)
        await bot.send_message(callback_query.from_user.id, "Ваше имя?")
        await Booking.name.set()
        return
    await state.update_data(time="вручную")
    await Booking.time.set()

@dp.message_handler(state=Booking.time)
async def manual_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    await message.answer("Ваше имя?")
    await Booking.name.set()

@dp.message_handler(state=Booking.name)
async def ask_phone(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📱 Отправить номер", request_contact=True))
    await message.answer("Отправьте ваш номер телефона кнопкой ниже:", reply_markup=kb)
    await Booking.phone.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=Booking.phone)
async def confirm(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    await message.answer(
        f"Спасибо! Вы записались:\n"
        f"Услуга: {data['service']}\n"
        f"Мастер: {data['master']}\n"
        f"Время: {data['time']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        "Скоро мы с вами свяжемся 💖", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "services")
async def show_services(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
        "💅 Маникюр — от 1200 ₽\n"
        "💇 Стрижка — от 1500 ₽\n"
        "🎨 Окрашивание — от 2500 ₽\n"
        "👁 Брови — от 1000 ₽")

@dp.callback_query_handler(lambda c: c.data == "faq")
async def show_faq(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
        "🕒 Работаем с 10:00 до 21:00 ежедневно.\n"
        "📍 Есть парковка\n"
        "💳 Принимаем наличные и карты\n"
        "⛔ Отменить запись можно за 2 часа")

@dp.callback_query_handler(lambda c: c.data == "contacts")
async def show_contacts(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id,
        "📍 Адрес: Москва, ул. Красоты, 15\n"
        "📞 Телефон: +7 (900) 123-45-67\n"
        "📱 WhatsApp: @salonadmin")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)