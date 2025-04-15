import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

# === Muhit o'zgaruvchilarni yuklash ===
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
MOVIE_CHANNEL = os.getenv("MOVIE_CHANNEL")
SUBSCRIPTION_CHANNELS = [
    os.getenv("SUB_CHANNEL1")
]
# Yopiq kanallar uchun
CLOSED_CHANNELS = [
    os.getenv("CLOSED_CHANNEL1"),
    os.getenv("CLOSED_CHANNEL2")
]

# === Botni ishga tushirish ===
bot = Bot(token=TOKEN)
router = Router()
dp = Dispatcher()

# Kino kodi va ularning xabar ID'lari
kino_id_lugat = {
    "1234": 2,
    "5678": 6
}

# Yopiq kanalda so‘rov yuborgan foydalanuvchilar ID'sini saqlash
user_requests = []  # Bu erda foydalanuvchilarning so‘rovlarini saqlaymiz

# === Obunani tekshirish funksiyasi ===
async def check_subscription(user_id: int) -> bool:
    for channel in SUBSCRIPTION_CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# === Kino yuborish funksiyasi ===
async def send_movie(message: Message):
    kino_id = message.text.strip()
    if kino_id in kino_id_lugat:
        xabar_id = kino_id_lugat[kino_id]
        await bot.copy_message(chat_id=message.chat.id, from_chat_id=MOVIE_CHANNEL, message_id=xabar_id)
    else:
        await message.reply("❌ Bunday kino topilmadi. Iltimos, boshqa kod kiriting!")

# === /start komandasi ===
@router.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id

    if await check_subscription(user_id):
        await message.answer("✅ Siz barcha kanallarga obuna bo‘lgansiz! Endi kino kodini kiriting 😊:")
    else:
        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url="https://t.me/FilmBoxApp")],
            [InlineKeyboardButton(text="📢 Yopiq Kanal 1 (So‘rov yuborish)", callback_data="join_channel1")],
            [InlineKeyboardButton(text="📢 Yopiq Kanal 2 (So‘rov yuborish)", callback_data="join_channel2")],
            [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check")]
        ])
        await message.answer(
            "❌ Iltimos, kanalga obuna bo‘ling va '✅ Tekshirish' tugmasini bosing.",
            reply_markup=buttons
        )

# === "Tekshirish" tugmasi bosilganda ===
@router.callback_query(lambda c: c.data == "check")
async def check_subscription_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if await check_subscription(user_id):
        await callback_query.message.edit_text("✅ Tabriklayman! Endi kino kodini kiriting 😊:")
    else:
        await callback_query.answer("❌ Siz hali kanallarga obuna bo‘lmadingiz!", show_alert=True)

# === Yopiq kanallar uchun so‘rovlar ===
@router.callback_query(lambda c: c.data == "join_channel1")
async def join_channel1(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    # Yopiq kanalga qo‘shilish so‘rovini yuborish
    user_requests.append(user_id)  # Foydalanuvchini so‘rovlar ro‘yxatiga qo‘shamiz
    await callback_query.answer("So‘rovingiz qabul qilindi! Yopiq kanalga qo‘shilish so‘rovi yuborildi.")

@router.callback_query(lambda c: c.data == "join_channel2")
async def join_channel2(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    # Yopiq kanalga qo‘shilish so‘rovini yuborish
    user_requests.append(user_id)  # Foydalanuvchini so‘rovlar ro‘yxatiga qo‘shamiz
    await callback_query.answer("So‘rovingiz qabul qilindi! Yopiq kanalga qo‘shilish so‘rovi yuborildi.")

# === Kino kodi qabul qilish ===
@router.message()
async def handle_movie_request(message: Message):
    user_id = message.from_user.id

    # Foydalanuvchi barcha kanallarga obuna bo‘lishi va so‘rov yuborishi kerak
    if await check_subscription(user_id) and user_id in user_requests:
        await send_movie(message)
    else:
        await message.answer("❌ Iltimos, barcha kanallarga obuna bo‘ling va yopiq kanal uchun so‘rov yuboring!")

# === Botni ishga tushirish ===
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    logging.info("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
