import os
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = "8613512274:AAFYNi9cYodA_6AqNLUbydeDSnFE-0TA6Uk"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Салом! Маро ба чатҳо илова кунед ё пайванди (ссылка) видеоро аз Instagram, TikTok ё YouTube фиристед.\n\n"
        "Ман овози онро ба паёми овозӣ (Voice Message) табдил медиҳам!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not (url.startswith("http://") or url.startswith("https://")):
        await update.message.reply_text("Лутфан пайванди дуруст фиристед (Instagram, TikTok ё YouTube)!")
        return

    msg = await update.message.reply_text("⏳ Видео коркард шуда истодааст, овозро ҷудо мекунам...")

    output_audio = "voice.ogg"
    temp_audio = "downloaded_audio"

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
        }],
        'outtmpl': f'{temp_audio}.%(ext)s',
        'quiet': True,
    }

    try:
        # Скачивание аудио с видео
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        input_file = f"{temp_audio}.opus"

        # Конвертация в формат голосового сообщения Telegram (.ogg/Opus)
        subprocess.run([
            'ffmpeg', '-i', input_file,
            '-c:a', 'libopus', '-b:a', '32k', '-vbr', 'on',
            '-compression_level', '10', output_audio, '-y'
        ], check=True)

        # Создание инлайн-кнопок
        keyboard = [
            [
                InlineKeyboardButton("🟢 Фиристодан ба WhatsApp", switch_inline_query=""),
                InlineKeyboardButton("🔵 Поделиться", switch_inline_query="")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправка аудио как Voice Message
        with open(output_audio, 'rb') as voice:
            await update.message.reply_voice(
                voice=voice,
                caption="🎙 Овози видео табдил дода шуд!\n\nБарои ба WhatsApp фиристодан тугмаи поёниро пахш карда, файлро равон кунед.",
                reply_markup=reply_markup
            )

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"Мушкилӣ пеш омад: {str(e)}")

    finally:
        # Удаление временных файлов
        for file in [f"{temp_audio}.opus", output_audio]:
            if os.path.exists(file):
                os.remove(file)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
