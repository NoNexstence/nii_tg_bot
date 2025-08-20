import os

from telegram import InputFile
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler, CommandHandler,
                          MessageHandler, filters, ConversationHandler, ContextTypes)

from sql import load_data
from document import create_doc


BOT_TOKEN = '8252550919:AAEiIn_d8JiAcfS_478erwoBjnkVorBWnyg'
YEAR, REGION, TYPE = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **Добрый день!**\n\n"
        "Я тестовый бот для генерации необходимых справок\n",

        parse_mode="Markdown"
    )

    keyboard = [["🔍 Поиск"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        "Нажми кнопку ниже, чтобы начать поиск:",
        reply_markup=reply_markup
    )

    return ConversationHandler.END


# ====================/ НАЧАТЬ ПОИСК /==================== #
async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔍 Поиск":
        keyboard = [
            [InlineKeyboardButton("2020", callback_data="year_2020")],
            [InlineKeyboardButton("2021", callback_data="year_2021")],
            [InlineKeyboardButton("2022", callback_data="year_2022")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🔍 **Начинаем поиск!**\n\n"
            "Выберите год:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return YEAR
    return ConversationHandler.END


# ====================/ ЖДЕМ КОЛБЭК С ГОДОМ /==================== #
async def handle_year_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("year_"):
        year = query.data[len("year_"):]
        context.user_data['year'] = year

        keyboard = [
            [InlineKeyboardButton("2290", callback_data="region_2290")],
            [InlineKeyboardButton("2336", callback_data="region_2336")],
            [InlineKeyboardButton("8150", callback_data="region_8150")],
            [InlineKeyboardButton("8250", callback_data="region_8250")],
            [InlineKeyboardButton("8950", callback_data="region_8950")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(
            f"Выбранный год: {year}\n\n"
            "Теперь выберете регион:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

        return REGION
    return YEAR


# ====================/ ЖДЕМ КОЛБЭК С РЕГИОНОМ /==================== #
async def handle_region_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("region_"):
        region = query.data[len("region_"):]
        context.user_data['region'] = region
        year = context.user_data.get("year")

        keyboard = [
            [InlineKeyboardButton("Поликлиники", callback_data="type_mo_Поликлиники")],
            [InlineKeyboardButton("Детские поликлиники", callback_data="type_mo_Детские поликлиники")],
            [InlineKeyboardButton("Амбулатории", callback_data="type_mo_Амбулатории")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(
            f"Выбранный год: {year}\n"
            f"Выбранный регион: {region}\n\n"
            "Теперь выберете тип МО:",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

        return TYPE
    return REGION


# ====================/ ЖДЕМ КОЛБЭК С ТИПОМ МО /==================== #
async def handle_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("type_mo_"):
        type_mo = query.data[len("type_mo_"):]
        context.user_data['type_mo'] = type_mo
        year = context.user_data.get("year")
        region = context.user_data.get("region")



        await query.message.edit_text(
            f"Выбранный год: {year}\n"
            f"Выбранный регион: {region}\n"
            f"Выбранный тип МО: {type_mo}\n\n"
            "Загружаю данные, ожидайте ...",
            parse_mode="Markdown",
        )
        data = load_data(year, region, type_mo)
        create_doc(data)

        file_path = "files/final_result.docx"

        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=InputFile(file, filename=f"отчет_{year}_{region}.docx"),
                    caption="✅ Справка готова!"
                )


        else:
            await query.message.reply_text("❌ Ошибка: файл не найден")

        return ConversationHandler.END
    return TYPE



def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("🔍 Поиск"), start_search)],
        states={
            YEAR: [CallbackQueryHandler(handle_year_selection, pattern="^year_")],
            REGION: [CallbackQueryHandler(handle_region_selection, pattern="^region_")],
            TYPE: [CallbackQueryHandler(handle_type_selection, pattern="^type_")]
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(filters.Text("🔍 Поиск"), start_search)
        ]
    )

    app.add_handler(conv_handler)

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()