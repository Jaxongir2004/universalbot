import logging
import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from quart import Quart, request
import asyncio

# === Muhit o'zgaruvchilarni yuklash ===
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH  # https://yourapp.onrender.com/webhook/TOKEN
MOVIE_CHANNEL = os.getenv("MOVIE_CHANNEL")
SUBSCRIPTION_CHANNELS = [os.getenv("SUB_CHANNEL1")]

# === Bot, Dispatcher, Router ===
bot = Bot(token=TOKEN)
router = Router()
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

# === Kino ID lug‘ati ===
kino_id_lugat = {
    "1234": 2,
    "241": 7,
    "242": 8,
    "244": list(range(9, 76))  # qisqartirilgan
}

# === Obuna tekshirish ===
async def check_subscription(user_id: int) -> bool:
    for channel in SUBSCRIPTION_CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            logging.error(f"Obuna tekshirishda xato: {e}")
            return False
    return True

# === /start komandasi ===
@router.message(Command("start"))
async def start_command(message: Message):
    if await check_subscription(message.from_user.id):
        await message.answer("✅ Obuna bor! Kod kiriting:")
    else:
        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url="https://t.me/FilmBoxApp")],
            [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check")]
        ])
        await message.answer("❌ Avval kanalga obuna bo‘ling:", reply_markup=buttons)

# === Tekshirish tugmasi ===
@router.callback_query(lambda c: c.data == "check")
async def check_subscription_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_subscription(user_id):
        await callback_query.message.edit_text("✅ Obuna bor! Kod kiriting:")
    else:
        await callback_query.answer("❌ Obuna hali yo‘q!", show_alert=True)

# === Kino kodi qabul qilish ===
@router.message()
async def handle_movie_request(message: Message):
    if await check_subscription(message.from_user.id):
        kino_id = message.text.strip()
        xabar_id = kino_id_lugat.get(kino_id)
        if xabar_id:
            if isinstance(xabar_id, list):
                for msg_id in xabar_id:
                    await bot.copy_message(chat_id=message.chat.id, from_chat_id=MOVIE_CHANNEL, message_id=msg_id)
            else:
                await bot.copy_message(chat_id=message.chat.id, from_chat_id=MOVIE_CHANNEL, message_id=xabar_id)
        else:
            await message.reply("❌ Bunday kino topilmadi!")
    else:
        await message.answer("❌ Iltimos, obuna bo‘ling!")

# === Quart server ===
app = Quart(__name__)

@app.route("/", methods=["GET"])
async def home():
    return "Bot ishlayapti!", 200

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    try:
        request_data = await request.get_data()
        update = types.Update.model_validate_json(request_data.decode("utf-8"))
        await dp.feed_update(bot, update)
        return "", 200
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return "", 500

# === Webhook o‘rnatish ===
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logging.info("✅ Webhook o‘rnatildi!")

# === UWSGI ishga tushirish uchun ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(on_startup())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
