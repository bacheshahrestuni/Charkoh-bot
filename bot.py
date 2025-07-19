from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters, ContextTypes

# اطلاعات را مستقیماً وارد کن:
TOKEN = "8004942127:AAEICmtuWkR4qd_lZrTyjPncNT37VoqsyWQ"  # توکن ربات
ADMIN_ID = 123456789  # آیدی عددی ادمین (جایگزین کن)
CHANNEL_ID = "@krGLcOkeqE44MTVk"  # کانال آرشیو
GROUP_TOPIC = -1002231302387  # آیدی گروه یا تاپیک اطلاع رسانی

# مراحل گفتگو
CHOOSING_TYPE, CHECK_FINAL, ASK_MUSIC_FILE, ASK_COVER_FILE, ASK_INFO, ASK_ALBUM_INFO = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("تک ترک", callback_data="single"),
        InlineKeyboardButton("فری‌استایل", callback_data="freestyle"),
        InlineKeyboardButton("آلبوم", callback_data="album")
    ]]
    await update.message.reply_text("📌 نوع پروژه را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING_TYPE

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data['type'] = choice

    if choice == "single":
        await query.message.reply_text("✅ آیا نسخه فاینال موزیک آماده است؟ (بله/خیر)")
        return CHECK_FINAL
    elif choice == "freestyle":
        await query.message.reply_text("🎤 لطفا فایل فری‌استایل را ارسال کنید:")
        return ASK_MUSIC_FILE
    elif choice == "album":
        await query.message.reply_text("📀 تعداد ترک‌های آلبوم را وارد کنید:")
        return ASK_ALBUM_INFO

async def check_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    answers = context.user_data.get('final_answers', [])
    answers.append(text)
    context.user_data['final_answers'] = answers

    if len(answers) == 1:
        await update.message.reply_text("✅ آیا نسخه فاینال کاور آرت ترک آماده است؟")
    elif len(answers) == 2:
        await update.message.reply_text("✅ آیا تمام مراحل مارکتینگ و ساخت بررسی شده‌اند؟")
    else:
        if all(a.lower() == 'بله' for a in answers):
            await update.message.reply_text("📥 لطفا فایل موزیک نهایی را ارسال کنید:")
            return ASK_MUSIC_FILE
        else:
            await update.message.reply_text("❌ چون پاسخ‌ها کامل نبود، ثبت انجام نشد.")
            return ConversationHandler.END
    return CHECK_FINAL

async def get_music_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.audio or update.message.document:
        file_id = update.message.audio.file_id if update.message.audio else update.message.document.file_id
        context.user_data['music_file'] = file_id
        if context.user_data.get('type') == 'freestyle':
            await update.message.reply_text("📝 اسم آرتیست را بفرست:")
            return ASK_INFO
        await update.message.reply_text("📥 لطفا فایل کاور آرت موزیک را ارسال کنید:")
        return ASK_COVER_FILE
    else:
        await update.message.reply_text("⚠️ لطفا یک فایل موزیک بفرستید.")
        return ASK_MUSIC_FILE

async def get_cover_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo or update.message.document:
        file_id = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
        context.user_data['cover_file'] = file_id
        await update.message.reply_text("🎵 اسم ترک را بفرست:")
        return ASK_INFO
    else:
        await update.message.reply_text("⚠️ لطفا کاور را بفرست.")
        return ASK_COVER_FILE

async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'track_name' not in context.user_data:
        context.user_data['track_name'] = update.message.text
        if context.user_data.get('type') == 'freestyle':
            await update.message.reply_text("📅 تاریخ پخش را بفرست:")
        else:
            await update.message.reply_text("🎼 نام آهنگساز را بفرست:")
        return ASK_INFO
    elif 'composer' not in context.user_data and context.user_data.get('type') != 'freestyle':
        context.user_data['composer'] = update.message.text
        await update.message.reply_text("🎚️ نام میکس و مستر را بفرست:")
        return ASK_INFO
    elif 'mixmaster' not in context.user_data and context.user_data.get('type') != 'freestyle':
        context.user_data['mixmaster'] = update.message.text
        await update.message.reply_text("🎨 نام کاور آرت را بفرست:")
        return ASK_INFO
    elif 'cover_name' not in context.user_data and context.user_data.get('type') != 'freestyle':
        context.user_data['cover_name'] = update.message.text
        await update.message.reply_text("🧑‍🎤 اسم آرتیست را بفرست:")
        return ASK_INFO
    elif 'artist' not in context.user_data:
        context.user_data['artist'] = update.message.text
        await update.message.reply_text("📅 تاریخ پخش را بفرست:")
        return ASK_INFO
    else:
        context.user_data['release_date'] = update.message.text
        await update.message.reply_text("✅ موزیک شما با موفقیت ثبت شد!")
        await context.bot.send_message(chat_id=CHANNEL_ID, text=f"آرتیست: {context.user_data.get('artist')}\nترک: {context.user_data.get('track_name')}\nتاریخ پخش: {context.user_data.get('release_date')}")
        if context.user_data.get('music_file'):
            await context.bot.send_audio(chat_id=CHANNEL_ID, audio=context.user_data['music_file'])
        if context.user_data.get('cover_file'):
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=context.user_data['cover_file'])
        await context.bot.send_message(chat_id=GROUP_TOPIC, text=f"📢 برنامه پخش جدید:\n🎤 {context.user_data.get('artist')} - {context.user_data.get('track_name')}\n📅 {context.user_data.get('release_date')}")
        return ConversationHandler.END

