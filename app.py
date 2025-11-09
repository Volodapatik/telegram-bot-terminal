from flask import Flask
import os
import threading
import telebot
import yt_dlp
import re
import subprocess

TOKEN = "7767505553:AAE-doqqnURz2ySunKO5zgKMpwCwya92i70"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
bot_running = True

def extract_url(text):
    match = re.search(r'youtu\.be/([^\s&]+)|youtube\.com/watch\?v=([^\s&]+)', text)
    return f"https://youtu.be/{match.group(1) or match.group(2)}" if match else None

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎵 Бот запущен в облаке! Отправь ссылку YouTube")

@bot.message_handler(commands=['stop'])
def stop_bot(message):
    global bot_running
    if message.from_user.id == 1637885523:
        bot.reply_to(message, "🛑 Останавливаю бота...")
        bot_running = False
        bot.stop_polling()
    else:
        bot.reply_to(message, "❌ У вас нет прав для остановки бота")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    global bot_running
    if not bot_running:
        return
        
    url = extract_url(message.text)
    if not url:
        bot.reply_to(message, "❌ Неверная ссылка")
        return
    
    try:
        chat_id = message.chat.id
        bot.send_message(chat_id, f"🎵 Обрабатываю: {url}")
        
        ydl_opts = {
            'format': 'worst[height<=360]',
            'outtmpl': 'video.%(ext)s',
        }
        
        bot.send_message(chat_id, "⬇️ Скачиваю видео...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        video_file = None
        for file in os.listdir('.'):
            if file.startswith('video.'):
                video_file = file
                break
        
        if not video_file:
            bot.reply_to(message, "❌ Не удалось скачать видео")
            return
        
        bot.send_message(chat_id, "🎵 Конвертирую в MP3...")
        
        mp3_file = 'audio.mp3'
        try:
            subprocess.run([
                'ffmpeg', '-i', video_file, 
                '-vn', '-acodec', 'libmp3lame', '-ab', '192k',
                '-y', mp3_file
            ], check=True, capture_output=True)
            
            if os.path.exists(mp3_file):
                file_size = os.path.getsize(mp3_file) / (1024 * 1024)
                bot.send_message(chat_id, f"📤 Отправляю ({file_size:.1f} МБ)...")
                
                with open(mp3_file, 'rb') as f:
                    bot.send_audio(chat_id, f, timeout=300)
                
                bot.send_message(chat_id, "✅ Готово!")
                
                os.remove(video_file)
                os.remove(mp3_file)
            else:
                bot.reply_to(message, "❌ Не удалось конвертировать в MP3")
                
        except subprocess.CalledProcessError as e:
            bot.reply_to(message, f"❌ Ошибка конвертации: {e}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

def run_bot():
    print("🚀 Запускаю Telegram бота...")
    bot.infinity_polling()

@app.route('/')
def home():
    return "🎵 YouTube to MP3 Bot - Cloud Run Ready! Bot is RUNNING!"

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    # Запускаємо бота в окремому потоці
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаємо Flask сервер
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
