import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Салом! Ба ман ссылкаи видеоро аз Instagram, TikTok ё YouTube фиристед. "
        "Ман аудиои онро ба шумо ҳамчун файл мефиристам, то тавонед ба WhatsApp, Imo ва дигар чатҳо роҳ диҳед!"
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("Лутфан ссылкаи дуруст (соз)-ро фиристед!")
        return

    msg = await update.message.reply_text("⏳ Видео коркард шуда истодааст, чанд сония сабр кунед...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio_file.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: download_audio(url, ydl_opts))
        
        audio_filename = None
        for file in os.listdir('.'):
            if file.startswith("audio_file."):
                audio_filename = file
                break

        if audio_filename and os.path.exists(audio_filename):
            with open(audio_filename, 'rb') as audio:
                await update.message.reply_audio(
                    audio=audio,
                    caption="🎵 Аудио тайёр шуд!\n\n📲 Барои фиристодан ба WhatsApp ё Imo: дар канори файл тугмаи се нуқта ё «Share / Поделиться»-ро пахш карда, WhatsApp ё Imo-ро интихоб кунед."
                )
            os.remove(audio_filename)
            await msg.delete()
        else:
            await msg.edit_text("❌ Аудио ёфт нашуд. Линкро тафтиш кунед.")

    except Exception as e:
        await msg.edit_text("❌ Хатогӣ ҳангоми боргирӣ. Ссылкаро тафтиш кунед ё баъдтар ҳаракат кунед.")

def download_audio(url, opts):
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN ёфт нашуд!")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    print("Бот фаъол шуд...")
    app.run_polling()

if __name__ == "__main__":
    main()
