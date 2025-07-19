import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import datetime

# مراحل گفتگو را مشخص می‌کنیم
(
    CHECK_FINAL,
    CHECK_COVER,
    CHECK_MARKETING,
    GET_MUSIC_FILE,
    GET_COVER_FILE,
    GET_TRACK_INFO,
    GET_ARTIST_NAME,
    GET_RELEASE_DATE,
) = range(8)

# اینجا دیتابیس ساده در حافظه تعریف می‌کنیم (برای تست)
tracks = []
current_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفا بفرمایید آیا نسخه فاینال موزیک آماده است؟ (بله/خیر)")
    return CHECK_FINAL

async def check_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "بله":
        current_data[update.effective_user.id] = {}
        await update.message.reply_text("آیا نسخه فاینال کاور آرت ترک آماده است؟ (بله/خیر)")
        return CHECK_COVER
    else:
        await update.message.reply_text("لطفا بعد از آماده شدن نسخه فاینال موزیک دوباره تلاش کنید.")
        return ConversationHandler.END

async def check_cover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "بله":
        await update.message.reply_text("آیا تمام مراحل ساخت و مارکتینگ را بررسی کرده‌اید؟ (بله/خیر)")
        return CHECK_MARKETING
    else:
        await update.message.reply_text("لطفا بعد از آماده شدن کاور آرت دوباره تلاش کنید.")
        return ConversationHandler.END

async def check_marketing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text == "بله":
        await update.message.reply_text("لطفا فایل فاینال موزیک خود را ارسال کنید.")
        return GET_MUSIC_FILE
    else:
        await update.message.reply_text("لطفا بعد از بررسی کامل موارد مارکتینگ دوباره تلاش کنید.")
        return ConversationHandler.END

async def get_music_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.audio or update.message.document
    if file:
        user_id = update.effective_user.id
        current_data[user_id]['music_file_id'] = file.file_id
        await update.message.reply_text("لطفا فایل کاور آرت موزیک خود را ارسال کنید.")
        return GET_COVER_FILE
    else:
        await update.message.reply_text("لطفا یک فایل موزیک ارسال کنید.")
        return GET_MUSIC_FILE

async def get_cover_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo
    if photo:
        user_id = update.effective_user.id
        current_data[user_id]['cover_file_id'] = photo[-1].file_id
        await update.message.reply_text("لطفا اطلاعات ترک را به این صورت ارسال کنید:\n1- اسم ترک\n2- آهنگساز\n3- میکس و مستر\n4- کاور آرت (نام طراح)")
        return GET_TRACK_INFO
    else:
        await update.message.reply_text("لطفا یک تصویر کاور آرت ارسال کنید.")
        return GET_COVER_FILE

async def get_track_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = update.message.text.strip().split('\n')
    if len(info) >= 4:
        user_id = update.effective_user.id
        current_data[user_id]['track_name'] = info[0]
        current_data[user_id]['composer'] = info[1]
        current_data[user_id]['mix_master'] = info[2]
        current_data[user_id]['cover_artist'] = info[3]
        await update.message.reply_text("اسم آرتیست را وارد کنید:")
        return GET_ARTIST_NAME
    else:
        await update.message.reply_text("لطفا اطلاعات را به فرمت درست وارد کنید.")
        return GET_TRACK_INFO

async def get_artist_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_data[user_id]['artist_name'] = update.message.text.strip()
    await update.message.reply_text("تاریخ دقیق پخش موزیک را وارد کنید (مثال: 2025-08-01):")
    return GET_RELEASE_DATE

async def get_release_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    date_str = update.message.text.strip()
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        current_data[user_id]['release_date'] = date_obj
        tracks.append(current_data[user_id])
        await update.message.reply_text("موزیک شما با موفقیت ثبت شد!")
        # اینجا می‌توانید فایل‌ها را به کانال ارسال کنید
        # و همچنین در گروه اطلاع رسانی کنید
        # context.bot.send_message(chat_id=CHANNEL_ID, text="آرشیو موزیک جدید")
        # context.bot.send_message(chat_id=GROUP_ID, text="اطلاع رسانی")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("فرمت تاریخ اشتباه است. لطفا دوباره وارد کنید (YYYY-MM-DD)")
        return GET_RELEASE_DATE

# هندلری که هر هفته شنبه لیست را اعلام می‌کند (می‌توانید با JobQueue انجام دهید)

async def announce_weekly(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today()
    upcoming = [t for t in tracks if t['release_date'] >= today]
    if upcoming:
        msg = "لیست ترک های این هفته:\n"
        for t in sorted(upcoming, key=lambda x: x['release_date']):
            msg += f"🎵 {t['track_name']} توسط {t['artist_name']} تاریخ پخش: {t['release_date']}\n"
        await context.bot.send_message(chat_id=GROUP_ID, text=msg)
    else:
        await context.bot.send_message(chat_id=GROUP_ID, text="هیچ ترکی جهت پخش وجود ندارد. برخی افراد در حال کم‌کاری می‌باشند. بررسی گردد.")

# اینجا باید توکن و سایر جزئیات ربات را وارد کنید
# و ConversationHandler را اضافه کنید.

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token("8004942127:AAEICmtuWkR4qd_lZrTyjPncNT37VoqsyWQ").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHECK_FINAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_final)],
            CHECK_COVER: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_cover)],
            CHECK_MARKETING: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_marketing)],
            GET_MUSIC_FILE: [MessageHandler(filters.AUDIO | filters.Document.ALL, get_music_file)],
            GET_COVER_FILE: [MessageHandler(filters.PHOTO, get_cover_file)],
            GET_TRACK_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_track_info)],
            GET_ARTIST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_artist_name)],
            GET_RELEASE_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_release_date)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)

    app.run_polling()
