import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import datetime

(
    ASK_TYPE,
    ALBUM_TRACK_COUNT,
    ALBUM_NAME,
    ALBUM_ARTIST,
    ALBUM_COMPOSER,
    ALBUM_MIX,
    ALBUM_ARTWORK,
    ALBUM_DATE,
    CHECK_FINAL,
    CHECK_COVER,
    CHECK_MARKETING,
    GET_MUSIC_FILE,
    GET_COVER_FILE,
    GET_TRACK_INFO,
    GET_ARTIST_NAME,
    GET_RELEASE_DATE,
    ADMIN_PASSWORD,
    ADMIN_MESSAGE
) = range(18)

tracks = []
current_data = {}

CHANNEL_ID = "@+krGLcOkeqE44MTVk"
GROUP_TOPIC = -1002231302387
ADMIN_ID = 6356825707
ADMIN_CODE = "1313"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! قصد پخش آلبوم / تک ترک / فری‌استایل دارید؟ لطفا یکی را تایپ کنید.")
    return ASK_TYPE

async def ask_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    t = update.message.text.strip()
    current_data[update.effective_user.id] = { 'release_type': t }
    if t == "تک ترک":
        await update.message.reply_text("آیا نسخه فاینال موزیک آماده است؟ (بله/خیر)")
        return CHECK_FINAL
    elif t == "فری‌استایل":
        await update.message.reply_text("لطفا فایل فری‌استایل خود را ارسال کنید.")
        return GET_MUSIC_FILE
    elif t == "آلبوم":
        await update.message.reply_text("تعداد ترک‌های آلبوم را وارد کنید:")
        return ALBUM_TRACK_COUNT
    else:
        await update.message.reply_text("گزینه وارد شده نامعتبر است. لطفا یکی از موارد زیر را تایپ کنید: آلبوم / تک ترک / فری‌استایل")
        return ASK_TYPE

async def check_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == "بله":
        await update.message.reply_text("آیا نسخه فاینال کاور آرت ترک آماده است؟ (بله/خیر)")
        return CHECK_COVER
    else:
        await update.message.reply_text("لطفا بعد از آماده شدن نسخه فاینال موزیک دوباره تلاش کنید.")
        return ConversationHandler.END

async def check_cover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == "بله":
        await update.message.reply_text("آیا تمام مراحل ساخت و مارکتینگ را بررسی کرده‌اید؟ (بله/خیر)")
        return CHECK_MARKETING
    else:
        await update.message.reply_text("لطفا بعد از آماده شدن کاور آرت دوباره تلاش کنید.")
        return ConversationHandler.END

async def check_marketing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == "بله":
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
        if current_data[user_id]['release_type'] == "فری‌استایل":
            await update.message.reply_text("اسم آرتیست را وارد کنید:")
            return GET_ARTIST_NAME
        else:
            await update.message.reply_text("لطفا فایل کاور آرت موزیک خود را ارسال کنید.")
            return GET_COVER_FILE
    else:
        await update.message.reply_text("لطفا یک فایل موزیک ارسال کنید.")
        return GET_MUSIC_FILE

async def get_cover_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        user_id = update.effective_user.id
        current_data[user_id]['cover_file_id'] = update.message.photo[-1].file_id
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
        await update.message.reply_text("✅ موزیک شما با موفقیت ثبت شد!")
        await context.bot.send_audio(chat_id=CHANNEL_ID,audio=current_data[user_id]['music_file_id'],caption=f"🎵 {current_data[user_id].get('track_name','فری‌استایل')} - {current_data[user_id]['artist_name']} ({current_data[user_id]['release_type']})")
        await context.bot.send_message(chat_id=GROUP_TOPIC,text=f"✅ {current_data[user_id]['release_type']} توسط {current_data[user_id]['artist_name']} برای تاریخ {current_data[user_id]['release_date']} ثبت شد!")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("فرمت تاریخ اشتباه است. لطفا دوباره وارد کنید (YYYY-MM-DD)")
        return GET_RELEASE_DATE

# آلبوم
async def album_track_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_data[user_id]['album_track_count'] = update.message.text.strip()
    await update.message.reply_text("اسم آلبوم را وارد کنید:")
    return ALBUM_NAME

async def album_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_data[user_id]['album_name'] = update.message.text.strip()
    await update.message.reply_text("اسم آرتیست را وارد کنید:")
    return ALBUM_ARTIST

async def album_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_data[user_id]['album_artist'] = update.message.text.strip()
    await update.message.reply_text("نام آهنگساز یا آهنگسازها را وارد کنید:")
    return ALBUM_COMPOSER

