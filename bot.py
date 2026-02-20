import json
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# ================== SOZLAMALAR ==================
# Tavsiya: tokenni env orqali qo'yish:
# PowerShell:  setx BOT_TOKEN "YOUR_TOKEN"
# So'ng terminalni qayta oching.
API_TOKEN = os.getenv("BOT_TOKEN", "8587967429:AAHB2SpROVyRY-AxDEwngHjXpGL2E_gdQMc")

ADMIN_ID = 6737790504

REQUIRED_CHANNELS = [
    "@kinolarkanal11",
    "@kinolarkanal12",
    "@kinolarkanal13",
    "@kinolarkanal14",
    "@asliddin_norkulov"
]

DB_FILE = "movies_by_code.json"

# ================== BOT ==================
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

# ================== JSON DB ==================
def load_db():
    if not os.path.exists(DB_FILE):
        data = {"movies": {}}  # {"1001": {"desc":"...", "file_id":"...", "added_at":"..."}}
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        data = {"movies": {}}
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

db = load_db()

# ================== MAJBURIY OBUNA ==================
async def check_subscriptions(user_id: int) -> bool:
    for ch in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception:
            # Bot kanalga admin bo'lmasa yoki kanal username noto'g'ri bo'lsa shu yerga tushadi
            return False
    return True

def subscribe_kb():
    kb = types.InlineKeyboardMarkup(row_width=1)
    for ch in REQUIRED_CHANNELS:
        kb.add(types.InlineKeyboardButton(f"➕ Obuna bo‘lish: {ch}", url=f"https://t.me/{ch.lstrip('@')}"))
    kb.add(types.InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub"))
    return kb

# ================== MENYULAR ==================
def admin_kb():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("➕ Kino qo‘shish", callback_data="add_movie"),
        types.InlineKeyboardButton("📋 Kino ro‘yxati", callback_data="list_movies"),
    )
    kb.add(
        types.InlineKeyboardButton("🗑 Kino o‘chirish", callback_data="delete_movie"),
        types.InlineKeyboardButton("ℹ️ Qo‘llanma", callback_data="help"),
    )
    return kb

def user_kb():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("ℹ️ Qo‘llanma", callback_data="help"))
    return kb

# ================== FSM HOLATLAR ==================
class AddMovie(StatesGroup):
    code = State()
    desc = State()
    video = State()

class DeleteMovie(StatesGroup):
    code = State()

# ================== /start ==================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    ok = await check_subscriptions(message.from_user.id)
    if not ok:
        await message.answer(
            "❗️Botdan foydalanish uchun quyidagi <b>5 ta</b> kanallarga obuna bo‘ling.\n"
            "So‘ng <b>Tekshirish</b> tugmasini bosing:",
            reply_markup=subscribe_kb()
        )
        return

    if message.from_user.id == ADMIN_ID:
        await message.answer("✅ <b>Admin panel</b>", reply_markup=admin_kb())
    else:
        await message.answer(
            "🎬 <b>Kino bot</b>\n\n"
            "📌 Sizga berilgan <b>kino kodini</b> (raqam) menga yuboring.\n"
            "Masalan: <code>1001</code>\n\n"
            "✅ Kanallarga obuna bo‘lish shart.",
            reply_markup=user_kb()
        )

@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_sub(call: types.CallbackQuery):
    ok = await check_subscriptions(call.from_user.id)
    if not ok:
        await call.answer("Hali obuna to‘liq emas!", show_alert=True)
        return

    await call.answer("✅ Obuna tasdiqlandi!")
    if call.from_user.id == ADMIN_ID:
        await call.message.answer("✅ <b>Admin panel</b>", reply_markup=admin_kb())
    else:
        await call.message.answer(
            "✅ Endi menga <b>kino kodini</b> yuboring.\nMasalan: <code>1001</code>",
            reply_markup=user_kb()
        )

@dp.callback_query_handler(lambda c: c.data == "help")
async def help_cb(call: types.CallbackQuery):
    if call.from_user.id == ADMIN_ID:
        txt = (
            "👑 <b>Admin qo‘llanma</b>\n\n"
            "➕ <b>Kino qo‘shish</b>:\n"
            "1) 'Kino qo‘shish' ni bosing\n"
            "2) Kod yuboring (faqat raqam)\n"
            "3) Tavsif yuboring\n"
            "4) Video yuboring\n\n"
            "🗑 <b>Kino o‘chirish</b>:\n"
            "— Kod yuborasiz, o‘chadi.\n\n"
            "User kino olish uchun botga faqat kod yuboradi."
        )
        await call.message.answer(txt, reply_markup=admin_kb())
    else:
        txt = (
            "ℹ️ <b>Qo‘llanma</b>\n\n"
            "1) Avval kanallarga obuna bo‘lasiz.\n"
            "2) Sizga berilgan kino <b>kodini</b> botga yuborasiz.\n"
            "3) Bot kinoni yuboradi.\n\n"
            "Misol: <code>1001</code>"
        )
        await call.message.answer(txt, reply_markup=user_kb())
    await call.answer()

