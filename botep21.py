import os
import logging
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Настраиваем логирование (вывод ошибок в консоль Render)
logging.basicConfig(level=logging.INFO)

# === Устанавливаем переменные окружения ===
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")  # Храним токен в Render
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-app-name.onrender.com/webhook")  # Ссылка для вебхука

app = FastAPI()
telegram_app = ApplicationBuilder().token(TOKEN).build()

LANGUAGES = {"de": "Deutsch", "en": "English", "ru": "Русский"}
user_data = {}

# === Устанавливаем вебхук ===
@app.on_event("startup")
async def on_startup():
    try:
        await telegram_app.initialize()  # Обязательная инициализация!
        await telegram_app.bot.set_webhook(WEBHOOK_URL)
        logging.info(f"✅ Вебхук установлен: {WEBHOOK_URL}")
    except Exception as e:
        logging.error(f"❌ Ошибка установки вебхука: {e}")

# === Обработка вебхука ===
@app.post("/webhook")
async def handle_webhook(request: Request):
    try:
        data = await request.json()
        print(f"📥 Получен вебхук: {data}")  # Логируем входящие данные
        
        update = Update.de_json(data, telegram_app.bot)

        await telegram_app.initialize()  # Обязательная инициализация перед обработкой обновлений
        await telegram_app.process_update(update)

        return {"status": "ok"}
    
    except Exception as e:
        logging.error(f"❌ Ошибка обработки вебхука: {e}")
        return {"status": "error", "message": str(e)}

# === Команда /start ===
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Русский", callback_data="lang_ru")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Пожалуйста, выберите язык:", reply_markup=reply_markup)

# === Обработчик выбора языка ===
async def language_selection(update: Update, context):
    query = update.callback_query
    await query.answer()
    selected_lang = query.data.split("_")[1]
    user_id = query.from_user.id
    user_data[user_id] = {"language": selected_lang}
    
    messages = {
        "de": "Bitte geben Sie den Firmennamen und die Nummer ein, z. B.: #123456789.",
        "en": "Please enter the company name and specification number, e.g.: #123456789.",
        "ru": "Введите название вашей фирмы и номер спецификации, например: #123456789."
    }
    await query.edit_message_text(messages[selected_lang])

# === Обработчик сообщений (если пользователь ввел что-то не так) ===
async def handle_message(update: Update, context):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        await update.message.reply_text("Используйте /start, чтобы начать.")
        return
    
    user_language = user_data[user_id]["language"]
    error_messages = {
        "de": "Ungültiger Firmenname oder Nummer. Versuchen Sie es erneut.",
        "en": "Invalid company name or number. Try again.",
        "ru": "Некорректное название фирмы или номера. Попробуйте ещё раз."
    }
    await update.message.reply_text(error_messages[user_language])

# === Добавляем обработчики команд ===
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(language_selection, pattern="^lang_.*"))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