async def album_composer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_data[user_id]['album_composer'] = update.message.text.strip()
    await update.message.reply_text("نام میکس من یا میکس من‌ها را وارد کنید:")
    return ALBUM_MIX

async def album_mix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current_data[user_id]['album_mix'] = update.message.text.strip()
    await update.message.reply_text("لطفا فایل آرت‌ورک آلبوم را ارسال کنید:")
    return ALBUM_ARTWORK

async def album_artwork(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        user_id = update.effective_user.id
        current_data[user_id]['album_artwork'] = update.message.photo[-1].file_id
        await update.message.reply_text("تاریخ دقیق پخش آلبوم را وارد کنید (مثال: 2025-08-01):")
        return ALBUM_DATE
    else:
        await update.message.reply_text("لطفا یک تصویر برای آلبوم ارسال کنید.")
        return ALBUM_ARTWORK

async def album_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        date_obj = datetime.datetime.strptime(update.message.text.strip(), "%Y-%m-%d").date()
        current_data[user_id]['album_date'] = date_obj
        await update.message.reply_text("✅ آلبوم شما با موفقیت ثبت شد!")
        await context.bot.send_photo(chat_id=CHANNEL_ID, photo=current_data[user_id]['album_artwork'], caption=f"آلبوم {current_data[user_id]['album_name']} توسط {current_data[user_id]['album_artist']} ({current_data[user_id]['album_track_count']} ترک) برای تاریخ {date_obj}")
        await context.bot.send_message(chat_id=GROUP_TOPIC, text=f"✅ آلبوم {current_data[user_id]['album_name']} توسط {current_data[user_id]['album_artist']} برای تاریخ {date_obj} ثبت شد!")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("فرمت تاریخ اشتباه است. لطفا دوباره وارد کنید.")
        return ALBUM_DATE

# پیام ادمین
async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ فقط ادمین می‌تواند از این دستور استفاده کند.")
        return ConversationHandler.END
    await update.message.reply_text("لطفا رمز 4 رقمی را وارد کنید:")
    return ADMIN_PASSWORD

async def admin_check_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == ADMIN_CODE:
        await update.message.reply_text("✅ رمز درست است. پیام خود را وارد کنید:")
        return ADMIN_MESSAGE
    else:
        await update.message.reply_text("❌ رمز اشتباه است.")
        return ConversationHandler.END

async def admin_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await context.bot.send_message(chat_id=GROUP_TOPIC, text=f"📢 پیام ادمین: {msg}")
    await update.message.reply_text("✅ پیام شما به گروه ارسال شد.")
    return ConversationHandler.END

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token("8004942127:AAEICmtuWkR4qd_lZrTyjPncNT37VoqsyWQ").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_TYPE:[MessageHandler(filters.TEXT & ~filters.COMMAND, ask_type)],
            CHECK_FINAL:[MessageHandler(filters.TEXT & ~filters.COMMAND, check_final)],
            CHECK_COVER:[MessageHandler(filters.TEXT & ~filters.COMMAND, check_cover)],
            CHECK_MARKETING:[MessageHandler(filters.TEXT & ~filters.COMMAND, check_marketing)],
            GET_MUSIC_FILE:[MessageHandler(filters.AUDIO | filters.Document.ALL, get_music_file)],
            GET_COVER_FILE:[MessageHandler(filters.PHOTO, get_cover_file)],
            GET_TRACK_INFO:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_track_info)],
            GET_ARTIST_NAME:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_artist_name)],
            GET_RELEASE_DATE:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_release_date)],
            ALBUM_TRACK_COUNT:[MessageHandler(filters.TEXT & ~filters.COMMAND, album_track_count)],
            ALBUM_NAME:[MessageHandler(filters.TEXT & ~filters.COMMAND, album_name)],
            ALBUM_ARTIST:[MessageHandler(filters.TEXT & ~filters.COMMAND, album_artist)],
            ALBUM_COMPOSER:[MessageHandler(filters.TEXT & ~filters.COMMAND, album_composer)],
            ALBUM_MIX:[MessageHandler(filters.TEXT & ~filters.COMMAND, album_mix)],
            ALBUM_ARTWORK:[MessageHandler(filters.PHOTO, album_artwork)],
            ALBUM_DATE:[MessageHandler(filters.TEXT & ~filters.COMMAND, album_date)]
        },
        fallbacks=[]
    )

    admin_handler = ConversationHandler(
        entry_points=[CommandHandler('adminmsg', admin_broadcast)],
        states={
            ADMIN_PASSWORD:[MessageHandler(filters.TEXT & ~filters.COMMAND, admin_check_password)],
            ADMIN_MESSAGE:[MessageHandler(filters.TEXT & ~filters.COMMAND, admin_send_message)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(admin_handler)
    app.run_polling()
