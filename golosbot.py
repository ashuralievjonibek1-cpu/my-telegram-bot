import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Токени бехатар аз муҳити Render гирифта мешавад
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Салом! Ба ман пайванди (ссылка) видеоро фиристед, ман онро ба паёми овозӣ (.ogg) табдил медиҳам.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("⚠️ Лутфан пайванди (ссылка) дурусти видеоро фиристед.")
        return

    msg = await update.message.reply_text("⏳ Видео боргирӣ ва ба паёми овозӣ табдил дода мешавад, лутфан сабр кунед...")

    output_filename = f"voice_{update.message.message_id}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'vorbis',
        }],
        'quiet': True,
    }

    def download_audio():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, download_audio)

        ogg_file = f"{output_filename}.ogg"

        if os.path.exists(ogg_file):
            with open(ogg_file, 'rb') as voice:
                await update.message.reply_voice(voice=voice)
            os.remove(ogg_file)
            await msg.delete()
        else:
            await msg.edit_text("❌ Хатогӣ: Файли овозӣ сохта нашуд.")

    except Exception as e:
        logging.error(f"Error: {e}")
        await msg.edit_text("❌ Хатогӣ ҳангоми коркарди видео. Санҷед, ки пайванд дуруст аст ё не.")

if __name__ == '__main__':
    if not TOKEN:
        print("ERROR: BOT_TOKEN пайдо нашуд! Онро дар Render Environment Variables гузоред.")
    else:
        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("Бот ба кор даромад...")
        app.run_polling()
