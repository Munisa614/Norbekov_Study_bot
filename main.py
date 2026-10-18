import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiohttp import web

# Configuration
BOT_TOKEN = "8846840460:AAEBhXz3qKq9R2piKj4qYX6vHRnTq9i88ms"  # BotFather bergan tokeningizni yozing
ADMIN_IDS = [1309449553, 7372128318]  # O'zingizning Telegram ID'ingizni yozing

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Bosqichlar (FSM)
class Registration(StatesGroup):
    full_name = State()
    phone_number = State()
    grade = State()
    course = State()


# Kurslar ro'yxati
COURSES = [
    "Matematika,ingliz tili, rus tili(chuqurlashtirib o'qitish)",
    "Prezident maktabiga tayyorlash kurslari",
    "4-11-sinflar uchun qo'shimcha darslar",
    "Abituriyentlarni tayyorlash",
     "Matematika va ingliz tilidan sertifikatga tayyorlash"
]


# /start buyrug'i
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    welcome_text = (
        "<b>Assalomu alaykum! 'Norbekov o'quv markazi' rasmiy botiga xush"
        " kelibsiz!</b>\n\nSifatli ta'lim va yorqin kelajak sari ilk qadamni"
        " tashlang.\n\nRo'yxatdan o'tish uchun iltimos, <b>Ism va"
        " Familiyangizni</b> kiriting:"
    )
    await message.answer(welcome_text, parse_mode="HTML")
    await state.set_state(Registration.full_name)


# 1. Ism-familiya
@dp.message(Registration.full_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await message.answer(
        "Rahmat! Endi Telefon raqamingizni yuboring yoki quyidagi"
        " tugmani bosing:",
        reply_markup=kb,
        parse_mode="Markdown",
    )
    await state.set_state(Registration.phone_number)


# 2. Telefon raqami
@dp.message(Registration.phone_number)
async def process_phone(message: types.Message, state: FSMContext):
    phone = (
        message.contact.phone_number if message.contact else message.text
    )
    await state.update_data(phone_number=phone)

    await message.answer(
        "Sinfingizni kiriting (Masalan: 7-sinf, 11-sinf yoki Talaba):",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Registration.grade)


# 3. Sinf
@dp.message(Registration.grade)
async def process_grade(message: types.Message, state: FSMContext):
    await state.update_data(grade=message.text)

    buttons = [[KeyboardButton(text=course)] for course in COURSES]
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    await message.answer(
        "Bizning kurslarimizdan birini tanlang:", reply_markup=kb
    )
    await state.set_state(Registration.course)


# 4. Kursni tanlash va Adminga yuborish
@dp.message(Registration.course)
async def process_course(message: types.Message, state: FSMContext):
    await state.update_data(course=message.text)
    data = await state.get_data()

    await message.answer(
        "Sizning arizangiz qabul qilindi! Tez orada administratorimiz siz bilan"
        " bog'lanadi.\n\nE'tiboringiz uchun rahmat!",
        reply_markup=ReplyKeyboardRemove(),
    )

    admin_text = (
        "<b>📥 YANGI ARIZA!</b>\n\n"
        f"👤 <b>Ism-Familiya:</b> {data['full_name']}\n"
        f"📞 <b>Tel:</b> {data['phone_number']}\n"
        f"🏫 <b>Sinf:</b> {data['grade']}\n"
        f"📚 <b>Tanlangan kurs:</b> {data['course']}\n"
        f"🔗 <b>Telegram Profile:</b> @{message.from_user.username if message.from_user.username else 'Mavjud emas'}"
    )

    admin_text = (
        "<b>📥 YANGI ARIZA!</b>\n\n"
        f"👤 <b>Ism-Familiya:</b> {data['full_name']}\n"
        f"📞 <b>Tel:</b> {data['phone_number']}\n"
        f"🏫 <b>Sinf:</b> {data['grade']}\n"
        f"📚 <b>Tanlangan kurs:</b> {data['course']}\n"
        f"🔗 <b>Telegram Profile:</b> @{message.from_user.username if message.from_user.username else 'Mavjud emas'}"
    )

    for admin_id in ADMIN_IDS:
      await bot.send_message(
          chat_id=admin_id, text=admin_text, parse_mode="HTML"
      )
    await state.clear()
 # --- Render uchun kichik veb-server (Bot uxlab qolmasligi uchun) ---
async def handle(request):
    return web.Response(text="Bot is running!")


async def web_server():
  app = web.Application()
  app.router.add_get("/", handle)
  runner = web.AppRunner(app)
  await runner.setup()
  port = int(os.environ.get("PORT", 8080))
  site = web.TCPSite(runner, "0.0.0.0", port)  # Mana shu joyi o'zgardi!
  await site.start()


async def main():
    # Veb server va botni bir vaqtda ishga tushiramiz
    await web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())