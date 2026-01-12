import json
from pathlib import Path
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DATA_FILE = Path("singola.json")

def save_singola(photo_file_id, caption):
    DATA_FILE.write_text(json.dumps({
        "photo": photo_file_id,
        "caption": caption
    }, ensure_ascii=False))

def load_singola():
    if not DATA_FILE.exists():
        return None
    return json.loads(DATA_FILE.read_text())

kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Singola di oggi", callback_data="singola")]
])

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(msg: types.Message):
        await msg.answer("🎯 Mister Pronostico\nScegli dal menu 👇", reply_markup=kb)

    @dp.callback_query(lambda c: c.data == "singola")
    async def send_singola(call: types.CallbackQuery):
        data = load_singola()
        if not data:
            await call.message.answer("Nessuna singola disponibile.")
        else:
            await call.message.answer_photo(
                photo=data["photo"],
                caption=data["caption"],
                parse_mode="HTML"
            )
        await call.answer()

    @dp.message(Command("setsingola"))
    async def set_singola(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return
        if not msg.reply_to_message or not msg.reply_to_message.photo:
            await msg.answer("Rispondi a una FOTO con /setsingola")
            return
        photo = msg.reply_to_message.photo[-1]
        caption = msg.reply_to_message.caption or ""
        save_singola(photo.file_id, caption)
        await msg.answer("✅ Singola salvata")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
