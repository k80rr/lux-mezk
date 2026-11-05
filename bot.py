import os
import logging
import asyncio
import tempfile
from pathlib import Path

import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =========================
# إعداد تسجيل الأخطاء
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# التوكن الخاص بك
BOT_TOKEN = "9019117078:AAFYULCx9deKyXSu_CJ7j2Uwm8Us7TxPMaE"


# =========================
# رسالة البداية
# =========================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                "📜 لستة المميزات",
                callback_data="bot_list"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "أهلاً بك في بوت 𝑷𝑳𝑼𝑿 𝑴𝑼𝑺𝑰𝑪 🎶\n\n"
        "للبحث عن أغنية اكتب:\n"
        "🎵 لوكس شغلي [اسم الأغنية]\n\n"
        "أو استخدم الأمر:\n"
        "/play اسم الأغنية"
    )

    await update.effective_message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )


# =========================
# قائمة المميزات
# =========================

async def bot_list_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    list_text = (
        "📋 قائمة مميزات 𝑷𝑳𝑼𝑿 𝑴𝑼𝑺𝑰𝑪:\n\n"
        "1️⃣ البحث الفوري والسريع عن الأغاني[span_0](start_span)[span_0](end_span).\n"
        "2️⃣ دعم روابط يوتيوب[span_1](start_span)[span_1](end_span).\n"
        "3️⃣ إرسال الأغاني بصيغة صوتية قابلة للتشغيل[span_2](start_span)[span_2](end_span).\n"
        "4️⃣ تنظيف الملفات المؤقتة تلقائياً[span_3](start_span)[span_3](end_span).\n"
        "5️⃣ واجهة بسيطة وسريعة[span_4](start_span)[span_4](end_span).\n\n"
        "✨ استمتع بتجربة البوت!"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(list_text)

    else:
        await update.effective_message.reply_text(list_text)


# =========================
# معالجة الأزرار
# =========================

async def button_callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if query.data == "bot_list":
        await bot_list_command(update, context)

    else:
        await query.answer()


# =========================
# محرك التحميل (المحدث لمنع التعليق)
# =========================

def download_music(query: str, folder: str):

    options = {
        "format": "bestaudio/best",
        "default_search": "ytsearch1",
        "outtmpl": str(Path(folder) / "audio.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 8,
        "retries": 1,
        "geo_bypass": True,
        "ignoreerrors": False,
        # هذه الإعدادات تمنع حظر يوتيوب وتجعل البحث صاروخي
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"]
            }
        },
    }

    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(f"ytsearch1:{query}", download=True)

        if not info:
            raise ValueError("لم يتم العثور على نتيجة")

        if "entries" in info:
            entries = info.get("entries")

            if not entries:
                raise ValueError("نتائج البحث فارغة")

            info = entries[0]

        if not info:
            raise ValueError("معلومات الأغنية غير متوفرة")

    audio_path = Path(ydl.prepare_filename(info))

    if not audio_path.exists():
        candidates = [
            path for path in Path(folder).glob("audio.*")
            if path.is_file()
        ]
        if not candidates:
            raise FileNotFoundError("ملف الصوت الناتج غير موجود")
        audio_path = candidates[0]

    return audio_path, info


# =========================
# البحث وإرسال الأغنية
# =========================

async def music_search_and_download(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    message = update.effective_message

    if not message or not message.text:
        return

    text = message.text.strip()
    query = ""

    # أمر /play
    if text.startswith("/play"):

        parts = text.split(maxsplit=1)

        if len(parts) > 1:
            query = parts[1].strip()

    # لوكس شغلي
    elif text.startswith("لوكس شغلي"):

        parts = text.split(maxsplit=2)

        if len(parts) > 2:
            query = parts[2].strip()

    # لوكس شغل
    elif text.startswith("لوكس شغل"):

        parts = text.split(maxsplit=2)

        if len(parts) > 2:
            query = parts[2].strip()

    if not query:
        return

    status_message = await message.reply_text(
        f"🔍 جاري البحث عن: {query}"
    )

    try:

        with tempfile.TemporaryDirectory() as temp_folder:

            audio_path, info = await asyncio.to_thread(
                download_music,
                query,
                temp_folder
            )

            MY_USER = "@K80rr"

            with open(audio_path, "rb") as audio_file:

                # إرسال الصوت مع إظهار يوزرك في تفاصيل الأغنية وفي الوصف[span_5](start_span)[span_5](end_span)
                await message.reply_audio(
                    audio=audio_file,
                    filename="PLUX_MUSIC.m4a",
                    title=info.get("title", query),
                    performer=f"𝑷𝑳𝑼𝑿 | {MY_USER}",
                    caption=f"🎵 **تم التحميل بواسطة:** {MY_USER}",
                    parse_mode="Markdown"
                )

        try:
            await status_message.delete()

        except Exception:
            logger.warning("تعذر حذف رسالة الحالة")

    except Exception as error:

        logger.error(
            "حدث خطأ أثناء التحميل: %s",
            error,
            exc_info=True
        )

        try:
            await status_message.edit_text(
                "❌ فشل تحميل الأغنية.\n"
                "تأكد من اسم الأغنية أو الرابط وحاول مجدداً."
            )

        except Exception:
            pass


# =========================
# تشغيل البوت
# =========================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start_command)
    )

    app.add_handler(
        CommandHandler("list", bot_list_command)
    )

    app.add_handler(
        CommandHandler("play", music_search_and_download)
    )

    app.add_handler(
        CallbackQueryHandler(button_callback_handler)
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            music_search_and_download
        )
    )

    logger.info("PLUX MUSIC BOT IS RUNNING")

    app.run_polling()


if __name__ == "__main__":
    main()
