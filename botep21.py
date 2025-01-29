import os
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)

TOKEN = "8141554325:AAEHm1Q0HvQ3O5lbyaxp0DD0R93pSYhemQ8" 
WEBHOOK_URL = "https://ep123456789.onrender.com/webhook"  

app = FastAPI()
telegram_app = ApplicationBuilder().token(TOKEN).build()

LANGUAGES = {"de": "Deutsch", "en": "English", "ru": "Русский"}
user_data = {}

@app.on_event("startup")
async def on_startup():
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    print("")

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)


async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Русский", callback_data="lang_ru")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Пожалуйста, выберите язык:", reply_markup=reply_markup)


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

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(language_selection, pattern="^lang_.*"))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
