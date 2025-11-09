import os
import telebot
import yt_dlp
import re
import subprocess
import sys
from flask import Flask, request
import threading

TOKEN = "7767505553:AAE-doqqnURz2ySunKO5zgKMpwCwya92i70"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)
bot_running = False
bot_thread = None

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
        print("Получена команда остановки от администратора")
        bot_running = False
        bot.stop_polling()
    else:
        bot.reply_to(message, "❌ У вас нет прав для остановки бота")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
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
    global bot_running
    bot_running = True
    print("🚀 Бот запущен в облаке!")
    bot.infinity_polling()

@app.route('/')
def home():
    return "🎵 YouTube to MP3 Bot is running on Cloud Run!"

@app.route('/start', methods=['POST'])
def start_bot():
    global bot_thread, bot_running
    if not bot_running:
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.start()
        return "✅ Бот запущен!"
    return "⚠️ Бот уже запущен"

@app.route('/stop', methods=['POST'])
def stop_bot_http():
    global bot_running
    bot_running = False
    bot.stop_polling()
    return "🛑 Бот остановлен"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