# ================== ADMIN: KINO QO‘SHISH ==================
@dp.callback_query_handler(lambda c: c.data == "add_movie")
async def add_movie_start(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo‘q!", show_alert=True)
        return
    await call.message.answer("🔢 Kino kodini yuboring (faqat raqam). Masalan: <code>1001</code>")
    await AddMovie.code.set()
    await call.answer()

@dp.message_handler(state=AddMovie.code)
async def add_movie_code(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.finish()
        return

    code = message.text.strip()
    if not code.isdigit():
        await message.answer("❌ Kod faqat raqam bo‘lsin. Masalan: <code>1001</code>")
        return

    if code in db["movies"]:
        await message.answer("⚠️ Bu kod band.\nBoshqa kod yuboring yoki avval o‘chirib qayta qo‘shing.")
        return

    await state.update_data(code=code)
    await message.answer("📝 Kino tavsifini yuboring (ixtiyoriy, lekin tavsiya):")
    await AddMovie.desc.set()

@dp.message_handler(state=AddMovie.desc)
async def add_movie_desc(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.finish()
        return

    desc = message.text.strip()
    await state.update_data(desc=desc)
    await message.answer("📹 Endi kinoni <b>video</b> qilib yuboring:")
    await AddMovie.video.set()

@dp.message_handler(content_types=types.ContentType.VIDEO, state=AddMovie.video)
async def add_movie_video(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.finish()
        return

    data = await state.get_data()
    code = data["code"]
    desc = data.get("desc", "")

    file_id = message.video.file_id

    db["movies"][code] = {
        "desc": desc,
        "file_id": file_id,
        "added_at": datetime.utcnow().isoformat()
    }
    save_db(db)

    await message.answer(f"✅ Kino saqlandi!\nKod: <b>{code}</b>", reply_markup=admin_kb())
    await state.finish()

@dp.message_handler(state=AddMovie.video)
async def add_movie_video_wrong(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.finish()
        return
    await message.answer("❌ Iltimos, aynan <b>video</b> yuboring.")

# ================== ADMIN: RO‘YXAT ==================
@dp.callback_query_handler(lambda c: c.data == "list_movies")
async def list_movies(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo‘q!", show_alert=True)
        return

    if not db["movies"]:
        await call.message.answer("Hali kino yo‘q.", reply_markup=admin_kb())
        await call.answer()
        return

    codes = sorted(db["movies"].keys(), key=lambda x: int(x) if x.isdigit() else x)
    text = "<b>🎬 Kinolar kodlari:</b>\n\n"
    for code in codes[-200:]:
        text += f"• <code>{code}</code>\n"
    text += "\n(So‘nggi 200 ta ko‘rsatildi)"
    await call.message.answer(text, reply_markup=admin_kb())
    await call.answer()

# ================== ADMIN: O‘CHIRISH ==================
@dp.callback_query_handler(lambda c: c.data == "delete_movie")
async def delete_movie_start(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo‘q!", show_alert=True)
        return
    await call.message.answer("🗑 O‘chirmoqchi bo‘lgan kino kodini yuboring:")
    await DeleteMovie.code.set()
    await call.answer()

@dp.message_handler(state=DeleteMovie.code)
async def delete_movie_process(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.finish()
        return

    code = message.text.strip()
    if code in db["movies"]:
        del db["movies"][code]
        save_db(db)
        await message.answer(f"✅ O‘chirildi: <code>{code}</code>", reply_markup=admin_kb())
    else:
        await message.answer("❌ Bunday kod topilmadi.", reply_markup=admin_kb())
    await state.finish()

# ================== USER: KOD YUBORSA KINO BERISH ==================
@dp.message_handler()
async def user_send_code(message: types.Message):
    # Admin oddiy xabar yuborsa ham user handlerga tushmasligi uchun:
    if message.from_user.id == ADMIN_ID:
        return

    ok = await check_subscriptions(message.from_user.id)
    if not ok:
        await message.answer("❗️Avval kanallarga obuna bo‘ling.", reply_markup=subscribe_kb())
        return

    txt = (message.text or "").strip()

    if not txt.isdigit():
        await message.answer("📌 Kino olish uchun menga faqat <b>kod</b> yuboring.\nMasalan: <code>1001</code>")
        return

    movie = db["movies"].get(txt)
    if not movie:
        await message.answer("❌ Bunday kodli kino topilmadi.")
        return

    caption = f"🎬 Kino kodi: <b>{txt}</b>\n\n{movie.get('desc','')}".strip()
    await bot.send_video(chat_id=message.from_user.id, video=movie["file_id"], caption=caption)

# ================== RUN ==================
if __name__ == "__main__":
    if API_TOKEN == "PASTE_YOUR_NEW_TOKEN_HERE":
        print("DIQQAT: API_TOKEN qo‘yilmagan. BotFather’dan yangi token olib, API_TOKEN ga qo‘ying.")
    print("Bot ishga tushdi...")
    executor.start_polling(dp, skip_updates=True)