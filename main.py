import os
import glob
import logging
import instaloader
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8605349177:AAH_V7xgvpAPueLDDWW8bZUoxPWXxiiTC98"

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=True,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    request_timeout=30.0
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Салом! Силсила (ссылка)-и Instagram Reels-ро ба ман фиристед!")

async def download_reels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_url = update.message.text.strip()

    if "instagram.com" not in raw_url:
        await update.message.reply_text("Лутфан, танҳо ссылкаи дурусти Instagram-ро фиристед!")
        return

    msg = await update.message.reply_text("Интизор шавед, видео боргирӣ шуда истодааст... ⏳")

    try:
        clean_url = raw_url.split("?")[0].rstrip('/')
        shortcode = clean_url.split("/")[-1]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target="downloads")
    except Exception as e:
        print(f"Огоҳӣ ҳангоми боргирӣ: {e}")

    mp4_files = glob.glob("downloads/*.mp4")

    if mp4_files:
        try:
            video_file = mp4_files[0]
            
            # Аввал паёми вақтиро пок мекунем
            try:
                await msg.delete()
            except:
                pass

            # Танҳо видеоро мефиристем
            await update.message.reply_video(
                video=open(video_file, 'rb'),
                caption="Ана видеои шумо! 🎬"
            )
        except Exception as send_error:
            print(f"Send Error: {send_error}")

        # Пок кардани файлҳои вақтӣ
        for f in glob.glob("downloads/*"):
            try:
                os.remove(f)
            except:
                pass
        if os.path.exists("downloads"):
            try:
                os.rmdir("downloads")
            except:
                pass
    else:
        await msg.edit_text("Хатогӣ: Видео боргирӣ нашуд.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_reels))

    print("Бот ба кор даромад...")
    app.run_polling()