async def get_album_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'album_tracks' not in context.user_data:
        context.user_data['album_tracks'] = update.message.text
        await update.message.reply_text("📀 اسم آلبوم را بفرست:")
        return ASK_ALBUM_INFO
    elif 'album_name' not in context.user_data:
        context.user_data['album_name'] = update.message.text
        await update.message.reply_text("🧑‍🎤 اسم آرتیست را بفرست:")
        return ASK_ALBUM_INFO
    elif 'album_artist' not in context.user_data:
        context.user_data['album_artist'] = update.message.text
        await update.message.reply_text("🎼 نام آهنگساز یا آهنگسازها را بفرست:")
        return ASK_ALBUM_INFO
    elif 'album_composer' not in context.user_data:
        context.user_data['album_composer'] = update.message.text
        await update.message.reply_text("🎚️ نام میکس‌من یا میکس‌من‌ها را بفرست:")
        return ASK_ALBUM_INFO
    elif 'album_mix' not in context.user_data:
        context.user_data['album_mix'] = update.message.text
        await update.message.reply_text("🎨 لطفا فایل آرت‌ورک را بفرست:")
        return ASK_ALBUM_INFO
    elif 'album_artwork' not in context.user_data:
        if update.message.photo or update.message.document:
            file_id = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
            context.user_data['album_artwork'] = file_id
            await update.message.reply_text("📅 تاریخ پخش آلبوم را بفرست:")
            return ASK_ALBUM_INFO
        else:
            await update.message.reply_text("⚠️ لطفا فایل آرت‌ورک را بفرست:")
            return ASK_ALBUM_INFO
    else:
        context.user_data['album_date'] = update.message.text
        await update.message.reply_text("✅ آلبوم با موفقیت ثبت شد!")
        await context.bot.send_message(chat_id=CHANNEL_ID, text=f"📀 آلبوم جدید:\n🎶 {context.user_data.get('album_name')}\n🎤 {context.user_data.get('album_artist')}\n📅 {context.user_data.get('album_date')}")
        if context.user_data.get('album_artwork'):
            await context.bot.send_photo(chat_id=CHANNEL_ID, photo=context.user_data['album_artwork'])
        await context.bot.send_message(chat_id=GROUP_TOPIC, text=f"📢 برنامه پخش آلبوم:\n🎶 {context.user_data.get('album_name')}\n📅 {context.user_data.get('album_date')}")
        return ConversationHandler.END

async def adminmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ فقط ادمین می‌تواند از این دستور استفاده کند.")
        return
    await update.message.reply_text("🔑 لطفا رمز 4 رقمی را وارد کن:")
    return 100

async def check_admin_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.strip() == "1234":
        context.user_data['admin_auth'] = True
        await update.message.reply_text("✏️ پیام را بفرست تا در گروه ارسال شود:")
        return 101
    else:
        await update.message.reply_text("❌ رمز اشتباه است.")
        return ConversationHandler.END

async def send_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('admin_auth'):
        await context.bot.send_message(chat_id=GROUP_TOPIC, text=update.message.text)
        await update.message.reply_text("✅ پیام ارسال شد.")
    return ConversationHandler.END

app = ApplicationBuilder().token(TOKEN).build()
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOOSING_TYPE: [CallbackQueryHandler(choose_type)],
        CHECK_FINAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_final)],
        ASK_MUSIC_FILE: [MessageHandler(filters.ALL, get_music_file)],
        ASK_COVER_FILE: [MessageHandler(filters.ALL, get_cover_file)],
        ASK_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_info)],
        ASK_ALBUM_INFO: [MessageHandler(filters.ALL, get_album_info)],
        100: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_admin_password)],
        101: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_admin_message)],
    },
    fallbacks=[]
)

app.add_handler(conv_handler)
app.add_handler(CommandHandler('adminmsg', adminmsg))

print("ربات در حال اجراست...")
app.run_polling()