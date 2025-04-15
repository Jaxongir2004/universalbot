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

# === Botni ishga tushirish ===
bot = Bot(token=TOKEN)
router = Router()
dp = Dispatcher()

# Kino kodi va ularning xabar ID'lari
kino_id_lugat = {
    "1234": 2,
    "241": 7,
    "242": 8,
    "244": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75]

}

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

        if isinstance(xabar_id, list):
            for msg_id in xabar_id:
                await bot.copy_message(chat_id=message.chat.id, from_chat_id=MOVIE_CHANNEL, message_id=msg_id)
        else:
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

# === Kino kodi qabul qilish ===
@router.message()
async def handle_movie_request(message: Message):
    user_id = message.from_user.id

    if await check_subscription(user_id):
        await send_movie(message)
    else:
        await message.answer("❌ Iltimos, barcha kanallarga obuna bo‘ling!")

# === Botni ishga tushirish ===
async def main():
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    logging.info("✅ Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
