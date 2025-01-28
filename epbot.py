from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

LANGUAGES = {
    "de": "Deutsch",
    "en": "English",
    "ru": "Русский"
}

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Deutsch", callback_data="lang_de")],
        [InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("Русский", callback_data="lang_ru")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
    )


async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected_lang = query.data.split("_")[1]
    user_id = query.from_user.id

    user_data[user_id] = {"language": selected_lang}

    messages = {
        "de": "Bitte geben Sie den Namen Ihrer Firma und die Nummer Ihrer Spezifikation ein, z. B.: #123456789.",
        "en": "Please enter the name of your company and the specification number, e.g.: #123456789.",
        "ru": "Пожалуйста, введите название Вашей фирмы и через пробел номер вашей спецификации, например: #123456789."
    }

    await query.edit_message_text(messages[selected_lang])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_data or "language" not in user_data[user_id]:
        await update.message.reply_text("Please use /start to begin.")
        return

    user_language = user_data[user_id]["language"]

    error_messages = {
        "de": "Ungültiger Firmenname oder Spezifikationsnummer. Bitte versuchen Sie es erneut.",
        "en": "Incorrect company name or specification number. Please try again.",
        "ru": "Некорректное название фирмы или номера спецификации. Попробуйте еще раз."
    }

    await update.message.reply_text(error_messages[user_language])

if __name__ == "__main__":
    import logging

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

    TOKEN = "8141554325:AAEHm1Q0HvQ3O5lbyaxp0DD0R93pSYhemQ8"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_selection, pattern="^lang_.*"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен!")
    app.run_polling()
